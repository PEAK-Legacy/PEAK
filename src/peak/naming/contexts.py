"""Base classes for naming contexts"""

from peak.api import *

from interfaces import *
from names import *
from properties import *

import spi

from peak.binding.components import Component, Once, Acquire

from peak.util.imports import importObject


__all__ = [
    'NameContext', 'AddressContext', 'AbstractContext', 'GenericURLContext'
]























class NameContext(Component):

    __implements__ = IBasicContext

    creationName    = Acquire(CREATION_NAME)
    creationParent  = Acquire(CREATION_PARENT)
    objectFactories = Acquire(OBJECT_FACTORIES)
    stateFactories  = Acquire(STATE_FACTORIES)

    schemeParser  = None
    nameClass     = CompositeName
    defaultScheme = None
    
    _acceptStringURLs    = True     # XXX

    namingAuthority = None
    # XXX nameInContext = binding.Once( nameClass([]) or CompoundName([]) )


    def _resolveComposite(self, name, iface):

        # You should override this method if you want dynamic weak NNS
        # support; that is, if you want to mix composite names and compound
        # names and figure out dynamically when you've crossed over into
        # another naming system.  

        if not name:
            # convert to compound (local) empty name
            return self._resolveLocal(CompoundName([]), iface) # XXX .nameClass
        else:
            local = name[0]
            if self.nameClass and self.nameClass.isComposite:
                local = CompoundName(local) # XXX use URL parser syntax?

            if len(name)==1:
                return self.resolveToInterface(local, iface)

            return self.lookup_nns(local).resolveToInterface(name[1:], iface)



    def _checkSupported(self, name, iface):

        if iface.isImplementedBy(self):
            return

        raise exceptions.NotAContext(
            "Unsupported interface", iface,
            resolvedObj=self, remainingName=name
        )
    

    def _resolveLocal(self, name, iface):

        if len(name)<2:
            self._checkSupported(name, iface)
            return self, name
            
        try:
            return self[name[:1]].resolveToInterface(name[1:],iface)

        except exceptions.NotAContext:
            self._checkSupported(name, iface)
            return self, name


    def _resolveURL(self, name, iface):

        #auth, nic = name.getAuthorityAndName()

        #if self.namingAuthority == auth and nic.startswith(self.nameInContext):
        
            self._checkSupported(name, iface)
            return self, name

        #else:
        #    ctx = self.__class__(self, namingAuthority=auth)
        #    return ctx.resolveToInterface(nic, iface)




    def resolveToInterface(self, name, iface=IBasicContext):

        parser = self.schemeParser
        name = toName(name, self.nameClass, self._acceptStringURLs)

        if name.isComposite:        
            return self._resolveComposite(name, iface)

        if name.isURL:

            if parser:
                if isinstance(name,parser):
                    return self._resolveURL(name,iface)
                elif parser.supportsScheme(name.scheme):
                    return self._resolveURL(
                        parser(name.scheme, name.body), iface
                    )

            ctx = spi.getURLContext(name.scheme, self, iface)

            if ctx is None:
                raise exceptions.InvalidName(
                    "Unknown scheme %s in %r" % (name.scheme,name)
                )

            return ctx.resolveToInterface(name,iface)

        return self._resolveLocal(name,iface)













    def lookup_nns(self, name=None):

        """Find the next naming system after resolving local part"""

        if not name:    # empty name means "this context"

            return self._deref(
                NNS_Reference( self ), name, None
            )

        obj = self[name]

        if isinstance(obj,self.__class__):
          
            # Same or subclass, must not be a junction;
            # so delegate the NNS lookup to it
            
            return obj.lookup_nns()


        elif not IBasicContext.isImplementedBy(obj):
            
            # Not a context?  make it an NNS reference

            return self._deref(
                NNS_Reference( obj ), name, None
            )

        else:
            # It's a context, so just return it
            return obj


    def close(self):
        pass






    def _deref(self, state, name, attrs=None):

        if isinstance(state,LinkRef):
            return self[state.linkName]

        for factory in self.objectFactories:

            result = factory.getObjectInstance(state, name, self, attrs)

            if result is not None:
                return result                      

        return state


    def _mkref(self, object, name, attrs):

        if IReferenceable.isImplementedBy(object):
            return (object.getReference(object), attrs)

        for factory in self.stateFactories:

            result = factory.getStateToBind(object, name, self, attrs)

            if result is not None:
                return result

        return object, attrs













    def lookupLink(self, name):

        """Return terminal link for 'name'"""

        ctx, name = self.resolveToInterface(name)
        if ctx is not self: return ctx.lookupLink(name)

        info = self._get(name)
        
        if info is NOT_FOUND:
            raise exceptions.NameNotFound(name)

        state, attrs = info
        if isinstance(state,LinkRef):
            return state

        return self._deref(state, name, attrs)


    def __getitem__(self, name):

        """Lookup 'name' and return an object"""
        
        ctx, name = self.resolveToInterface(name)
        if ctx is not self: return ctx[name]
        
        obj = self._getOb(name)
        if obj is NOT_FOUND:
            raise exceptions.NameNotFound(name)

        return obj










    def get(self, name, default=None):
    
        """Lookup 'name' and return an object, or 'default' if not found"""
        
        ctx, name = self.resolveToInterface(name)
        if ctx is not self: return ctx.get(name,default)

        return self._getOb(name, default)


    def _getOb(self, name, default=NOT_FOUND):

        info = self._get(name)
        if info is NOT_FOUND: return default

        state, attrs = info

        return self._deref(state, name, attrs)


    def __contains__(self, name):
        """Return a true value if 'name' has a binding in context"""

        ctx, name = self.resolveToInterface(name)
        
        if ctx is not self:
            return name in ctx

        return self._get(name, retrieve=False) is not NOT_FOUND


    def lookup(self, name):
        """Lookup 'name' --> object; synonym for __getitem__"""
        return self[name]

    def has_key(self, name):
        """Synonym for __contains__"""
        return name in self



    def keys(self):
        """Return a sequence of the names present in the context"""
        return [name for name in self]
        
    def items(self):
        """Return a sequence of (name,boundItem) pairs"""
        return [ (name,self._getOb(name, None)) for name in self ]

    def info(self):
        """Return a sequence of (name,refInfo) pairs"""
        return [ (name,self._get(name,retrieve=False))
                    for name in self
        ]

    def bind(self, name, object, attrs=None):

        """Synonym for __setitem__, with attribute support"""

        self.__setitem__(name,object,attrs)

    def unbind(self, name, object):

        """Synonym for __delitem__"""

        del self[name]


    def rename(self, oldName, newName):

        """Rename 'oldName' to 'newName'"""

        ctx, name = self.resolveToInterface(oldName,IWriteContext)
        
        if ctx is not self:
            ctx.rename(oldName,newName)
            return
            
        ctx, newName = self.resolveToInterface(newName)
       
        self._rename(name,newName)

    def __setitem__(name, object, attrs=None):

        """Bind 'object' under 'name'"""

        ctx, name = self.resolveToInterface(name,IWriteContext)
        
        if ctx is not self:
            ctx[name]=object

        else:
            state,bindattrs = self._mkref(object,name,attrs)
            self._bind(name, state, bindAttrs)


    def __delitem__(self, name):
        """Remove any binding associated with 'name'"""

        ctx, name = self.resolveToInterface(name,IWriteContext)
        
        if ctx is not self:
            del ctx[name]
        else:
            self._unbind(name)


















    # The actual implementation....

    def _get(self, name, retrieve=1):

        """Lookup 'name', returning 'NOT_FOUND' if not found
        
        If 'name' doesn't exist, always return 'NOT_FOUND'.  Otherwise,
        if 'retrieve' is true, return a '(state,attrs)' tuple of binding info.

        If 'retrieve' is false, you may return any value other than
        'NOT_FOUND'.  This is for optimization purposes, to allow you to
        skip costly retrieval operations if a simple existence check will
        suffice."""

        raise NotImplementedError


    def __iter__(self):
        """Return an iterator of the names present in the context

        Note: must return names which are directly usable by _get()!  That is,
        ones which have already been passed through 'toName()' and/or
        'self.schemeParser()'.
        """        
        raise NotImplementedError


    def _bind(self, name, state, attrs=None):
        raise NotImplementedError


    def _unbind(self, name):
        raise NotImplementedError


    def _rename(self, old, new):
        raise NotImplementedError




class AddressContext(NameContext):

    """Handler for address-only URL namespaces"""


    def _get(self, name, retrieve=1):
        return (name, None)     # refInfo, attrs


    def _resolveLocal(self, name, iface):

        # Convert compound names to a URL in this context's scheme

        return self._resolveURL(
            self.schemeParser(self.defaultScheme, str(name)), iface
        )   # XXX should pass name, not str(name), but URL's don't unparse
            # XXX bodies yet



# XXX Backward compatibility

AbstractContext = NameContext
GenericURLContext = AddressContext











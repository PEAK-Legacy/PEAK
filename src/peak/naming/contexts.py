"""Base classes for naming contexts"""

from peak.api import *

from interfaces import *
from names import *
from properties import *

import spi

from peak.binding.components import Component, Once, Acquire

from peak.util.imports import importObject


__all__ = ['AbstractContext', 'GenericURLContext']

























class AbstractContext(Component):

    __implements__ = IBasicContext

    creationName    = Acquire(CREATION_NAME)
    creationParent  = Acquire(CREATION_PARENT)
    objectFactories = Acquire(OBJECT_FACTORIES)
    stateFactories  = Acquire(STATE_FACTORIES)

    schemeParser  = None
    nameClass     = None
    defaultScheme = None
    
    _allowCompositeNames = False    # XXX
    _acceptStringURLs    = True     # XXX


    def close(self):
        pass






















    def _getTargetCtx(self, name, iface=IBasicContext):

        parser = self.schemeParser
        name = toName(name, self.nameClass, self._acceptStringURLs)

        if name.isComposite:        
            if self._allowCompositeNames:
                return self, name
            else:
                name=ParsedURL('+',str(name))   # convert to URL


        if name.isURL:

            if parser:
                if isinstance(name,parser):
                    return self, name
                elif parser.supportsScheme(name.scheme):
                    return self, parser(name.scheme, name.body)

            ctx = spi.getURLContext(name.scheme, self, iface)

            if ctx is None:
                raise exceptions.InvalidName(
                    "Unknown scheme %s in %r" % (name.scheme,name)
                )

            return ctx, name

        if self.nameClass:
            return self, name

        elif parser:
            return self, parser(self.defaultScheme, str(name))

        raise exceptions.InvalidName(
            "This context only supports URLs", name
        )



    def lookup_nns(self, name=None):

        """Find the next naming system after resolving local part"""

        if name is None:

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

        ctx, name = self._getTargetCtx(name)
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
        
        ctx, name = self._getTargetCtx(name)
        if ctx is not self: return ctx[name]
        
        obj = self._getOb(name)
        if obj is NOT_FOUND:
            raise exceptions.NameNotFound(name)

        return obj










    def get(self, name, default=None):
    
        """Lookup 'name' and return an object, or 'default' if not found"""
        
        ctx, name = self._getTargetCtx(name)
        if ctx is not self: return ctx.get(name,default)

        return self._getOb(name, default)


    def _getOb(self, name, default=NOT_FOUND):

        info = self._get(name)
        if info is NOT_FOUND: return default

        state, attrs = info

        return self._deref(state, name, attrs)


    def __contains__(self, name):
        """Return a true value if 'name' has a binding in context"""

        ctx, name = self._getTargetCtx(name)
        
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

        ctx, name = self._getTargetCtx(oldName,IWriteContext)
        
        if ctx is not self:
            ctx.rename(oldName,newName)
            return
            
        ctx, newName = self._getTargetCtx(newName)
       
        self._rename(name,newName)

    def __setitem__(name, object, attrs=None):

        """Bind 'object' under 'name'"""

        ctx, name = self._getTargetCtx(name,IWriteContext)
        
        if ctx is not self:
            ctx[name]=object

        else:
            state,bindattrs = self._mkref(object,name,attrs)
            self._bind(name, state, bindAttrs)


    def __delitem__(self, name):
        """Remove any binding associated with 'name'"""

        ctx, name = self._getTargetCtx(name,IWriteContext)
        
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




class GenericURLContext(AbstractContext):

    """Handler for address-only URL namespaces"""

    def _get(self, name, retrieve=1):
        return (name, None)     # refInfo, attrs















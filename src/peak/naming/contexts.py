"""Base classes for naming contexts"""

from interfaces import *
from names import *
from references import *
from peak.binding.imports import importObject
from peak.binding.components import Component, bindTo, getRootComponent, Once

import spi

_marker = object()

__all__ = ['AbstractContext', 'BasicInitialContext', 'GenericURLContext']




























class AbstractContext(Component):

    __implements__ = IBasicContext

    _supportedSchemes = ()

    _acceptURLs = 1

    _makeName = CompoundName

    _allowCompositeNames = 0

    creationParent = bindTo(IParentForRetrievedObject)

    def __init__(self, parent=None, **kw):
        if kw:
            self.__dict__.update(kw)
        if parent is not None:
            self.setParentComponent(parent)

    def close(self):
        pass

    def __del__(self):
        self.close()
















    def _getTargetCtx(self, name, iface=IBasicContext):

        name = toName(name, self._makeName, self._acceptURLs)

        if name.isComposite:
        
            if self._allowCompositeNames:
                return self, name
                
            else:
                # convert to URL
                name=OpaqueURL('+:'+str(name))


        if name.isURL:

            if self._supportsScheme(name.scheme):
            
                if not isinstance(name,ParsedURL):
                    name = self._makeName(name)

                return self, name

            ctx = spi.getURLContext(name.scheme, self, iface)

            if ctx is None:
                raise InvalidNameException(
                    "Unknown scheme %s in %r" % (name.scheme,name)
                )

            return ctx, name

        return self, name








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


    def _supportsScheme(self, scheme):
        return scheme.lower() in self._supportedSchemes






    def _deref(self, state, name, attrs=None):

        return spi.getObjectInstance(
            state, name, self, attrs
        )


    def lookupLink(self, name):

        """Return terminal link for 'name'"""

        ctx, name = self._getTargetCtx(name)
        if ctx is not self: return ctx.lookupLink(name)

        info = self._get(name,_marker)
        
        if info is _marker:
            raise NameNotFoundException(name)

        state, attrs = info

        if isinstance(state,LinkRef):
            return state

        return self._deref(state, name, attrs)


    def __getitem__(self, name):
    
        """Lookup 'name' and return an object"""
        
        ctx, name = self._getTargetCtx(name)
        if ctx is not self: return ctx[name]
        
        obj = self._getOb(name,_marker)
        if obj is _marker:
            raise NameNotFoundException(name)

        return obj


    def get(self, name, default=None):
    
        """Lookup 'name' and return an object, or 'default' if not found"""
        
        ctx, name = self._getTargetCtx(name)
        if ctx is not self: return ctx.get(name,default)

        return self._getOb(name, default)


    def _getOb(self, name, default):

        info = self._get(name,default)
        if info is default: return info

        state, attrs = info

        return self._deref(state, name, attrs)


    def __contains__(self, name):
        """Return a true value if 'name' has a binding in context"""

        ctx, name = self._getTargetCtx(name)
        
        if ctx is not self:
            return name in ctx

        return self._get(name, _marker, retrieve=False) is not _marker


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
            
            state,bindattrs = spi.getStateToBind(
                object,name,self,attrs
            )

            self._bind(name, state, bindAttrs)


    def __delitem__(self, name):
        """Remove any binding associated with 'name'"""

        ctx, name = self._getTargetCtx(name,IWriteContext)
        
        if ctx is not self:
            del ctx[name]
        else:
            self._unbind(name)














    # The actual implementation....

    def _get(self, name, default=None, retrieve=1):

        """Lookup 'name', returning 'default' if not found

        If 'retrieve' is true, return a '(state,attrs)' tuple of binding info.
        Otherwise, return any true value that is not 'default'.  In either
        case, return 'default' if the name is not bound.
        """

        raise NotImplementedError


    def __iter__(self):
        """Return an iterator of the names present in the context

        Note: must return names which are directly usable by _get()!  That is,
        ones which have already been passed through toName() and/or
        self._makeName().
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

    def _getParserFor(self, scheme):
        from factories import schemeParsers
        return importObject(schemeParsers.get(scheme.lower()))


    def _getTargetCtx(self, name, iface=IBasicContext):

        name = toName(name)

        if name.isComposite:        
            # convert to URL
            name = OpaqueURL('+:'+str(name))

        if name.isURL:
            parser = self._getParserFor(name.scheme)
            
            if parser is not None:            
                return self, parser.fromURL(name)

            ctx = spi.getURLContext(name.scheme, self, iface)

            if ctx is None:
                raise InvalidNameException(
                    "Unknown scheme %s in %r" % (name.scheme,name)
                )

            return ctx, name

        raise InvalidNameException("Not a URL:", name)


    def _get(self, name, default=None, retrieve=1):
        return (name, None)     # refInfo, attrs




class BasicInitialContext(AbstractContext):

    def creationParent(self, d, a):

        """Default binding for 'creationParent' is the nearest LocalConfig

        Note that you should normally supply 'creationParent=someObj' as a
        keyword option to 'naming.InitialContext()' to explicitly set the
        creation parent.  But if you don't, the default creation parent is
        'config.getLocal(binding.getRootComponent(theNewInitialContext))'."""

        from peak.config.api import getLocal
        return getLocal(getRootComponent(self))

    creationParent = Once(creationParent)

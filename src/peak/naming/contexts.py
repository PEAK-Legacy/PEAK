"""Base classes for naming contexts"""

from interfaces import *
from names import *
from references import *

import spi

_marker = object()

__all__ = ['AbstractContext']






























class AbstractContext(object):

    __implements__ = IBasicContext

    _envShared = 1
    _supportedSchemes = ()
    _acceptURLs = 1
    _makeName = CompoundName
    _allowCompositeNames = 0
    
    def __init__(self, env):
        self._environ = env

    def _beforeEnvWrite(self, key, value=_marker):
        if not self._envShared: return
        self._environ = self._environ.copy()
        self._envShared = 0


    def addToEnvironment(self, key, value):
        self._beforeEnvWrite(key,value)
        self._environ[key] = value

    def removeFromEnvironment(self, key):
        self._beforeEnvWrite(key)
        del self._environ[key]

    def getEnvironment(self):
        if not self._envShared: self._envShared = 1
        return self._environ


    def close(self):
        if hasattr(self,'_environ'):
            del self._environ

    def copy(self):
        return self.__class__(self.getEnvironment())



    def _getTargetCtx(self, name, iface=IBasicContext):

        name = toName(name, self._makeName, self._acceptURLs)

        if name.isComposite:
        
            if self._allowCompositeNames:
                return self, name
                
            else:
                # convert to URL
                name=toName('+:'+str(name), acceptURL=1)


        if name.isURL:

            if self._supportsScheme(name.scheme):
            
                if not isinstance(name,ParsedURL):
                    name = self._makeName(name)

                return self, name

            ctx = spi.getURLContext(
                name.scheme, self, None, iface
            )

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
                Reference( None, RefAddr("nns", self) ),
                name, None
            )

        obj = self[name]

        if isinstance(obj,self.__class__):
          
            # Same or subclass, must not be a junction;
            # so delegate the NNS lookup to it
            
            return obj.lookup_nns()


        elif not IBasicContext.isImplementedBy(obj):
            
            # Not a context?  make it an NNS reference

            return self._deref(
                Reference( None, RefAddr("nns", obj) ),
                name, None
            )

        else:
            # It's a context, so just return it
            return obj


    def _supportsScheme(self, scheme):
        return scheme.lower() in self._supportedSchemes




    def _deref(self, state, name, attrs=None):

        return spi.getObjectInstance(
            state, name, self, self.getEnvironment(), attrs
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

        return self._get(name,_marker,None) is not _marker


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
        return [ (name,self._get(name,retrieve=RETRIEVE_INFO))
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
                object,name,self,self.getEnvironment(),attrs
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

        If 'retrieve' is true, return a '(state,attrs)' tuple of
        binding info.  Otherwise, return the key.  In either case,
        return 'default' if the name is not bound.
        """

        raise NotImplementedError


    def __iter__(self):
        """Return an iterator of the names present in the context"""
        raise NotImplementedError

    def _bind(self, name, state, attrs=None):
        raise NotImplementedError

    def _unbind(self, name):
        raise NotImplementedError

    def _rename(self, old, new):
        raise NotImplementedError

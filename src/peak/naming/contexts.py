"""Base classes for naming contexts"""

from peak.api import *

from interfaces import *
from names import *

import spi

from peak.binding.components import Component, Once, Acquire

from peak.util.imports import importObject


__all__ = [
    'NameContext', 'AddressContext',
]
























class NameContext(Component):

    __implements__ = IBasicContext

    parseURLs       = True
    creationName    = Acquire(CREATION_NAME)
    creationParent  = Acquire(CREATION_PARENT)
    objectFactories = Acquire(OBJECT_FACTORIES)
    stateFactories  = Acquire(STATE_FACTORIES)
    schemeParser    = Acquire(SCHEME_PARSER)

    compoundParser  = CompoundName
    compositeParser = CompositeName

    namingAuthority = Once( lambda s,d,a: s.schemeParser() )
    nameInContext   = Once( lambda s,d,a: s.compoundParser(()) )

























    def _resolveComposite(self, name, iface):

        # You should override this method if you want dynamic weak NNS
        # support; that is, if you want to mix composite names and compound
        # names and figure out dynamically when you've crossed over into
        # another naming system.  

        if not name:
            # convert to compound (local) empty name
            return self._resolveLocal(self.compoundParser(()), iface)

        else:

            if isBoundary(name):    # /, x/
                self._checkSupported(name, iface)
                return self, name
                
            local = toName(name[0], self.compoundParser, self.parseURLs)

            if len(name)==1:    # 'x'
                # Single element composite name doesn't change namespaces
                return self.resolveToInterface(local,iface)


            # '/y', 'x/y' -- lookup the part through the '/' and continue

            ctx = self[CompositeName((local,''))]

            if isResolver(ctx):
                return ctx.resolveToInterface(name[1:], iface)

            raise exceptions.NotAContext(
                "Unsupported interface", iface,
                resolvedObj=ctx, remainingName=name[1:]
            )






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
            ctx = self[name[:1]]

            if isResolver(ctx):
                return ctx.resolveToInterface(name[1:],iface)

        except exceptions.NotAContext:
            pass

        # It wasn't a resolver, or didn't support the target interface,
        # so fall back to self and name, if possible.

        self._checkSupported(name, iface)
        return self, name



    def _resolveURL(self, name, iface):

        auth, nic = name.getAuthorityAndName()
        diff = nic - self.nameInContext

        if self.namingAuthority == auth and diff is not None:
            return self.resolveToInterface(diff, iface)

        else:
            ctx = self.__class__(self, namingAuthority=auth)
            return ctx.resolveToInterface(nic, iface)







    def resolveToInterface(self, name, iface=IBasicContext):

        name = toName(name, self.compositeParser, self.parseURLs)

        if name.nameKind == COMPOSITE_KIND:
            return self._resolveComposite(name, iface)

        elif name.nameKind == COMPOUND_KIND:
            name = self.compoundParser(name)        # ensure syntax is correct
            return self._resolveLocal(name,iface)   # resolve locally


        # else name.nameKind == URL_KIND

        parser = self.schemeParser

        if parser:

            if isinstance(name, parser):
                return self._resolveURL(name,iface)

            elif parser.supportsScheme(name.scheme):
                return self._resolveURL(
                    parser(name.scheme, name.body), iface
                )

        # Delegate to the appropriate URL context

        ctx = spi.getURLContext(name.scheme, iface, self)

        if ctx is None:
            raise exceptions.InvalidName(
                "Unknown scheme %s in %r" % (name.scheme,name)
            )

        return ctx.resolveToInterface(name,iface)





    def _contextNNS(self, attrs=None):
        return NNS_Reference( self ), attrs


    def _get_nns(self, name, retrieve=1):

        if not name:
            return self._contextNNS()

        ob = self._get(name, retrieve)

        if ob is NOT_FOUND or not retrieve:
            return ob

        state, attrs = ob

        ob = self._deref(state, name, attrs)
        
        if isinstance(ob, self.__class__):
            # Same or subclass, must not be a junction;
            # so delegate the NNS lookup to it
            return ob._contextNNS(attrs)

        elif isResolver(ob):
            # it's a context, so let it go as-is
            return state, attrs

        # Otherwise, wrap it in an NNS_Reference
        return NNS_Reference( ob ), attrs


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

        if isBoundary(name):
            info = self._get_nns(name[0])
        else:
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

        if isBoundary(name):
            info = self._get_nns(name[0])
        else:
            info = self._get(name)

        if info is NOT_FOUND: return default
        state, attrs = info
        return self._deref(state, name, attrs)

    def __contains__(self, name):
        """Return a true value if 'name' has a binding in context"""

        ctx, name = self.resolveToInterface(name)
        
        if ctx is not self:
            return name in ctx

        if isBoundary(name):
            return self._get_nns(name[0], False) is not NOT_FOUND

        return self._get(name, False) is not NOT_FOUND

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
        return [ (name,self._get(name,False))
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

        oldCtx, n1 = self.resolveToInterface(oldName,IResolver)
        newCtx, n2 = self.resolveToInterface(newName,IResolver)

        if oldCtx.namingAuthority <> newCtx.namingAuthority or \
            crossesBoundaries(n1) or crossesBoundaries(n2):
                raise exceptions.InvalidName(
                    "Can't rename across naming systems", oldName, newName
                )

        n1 = oldCtx.nameInContext + n1
        n2 = newCtx.nameInContext + n2

        common = []
        for p1, p2 in zip(n1,n2):
            if p1!=p2: break
            common.append(p1)

        common = self.compoundParser(common)
        n1 = n1 - common
        n2 = n2 - common

        if self.namingAuthority<>oldCtx.namingAuthority or \
            (common-self.nameInContext) is None:

            ctx, base = self.resolveToInterface(
                oldCtx.namingAuthority + common, IWriteContext
            )

            if ctx is not self:
                ctx.rename(base+n1,base+n2)
                return

        else:    
            base = common - self.nameInContext

        self._rename(base+n1, base+n2)

    def __setitem__(name, object, attrs=None):

        """Bind 'object' under 'name'"""

        ctx, name = self.resolveToInterface(name,IWriteContext)
        
        if ctx is not self:
            ctx[name]=object

        elif isBoundary(name):
            name = name[0]
            state,bindAttrs = self._mkref(object,name,attrs)
            self._bind_nns(name, state, bindAttrs)

        else:
            state,bindAttrs = self._mkref(object,name,attrs)
            self._bind(name, state, bindAttrs)


    def __delitem__(self, name):
        """Remove any binding associated with 'name'"""

        ctx, name = self.resolveToInterface(name,IWriteContext)
        
        if ctx is not self:
            del ctx[name]
        elif isBoundary(name):
            self._unbind_nns(name[0])
        else:
            self._unbind(name)











    # The actual implementation....

    def _get(self, name, retrieve=True):

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

    def _bind_nns(self, name, state, attrs=None):
        raise NotImplementedError

    def _unbind(self, name):
        raise NotImplementedError

    def _unbind_nns(self, name):
        raise NotImplementedError

    def _rename(self, old, new):
        raise NotImplementedError

class AddressContext(NameContext):

    """Handler for address-only URL namespaces"""


    def _get(self, name, retrieve=True):
        return (name, None)     # refInfo, attrs


    def _resolveURL(self, name, iface):

        # Since the URL contains all data needed, there's no need
        # to extract naming authority; just handle the URL directly

        self._checkSupported(name, iface)
        return self, name


    def _resolveLocal(self, name, iface):

        # Convert compound names to a URL in this context's scheme

        return self.resolveToInterface(
            self.namingAuthority + name, iface
        )








from peak.api import *
from interfaces import *
from types import FunctionType, MethodType
import posixpath
from errors import NotFound, NotAllowed, WebException
from environ import traverseAttr, traverseDefault

__all__ = [
    'Traversable', 'Decorator', 'MultiTraverser',
]































class Traversable(binding.Component):

    """Basic traversable object; uses self as its subject and for security"""

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    def traverseTo(self, name, ctx):
        return traverseDefault(ctx, self, 'attr', name, name)

    def preTraverse(self, ctx):
        return ctx    # Should do any traversal requirements checks

    def getURL(self,ctx):
        return ctx.traversedURL

























class Decorator(Traversable):

    """Traversal adapter whose local attributes add/replace the subject's"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForTypes = [object],
    )

    ob = None

    def asTraversableFor(klass, ob):
        return klass(ob = ob)

    asTraversableFor = classmethod(asTraversableFor)


    def traverseTo(self, name, ctx):
        try:
            loc = traverseAttr(ctx, self, 'attr', name, name, NOT_FOUND)
            if loc is not NOT_FOUND:
                return loc

        except NotAllowed:           
            # Access failed, see if attribute is private
            guard = adapt(self, security.IGuardedObject, None)

            if guard is not None and guard.getPermissionForName(name):
                # We have explicit permissions defined, so reject access
                raise

        # attribute is absent or private, fall through to underlying object
        return traverseDefault(ctx, self.ob, 'attr', name, name)







class MultiTraverser(Traversable):

    """Aggregate traversal across a sequence of delegate traversables"""

    items = binding.Require("items to be traversed")

    def preTraverse(self, ctx):
        for item in self.items:
            ctx = IWebTraversable(item).preTraverse(ctx)
        return ctx

    def traverseTo(self, name, ctx):

        newItems = []

        for item in self.items:
            try:
                loc = IWebTraversable(item).traverseTo(name, ctx)
            except NotFound:    # XXX NotAllowed too?
                continue
            else:
                # we should suggest the parent, since our caller won't
                binding.suggestParentComponent(item, name, loc.current)
                newItems.append(loc.current)

        if not newItems:
            raise NotFound(ctx,name)

        if len(newItems)==1:
            loc = newItems[0]
        else:
            loc = self._subTraverser(self, name, items = newItems)
        return ctx.childContext(name,loc)

    _subTraverser = lambda self, *args, **kw: self.__class__(*args,**kw)






class CallableAsHTTP(protocols.Adapter):

    """Make functions/methods callable"""

    protocols.advise(
        instancesProvide = [IHTTPHandler],
        asAdapterForTypes = [FunctionType, MethodType]
    )

    def handle_http(self, ctx):
        # XXX this should return to mapply-like functionality someday
        return self.subject(ctx)






























from peak.api import *
from interfaces import *
from types import FunctionType, MethodType
import posixpath
from errors import NotFound, NotAllowed, WebException
from environ import traverseAttr, traverseDefault
from urlparse import urljoin

__all__ = [
    'Traversable', 'Place', 'Decorator', 'MultiTraverser',
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

























class Place(Traversable):
    """Traversable that has a fixed URL (maybe relative to parent component)

    The 'place_url' attribute of a 'Place' determines its response to the
    'getURL()' method.  If the 'place_url' is relative (i.e. doesn't start with
    a URL scheme or a '/'), it is relative to the application's root URL.
    Otherwise, it's absolute.

    If you do not set a 'place_url', then it will be computed using the
    instance's 'getComponentName()', added onto the 'place_url' of its
    'getParentComponent()'.  If the instance has no name (i.e., its name
    is 'None'), or its parent cannot be adapted to 'web.IPlace', then it
    assumes that it is the application's root object, and thus uses the
    application root URL as its own URL.  (Unless of course you've explicitly
    set a 'place_url'.)

    As a special case, if the instance's name is '""' (the empty string), then
    it will use the same URL as its parent 'IPlace'.  This peculiarity is
    useful when a component needs to be in an 'IPlace' component tree, without
    affecting the URLs of its child components.
    """

    protocols.advise(
        instancesProvide = [IPlace]
    )

    def getURL(self, ctx):
        # Root-relative URL
        base = ctx.rootURL+'/'[ctx.rootURL.endswith('/'):]
        return urljoin(base,self.place_url)











    def place_url(self,d,a):

        name = self.getComponentName()
        if name is None:
            # No name, we must be the root
            return ''

        base = IPlace(self.getParentComponent(),None)
        if base is not None:
            if name:
                return posixpath.join(base.place_url, name)
            else:
                return base.place_url

        # No parent, we must be the root
        return ''

    place_url = binding.Make(place_url)























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






























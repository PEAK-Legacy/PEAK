from peak.api import *
from interfaces import *
from types import FunctionType, MethodType, ClassType
import posixpath
from errors import NotFound, NotAllowed, WebException
from environ import traverseAttr, traverseDefault
from urlparse import urljoin

__all__ = [
    'Traversable', 'Place', 'Decorator', 'MultiTraverser', 'Location',
]






























class Traversable(binding.Component):

    """Basic traversable object; uses self as its subject and for security"""

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    def traverseTo(self, name, ctx, default=NOT_GIVEN):
        return traverseDefault(ctx, self, 'attr', name, name, default)

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























class TypeAsViewTarget(protocols.Adapter):

    protocols.advise(
        instancesProvide = [IViewTarget],
        asAdapterForTypes=[type,ClassType]
    )

    def registerWithProtocol(self,protocol,adapter):
        protocols.declareAdapter(
            adapter,[protocol],forTypes=[self.subject]
        )


class ProtocolAsViewTarget(protocols.Adapter):
    protocols.advise(
        instancesProvide = [IViewTarget],
        asAdapterForProtocols=[protocols.IOpenProtocol]
    )

    def registerWithProtocol(self,protocol,adapter):
        protocols.declareAdapter(
            adapter,[protocol],forProtocols=[self.subject]
        )


















class Location(Place,binding.Configurable):
    """A location suitable for configuration via site map"""

    protocols.advise(
        instancesProvide = [IConfigurableLocation]
    )

    containers = binding.Make(list)
    have_views = False


    def preTraverse(self,ctx):
        if self.have_views:
            ctx = ctx.clone(view_protocol=VIEW_NAMES.of(self).get)
        return ctx


    def traverseTo(self, name, ctx, default=NOT_GIVEN):
        if self.have_views:
            ctx = ctx.clone(view_protocol=VIEW_NAMES.of(self).get)

        result = Place.traverseTo(self,name,ctx,NOT_FOUND)

        if result is NOT_FOUND:
            for perm,cont in self.containers:
                if perm is not None:
                    if not ctx.allows(cont,permissionNeeded=perm):
                        continue
                context = ctx.clone(current=cont)
                result = context.traverseName(name,NOT_FOUND)
                if result is not NOT_FOUND:
                    return result

        if default is NOT_GIVEN:
            raise NotFound(ctx,name)
        return default





    def registerLocation(self,location_id,path):
        path = adapt(path,web.TraversalPath)
        self.registerProvider(
            'peak.web.locations.'+location_id,config.Value(path)
        )

    def registerView(self,target,name,handler):
        self.have_views = True
        IViewTarget(target).registerWithProtocol(
            config.registeredProtocol(self,VIEW_NAMES+'.'+name),
            lambda ob:handler
        )

    def addContainer(self,container,permissionNeeded=None):
        binding.suggestParentComponent(self,None,container)
        self.containers.append((permissionNeeded,container))

























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


    def traverseTo(self, name, ctx, default=NOT_GIVEN):
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
        return traverseDefault(ctx, self.ob, 'attr', name, name, default)







class MultiTraverser(Traversable):

    """Aggregate traversal across a sequence of delegate traversables"""

    items = binding.Require("items to be traversed")

    def preTraverse(self, ctx):
        for item in self.items:
            ctx = IWebTraversable(item).preTraverse(ctx)
        return ctx

    def traverseTo(self, name, ctx, default=NOT_GIVEN):

        newItems = []

        for item in self.items:
            loc = IWebTraversable(item).traverseTo(name, ctx, NOT_FOUND)
            if loc is NOT_FOUND:    # XXX trap NotAllowed too?
                continue
            else:
                # we should suggest the parent, since our caller won't
                binding.suggestParentComponent(item, name, loc.current)
                newItems.append(loc.current)

        if not newItems:
            if default is NOT_GIVEN:
                raise NotFound(ctx,name)
            return default

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






























from peak.api import *
from interfaces import *
from types import FunctionType, MethodType, ClassType
import posixpath
from errors import NotFound, NotAllowed, WebException
from environ import traverseAttr, traverseDefault, traverseView
from urlparse import urljoin
from peak.util.EigenData import AlreadyRead

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

    def beforeHTTP(self, ctx):
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























[dispatch.on('target')]
def registerWithProtocol(target,protocol,adapter):
    """Register 'target' as a source of 'protocol', via 'adapter'"""
    

[registerWithProtocol.when([type,ClassType])]
def registerTypeWithProtocol(target,protocol,adapter):
    protocols.declareAdapter(adapter,[protocol],forTypes=[target])


[registerWithProtocol.when([protocols.IOpenProtocol])]
def registerProtocolWithProtocol(target,protocol,adapter):
    protocols.declareAdapter(adapter,[protocol],forProtocols=[target])




























class Location(Place,binding.Configurable):

    """A location suitable for configuration via site map"""

    protocols.advise(
        instancesProvide = [IConfigurableLocation]
    )

    containers = binding.Make(list)
    have_views = False
    local_views = binding.Make(dict)

    def traverseTo(self, name, ctx, default=NOT_GIVEN):

        for perm,cont in self.containers:
            if perm is not None:
                if not ctx.allows(cont,permissionNeeded=perm):
                    continue
            context = ctx.clone(current=cont,viewHandler=self.viewHandler)
            result = context.traverseName(name,NOT_FOUND)
            if result is not NOT_FOUND:
                context = context.parentContext()
                if context.current is cont:
                    context.current = self
                return result

        return traverseDefault(ctx, self, '', name, name, default)


    def registerLocation(self,location_id,path):
        path = adapt(path,web.TraversalPath)
        self.registerProvider(LOCATION_ID(location_id),config.Value(path))


    def addContainer(self,container,permissionNeeded=None):
        binding.suggestParentComponent(self,None,container)
        self.containers.insert(0,(permissionNeeded,container))




    def registerView(self,target,name,handler):
        if target is None:
            self.local_views[name] = handler
        else:
            self.have_views = True
            registerWithProtocol(
                target, self.registrationProtocol(name), lambda ob:(ob,handler)
            )


    def registrationProtocol(self,name):
        parent = config.parentProviding(
            self.getParentComponent(), IViewService, None
        )

        if parent is not None:
            parent.registrationProtocol(name)   # force it to register first

        return config.registeredProtocol(self,str(VIEW_NAMES+'.'+name))


    def viewHandler(self,name,ob,default=None):
        if ob is self and name in self.local_views:
            return self.local_views[name]

        p = self._viewProtocolFor(name,None)
        if p is not None:
            target, handler = adapt(ob,p,(NOT_FOUND,NOT_FOUND))
            if handler is not NOT_FOUND:
                return lambda ctx,ob,ns,nm,qname,default=NOT_GIVEN: (
                    handler(ctx, target, ns, nm, qname, default)
                )
        return default

    _viewProtocolFor = binding.Make(lambda self:VIEW_NAMES.of(self).get)






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
        loc = traverseAttr(ctx, self, 'attr', name, name, NOT_FOUND)
        if loc is not NOT_FOUND:
            return loc

        # attribute is absent or private, fall through to underlying object
        return traverseDefault(ctx, self.ob, 'attr', name, name, default)


    def getURL(self,ctx):
        uctx = traverseView(
            ctx, self.ob,'view','peak.web.url','peak.web.url', None
        )
        if uctx is not None:
            return uctx.current
        return ctx.traversedURL







class MultiTraverser(Traversable):

    """Aggregate traversal across a sequence of delegate traversables"""

    items = binding.Require("items to be traversed")

    def beforeHTTP(self, ctx):
        for item in self.items:
            ctx = IWebTraversable(item).beforeHTTP(ctx)
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






























"""Support for 'zope.publisher'"""

from peak.api import *
from interfaces import *
from peak.running.commands import EventDriven

__all__ = [
    'Interaction', 'NullAuthenticationService', 'InteractionPolicy',
    'CGIPublisher', 'DefaultExceptionHandler', 'NullSkinService',
    'TraversalPath'
]


class DefaultExceptionHandler(binding.Singleton):

    def handleException(self, interaction, thrower, exc_info, retry_allowed=1):
        try:
            storage.abort(interaction.app)

            # XXX note that the following assumes exc_info is available as
            # XXX sys.exc_info; will this always be the case?
            interaction.log.exception("ERROR:")

            # XXX Maybe the following should be in a method on interaction?
            interaction.response.reset()
            interaction.response.setCharsetUsingRequest(interaction.request)
            interaction.response.handleException(exc_info)

        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None









class TraversalPath(naming.CompoundName):

    """Name that knows how to do 'IWebTraversable' traversal"""

    syntax = naming.PathSyntax(
        direction=1,
        separator='/'
    )

    def traverse(self, ob, interaction, getRoot = lambda o,i: o):

        path = iter(self)
        part = path.next()

        if not part:
            ob = getRoot(ob, interaction)
        else:
            # reset to beginning
            path = iter(self)

        for part in path:

            if part == '..':
                parent = binding.getParentComponent(ob)
                if parent is not None and parent is not interaction.skin:
                    ob = parent

            elif part=='.':
                pass

            elif part:
                newOb = ob.traverseTo(part, interaction)
                if (newOb is NOT_FOUND or newOb is NOT_ALLOWED):
                    return newOb
                binding.suggestParentComponent(ob,part,newOb)
                ob = newOb

        return ob



class NullSkinService(binding.Component):

    app = binding.bindTo('policy/app')

    policy = binding.bindTo('..')

    root = binding.Once(
        lambda self, d, a: adapt(self.app, self.policy.pathProtocol)
    )

    defaultSkin = binding.Once(
        lambda self, d, a:
            web.Skin(
                self.app, root=self.root, policy=self.policy,
                layers=[web.DefaultLayer()]
            )
            # XXX needs to create a default layer
    )

    def getSkin(self, interaction):
        return self.defaultSkin


class NullAuthenticationService(binding.Singleton):

    def getUser(self, interaction):
        return None














class InteractionPolicy(binding.Component, protocols.StickyAdapter):

    protocols.advise(
        instancesProvide = [IInteractionPolicy],
        asAdapterForProtocols = [binding.IComponent],
        factoryMethod = 'fromComponent',
    )

    def fromComponent(klass, ob, proto):
        ip = klass(ob)
        protocols.StickyAdapter.__init__(ip, ob, proto)
        return ip

    fromComponent = classmethod(fromComponent)

    app           = binding.bindTo('./subject')
    log           = binding.bindTo(APPLICATION_LOG)
    errorProtocol = binding.bindTo(ERROR_PROTOCOL)
    pathProtocol  = binding.bindTo(PATH_PROTOCOL)
    pageProtocol  = binding.bindTo(PAGE_PROTOCOL)
    authSvc       = binding.bindTo(AUTHENTICATION_SERVICE)
    skinSvc       = binding.bindTo(SKIN_SERVICE)
    defaultMethod = binding.bindTo(DEFAULT_METHOD)

    resourcePrefix   = binding.bindTo(RESOURCE_PREFIX)
    interactionClass = binding.bindTo(INTERACTION_CLASS)















class Interaction(security.Interaction):

    """Base publication policy/interaction implementation"""

    policy   = binding.requireBinding(
        "IInteractionPolicy for application", adaptTo=IInteractionPolicy
    )
    request  = binding.requireBinding("Request object")

    response = binding.bindTo("request/response")

    app      = binding.bindTo('policy/app')
    log      = binding.bindTo('policy/log')

    errorProtocol  = binding.bindTo('policy/errorProtocol')
    pathProtocol   = binding.bindTo('policy/pathProtocol')
    pageProtocol   = binding.bindTo('policy/pageProtocol')
    resourcePrefix = binding.bindTo('policy/resourcePrefix')

    user = binding.Once(
        lambda self,d,a: self.policy.authSvc.getUser(self)
    )

    skin = binding.Once(
        lambda self,d,a: self.policy.skinSvc.getSkin(self)
    )

    def beforeTraversal(self, request):
        """Begin transaction before traversal"""
        storage.beginTransaction(self.app)

    def getApplication(self,request):
        return self.skin

    def callTraversalHooks(self, request, ob):
        ob.preTraverse(self)





    def traverseName(self, request, ob, name, check_auth=1):

        nextOb = TraversalPath([name]).traverse(ob,self)

        if nextOb is NOT_FOUND:
            return self.notFound(ob, name)

        if nextOb is NOT_ALLOWED:
            return self.notAllowed(ob, name)

        return nextOb


    def afterTraversal(self, request, ob):
        # Let the found object know it's being traversed
        ob.preTraverse(self)


    def getDefaultTraversal(self, request, ob):

        """Find default method if object isn't renderable"""

        default = self.policy.defaultMethod

        if default and adapt(ob.getObject(), self.pageProtocol, None) is None:

            # Not renderable, try for default method
            newOb = ob.traverseTo(default, self)

            if newOb is not NOT_FOUND:
                # The traversal will succeed, so tell the request to proceed
                return ob, (default,)

        # object is renderable, default traversal will fail, or no default
        # is in use: just render the object directly
        return ob, ()





    def callObject(self, request, ob):

        page = adapt(ob.getObject(), self.pageProtocol, None)

        if page is None:
            # Render the found object directly
            return ob.getObject()

        binding.suggestParentComponent(ob.getParentComponent(),None,page)
        return page.render(self)


    def afterCall(self, request):

        """Commit transaction after successful hit"""

        storage.commitTransaction(self.app)
        if request.method=="HEAD":
            # XXX this doesn't handle streaming; there really should be
            # XXX a different response class for HEAD; Zope 3 should
            # XXX probably do it that way too.
            request.response.setBody('')


    def handleException(self, object, request, exc_info, retry_allowed=1):

        """Convert exception to a handler, and invoke it"""

        try:
            handler = adapt(
                exc_info[1], self.errorProtocol, DefaultExceptionHandler
            )
            return handler.handleException(
                self, object, exc_info, retry_allowed
            )
        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None


    def notFound(self, ob, name):
        from zope.publisher.interfaces import NotFound
        raise NotFound(ob, name, self.request)          # XXX


    def notAllowed(self, ob, name):
        from zope.publisher.interfaces import Unauthorized
        raise Unauthorized(name=name)   # XXX

































class CGIPublisher(binding.Component):

    """Use 'zope.publisher' to run an application as CGI/FastCGI

    For basic use, this just needs an 'app' parameter, and it will publish
    that application using 'BaseInteraction' as its interaction class,
    'IWebTraversable' and 'IWebPage' as its path and page protocols,
    and the default request classes supplied by 'zope.publisher'.

    Three HTTP variants are supported: "generic" HTTP, "browser" HTTP, and
    XML-RPC.  They are distinguished from one another by the CGI
    'REQUEST_METHOD' and 'CONTENT_TYPE' environment variables.  A "POST"
    of 'text/xml' is considered XML-RPC, while all other "POST", "GET",
    and "HEAD" methods are considered "browser" HTTP.  Any other methods
    ("PUT", "DELETE", etc.) are considered "generic" HTTP (e.g. WebDAV).

    You can override specific request types as follows::

        HTTP Variant    KW for Request Class    Property Name
        ------------    --------------------    -----------------------
        "Generic"       mkHTTP                  peak.web.HTTPRequest
        "XML-RPC"       mkXMLRPC                peak.web.XMLRPCRequest
        "Browser"       mkBrowser               peak.web.BrowserRequest

    So, for example, to change the XML-RPC request class, you might do this::

        myPublisher = CGIPublisher( mkXMLRPC = MyXMLRPCRequestClass )

    In practice, you're more likely to want to change the interaction class,
    since the default request classes are likely to suffice for most
    applications.  (It's also easier to change the properties in an application
    .ini file than to supply the classes as keyword arguments.)

    'CGIPublisher' is primarily intended as a base adapter class for creating
    web applications.  To use it, you can simply subclass it, replacing the
    'app' binding with an instance of your application, and replacing any other
    parameters as needed.  The resulting class can be invoked with 'peak CGI'
    to run as a CGI or FastCGI application."""



    protocols.advise(
        instancesProvide=[running.IRerunnableCGI],
    )


    # The fromApp method is registered as an adapter factory for
    # arbitrary components to IRerunnableCGI, in peak.running.interfaces.
    # If we registered it here, it wouldn't be usable unless peak.web
    # was already imported, which leads to bootstrap problems, at least
    # with very trivial web apps (like examples/trivial_web).

    def fromApp(klass, app, protocol):
        return klass(app, app=app)

    fromApp = classmethod(fromApp)


    app              = binding.requireBinding("Application root to publish")
    policy           = binding.bindTo('app', adaptTo = IInteractionPolicy)
    interactionClass = binding.bindTo('policy/interactionClass')


    # items to (potentially) replace in subclasses

    publish   = binding.bindTo('import:zope.publisher.publish:publish')

    mkXMLRPC  = binding.bindTo(PropertyName('peak.web.XMLRPCRequest'))
    mkBrowser = binding.bindTo(PropertyName('peak.web.BrowserRequest'))
    mkHTTP    = binding.bindTo(PropertyName('peak.web.HTTPRequest'))

    _browser_methods = binding.Copy( {'GET':1, 'POST':1, 'HEAD':1} )










    def runCGI(self, input, output, errors, env, argv=()):

        """Process one request"""

        method = env.get('REQUEST_METHOD', 'GET').upper()

        if method in self._browser_methods:
            if (method == 'POST' and
                env.get('CONTENT_TYPE', '').lower().startswith('text/xml')
                ):
                request = self.mkXMLRPC(input, output, env)
            else:
                request = self.mkBrowser(input, output, env)
        else:
            request = self.mkHTTP(input, output, env)

        request.setPublication(
            self.interactionClass(
                self, None, policy = self.policy, request = request
            )
        )
        return self.publish(request) or 0




















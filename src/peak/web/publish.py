"""Support for 'zope.publisher'"""

from peak.api import *
from interfaces import *
from peak.running.commands import EventDriven
from zope.publisher import http, browser, xmlrpc, publish

__all__ = [
    'Interaction', 'NullAuthenticationService', 'InteractionPolicy',
    'HTTPRequest', 'BrowserRequest', 'XMLRPCRequest', 'CGIPublisher',
]






























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

    log              = binding.bindTo(APPLICATION_LOG)
    locationProtocol = binding.bindTo(LOCATION_PROTOCOL)
    behaviorProtocol = binding.bindTo(BEHAVIOR_PROTOCOL)
    authSvc          = binding.bindTo(AUTHENTICATION_SERVICE)    
    defaultMethod    = binding.bindTo(DEFAULT_METHOD)















class Interaction(security.Interaction):

    """Base publication policy/interaction implementation"""

    app      = binding.requireBinding("Application root to publish")
    request  = binding.requireBinding("Request object")
    response = binding.bindTo("request/response")

    policy   = binding.bindTo('app', adaptTo = IInteractionPolicy)
    log      = binding.bindTo('policy/log')

    root     = binding.Once(
        lambda s,d,a: adapt(s.app, s.locationProtocol)
    )   
   
    locationProtocol = binding.bindTo('policy/locationProtocol')
    behaviorProtocol = binding.bindTo('policy/behaviorProtocol')

    user = binding.Once(
        lambda self,d,a: self.policy.authSvc.getUser(self)
    )


    def beforeTraversal(self, request):
        """Begin transaction before traversal"""
        storage.beginTransaction(self.app)


    def getApplication(self,request):
        return self.root


    def callTraversalHooks(self, request, ob):
        ob.preTraverse(self)







    def traverseName(self, request, ob, name, check_auth=1):

        if not name or name=='.':
            return ob

        if name=='..':
            parent = binding.getParentComponent(ob)
            if parent is not None and ob is not self.app:
                return parent
            return ob

        nextOb = ob.getSublocation(name, self)
        if nextOb is NOT_FOUND:
            return self.notFound(ob, name)
        if nextOb is NOT_ALLOWED:
            return self.notAllowed(ob, name)
        return nextOb


    def afterTraversal(self, request, ob):
        pass    # nothing to do after traversal yet


    def getDefaultTraversal(self, request, ob):

        """Find default method if object isn't renderable"""

        if adapt(ob.getObject(), self.behaviorProtocol, None) is None:
            # Not renderable, try for default method
            return ob, (self.policy.defaultMethod,)
            
        # object is renderable, no need for further traversal
        return ob, ()
            

    def callObject(self, request, ob):
        return adapt(ob.getObject(), self.behaviorProtocol).render(self)




    def afterCall(self, request):

        """Commit transaction after successful hit"""

        storage.commitTransaction(self.app)
        if request.method=="HEAD":
            # XXX this doesn't handle streaming; there really should be
            # XXX a different response class for HEAD; Zope 3 should
            # XXX probably do it that way too.
            request.response.setBody('')


    def handleException(self, object, request, exc_info, retry_allowed=1):

        """Abort transaction and delegate error handling to response"""

        # XXX this should actually adapt the error to an error protocol,
        # XXX and then delegate its handling there.

        try:
            storage.abort(self.app)
            self.log.exception("Error handling request")
            self.response.reset()
            self.response.setCharsetUsingRequest(self.request)
            self.response.handleException(exc_info)
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


class HTTPRequest(http.HTTPRequest, http.HTTPCharsets):

    """HTTPRequest with a built-in charset handler"""

    __slots__ = ()
    request = property(lambda self: self)


class BrowserRequest(
    browser.BrowserRequest, browser.BrowserLanguages, http.HTTPCharsets
):

    """BrowserRequest w/built-in charset and language handlers"""

    __slots__ = ()
    request = property(lambda self: self)


class XMLRPCRequest(xmlrpc.XMLRPCRequest, http.HTTPCharsets):

    """XMLRPCRequest w/built-in charset handler"""

    __slots__ = ()
    request = property(lambda self: self)

















class CGIPublisher(binding.Component):

    """Use 'zope.publisher' to run an application as CGI/FastCGI

    For basic use, this just needs an 'app' parameter, and it will publish
    that application using 'BaseInteraction' as its interaction class,
    'IWebLocation' and 'IWebMethod' as its location and behavior protocols,
    and the default request classes supplied by 'zope.publisher'.

    Three HTTP variants are supported: "generic" HTTP, "browser" HTTP, and
    XML-RPC.  They are distinguished from one another by the CGI
    'REQUEST_METHOD' and 'CONTENT_TYPE' environment variables.  A "POST"
    of 'text/xml' is considered XML-RPC, while all other "POST", "GET",
    and "HEAD" methods are considered "browser" HTTP.  Any other methods
    ("PUT", "DELETE", etc.) are considered "generic" HTTP (e.g. WebDAV).

    You can override specific request types as follows::

        HTTP Variant    KW for Request Class
        ------------    --------------------
        "Generic"       mkHTTP
        "XML-RPC"       mkXMLRPC
        "Browser"       mkBrowser

    So, for example, to change the XML-RPC request class, you might do this::

        myPublisher = CGIPublisher( mkXMLRPC = MyXMLRPCRequestClass )

    In practice, you're more likely to want to change the interaction class,
    since the default request classes provided by 'zope.publisher' are likely
    to suffice for most applications.

    'CGIPublisher' is primarily intended as a base adapter class for creating
    web applications.  To use it, you can simply subclass it, replacing the
    'app' binding with an instance of your application, and replacing any other
    parameters as needed.  The resulting class can be invoked with 'peak CGI'
    to run as a CGI or FastCGI application."""




    protocols.advise(
        instancesProvide=[running.IRerunnableCGI],
        asAdapterForTypes=[binding.Component],
        factoryMethod = 'fromApp',
    )


    def fromApp(klass, app, protocol):
        return klass(app, app=app)

    fromApp = classmethod(fromApp)


    app = binding.requireBinding("Application root to publish")

    interactionClass=binding.bindTo(INTERACTION_CLASS)



    # items to (potentially) replace in subclasses

    publish   = staticmethod(publish.publish)

    mkXMLRPC  = XMLRPCRequest   # XXX should these be a property+default?
    mkBrowser = BrowserRequest
    mkHTTP    = HTTPRequest

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
                self, None, app = self.app, request = request
            )
        )
        return self.publish(request) or 0




















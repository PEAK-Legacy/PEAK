"""Support for 'zope.publisher'"""

from peak.api import *
from interfaces import *
from peak.running.commands import EventDriven

__all__ = [
    'BaseInteraction',
]
































class BaseInteraction(security.Interaction):

    """Base publication policy/interaction implementation"""

    app      = binding.bindTo('../app')
    request  = binding.requireBinding("Request object")
    response = binding.bindTo("request/response")

    locationProtocol = binding.bindTo('../locationProtocol')
    behaviorProtocol = binding.bindTo('../behaviorProtocol')


    def beforeTraversal(self, request):
        """Begin transaction before traversal"""
        storage.beginTransaction(self.app)


    def getApplication(self,request):
        app = adapt(self, self.locationProtocol)
        binding.suggestParentComponent(None,None,app)
        return app


    def callTraversalHooks(self, request, ob):
        pass    # no such thing as traversal hooks at present


    def traverseName(self, request, ob, name, check_auth=1):

        if not name or name='.':
            return ob

        if name=='..':
            parent = binding.getParentComponent(ob)
            if parent is not None and ob is not self.app:
                return parent
            return ob

        return ob.getSublocation(name, self)


    def afterTraversal(self, request, ob):
        pass    # nothing to do after traversal yet


    def getDefaultTraversal(self, request, ob):
        # XXX do we need this?
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
        try:
            storage.abort(self.app)
            self.response.reset()
            self.response.handleException(exc_info)
        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None








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
        asAdapterForTypes=[binding.component],
        factoryMethod = 'fromApp',
    )

    app       = binding.requireBinding("Application root to publish")
    publish   = binding.bindTo("import:zope.publisher.publish:publish")

    mkXMLRPC  = binding.bindTo("import:zope.publisher.xmlrpc:XMLRPCRequest")
    mkBrowser = binding.bindTo("import:zope.publisher.browser:BrowserRequest")
    mkHTTP    = binding.bindTo("import:zope.publisher.http:HTTPRequest")

    _browser_methods = binding.Copy( {'GET':1, 'POST':1, 'HEAD':1} )

    # items to replace in subclasses
    interactionClass = BaseInteraction
    locationProtocol = IWebLocation
    behaviorProtocol = IWebMethod


    def fromApp(klass, app, protocol):
        return klass(app=app)


















    def runCGI(self, input, output, errors, env, argv=[]):

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
                self, None, request = request
            )
        )
        return self.publish(request) or 0




















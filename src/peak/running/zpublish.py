"""Support for 'zope.publisher'"""

from peak.api import *
from interfaces import *
from zope.publisher.base import DefaultPublication
from commands import EventDriven

__all__ = [

    'BasePublication',
    'HTTPPublication', 'XMLRPCPublication', 'BrowserPublication',

    'CGICommand', 'CGIPublisher', 'FastCGIAcceptor',
]



























class BasePublication(binding.Component, DefaultPublication):

    """Base publication policy"""

    app = binding.requireBinding("Application to be published")


    def beforeTraversal(self, request):

        """Begin transaction and attempt authentication"""

        super(BasePublication,self).beforeTraversal(request)
        storage.begin(self.app)

        # XXX try to authenticate here


    def callTraversalHooks(self, request, ob):
        pass    # XXX try local authentication if user not yet found


    def afterTraversal(self, request, ob):
        pass    # XXX try local authentication if user not yet found


    def afterCall(self, request):
        """Commit transaction after successful hit"""
        storage.commit(self.app)


    def handleException(self, object, request, exc_info, retry_allowed=1):
        """Abort transaction and delegate error handling to response"""

        try:
            storage.abort(self.app)
            request.response.handleException(exc_info)
        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None

class HTTPPublication(BasePublication):

    def afterCall(self,request):

        """Handle "HEAD" method by truncating output"""

        super(HTTP,self).afterCall(request)

        if request.method=="HEAD":
            # XXX this doesn't handle streaming; there really should be
            # XXX a different response class for HEAD; Zope 3 should
            # XXX probably do it that way too.
            request.response.setBody('')


class XMLRPCPublication(HTTP):

    """XMLRPC support"""

    def traverseName(self,request,ob,name):
        # XXX should try for a "methods" view of 'ob'
        return super(XMLRPC,self).traverseName(request,ob,name)


class BrowserPublication(HTTP):

    """DWIM features for human viewers"""

    def getDefaultTraversal(self, request, ob):
        # XXX this should figure out a default traversal for human viewers
        return ob, ()










class CGIPublisher(binding.Component):

    """Use 'zope.publisher' to run an application as CGI/FastCGI

    For basic use, this just needs an 'app' parameter, and it will publish
    that application using the default publication classes supplied by
    'peak.running.zpublish' and default request classes supplied by
    'zope.publisher'.

    Three HTTP variants are supported: "generic" HTTP, "browser" HTTP, and
    XML-RPC.  They are distinguished from one another by the CGI
    'REQUEST_METHOD' and 'CONTENT_TYPE' environment variables.  A "POST"
    of 'text/xml' is considered XML-RPC, while all other "POST", "GET",
    and "HEAD" methods are considered "browser" HTTP.  Any other methods
    ("PUT", "DELETE", etc.) are considered "generic" HTTP (e.g. WebDAV).

    You can override specific publication or request types as follows::

        HTTP Variant    KW for Request Class    KW for Publication Class
        ------------    --------------------    ------------------------
        "Generic"       mkHTTP                  httpPubClass
        "XML-RPC"       mkXMLRPC                xmlrpcPubClass
        "Browser"       mkBrowser               browserPubClass

    So, for example, to change the XML-RPC request class, you might do this::

        myPublisher = CGIPublisher( mkXMLRPC = MyXMLRPCRequestClass )

    In practice, you're more likely to want to change the publication classes,
    since the default request classes provided by 'zope.publisher' are likely
    to suffice for most applications.  A publication is a policy object that
    controls how 'zope.publisher' processes a request; see 'IPublication' in
    'zope.publisher.interfaces' for information on what a publication object
    needs to do.

    There are two ways to customize the publication objects used by a
    'CGIPublisher': you can set the publication class (e.g. 'httpPubClass')
    or you can supply a prepared publication instance.  The two examples
    below produce the same result::


        myPublisher = CGIPublisher( app=anApp, httpPubClass=MyHTTPPubClass )

        myPublisher = CGIPublisher( httpPublication=MyHTTPPubClass(app=anApp) )

    If you supply publication objects ('httpPublication', 'xmlrpcPublication',
    and 'browserPublication'), 'CGIPublisher' does not need the publication
    classes or even an 'app' object, as it only uses these in order to generate
    its default publication instances.

    'CGIPublisher' isn't intended for standalone use; it's effectively a
    configurable subcomponent of 'CGICommand'.  If you need to control the
    behavior it supplies, you can create a customized 'CGIPublisher' and
    use it to create a 'CGICommand' that behaves the way you want.  See
    'CGICommand' on how to set up and run a CGI publishing application."""

    protocols.advise(
        instancesProvide=[IRerunnable]
    )

    app       = binding.requireBinding("Application root to publish")
    publish   = binding.bindTo("import:zope.publisher.publish:publish")

    mkXMLRPC  = binding.bindTo("import:zope.publisher.xmlrpc:XMLRPCRequest")
    mkBrowser = binding.bindTo("import:zope.publisher.browser:BrowserRequest")
    mkHTTP    = binding.bindTo("import:zope.publisher.http:HTTPRequest")

    xmlrpcPubClass  = XMLRPCPublication
    browserPubClass = BrowserPublication
    httpPubClass    = HTTPPublication

    _browser_methods = binding.Copy( {'GET':1, 'POST':1, 'HEAD':1} )










    def run(self, input, output, errors, env, argv=[]):

        """Process one request"""

        method = env.get('REQUEST_METHOD', 'GET').upper()

        if method in self._browser_methods:
            if (method == 'POST' and
                env.get('CONTENT_TYPE', '').lower().startswith('text/xml')
                ):
                request = self.mkXMLRPC(input, output, env)
                request.setPublication(self.xmlrpcPublication)
            else:
                request = self.mkBrowser(input, output, env)
                request.setPublication(self.browserPublication)
        else:
            request = self.mkHTTP(input, output, env)
            request.setPublication(self.httpPublication)

        return self.publish(request)


    xmlrpcPublication = binding.Once(
        lambda self,d,a: self.xmlrpcPubClass(app=self.app)
    )


    browserPublication = binding.Once(
        lambda self,d,a: self.browserPubClass(app=self.app)
    )


    httpPublication = binding.Once(
        lambda self,d,a: self.httpPubClass(app=self.app)
    )






class FastCGIAcceptor(binding.Component):

    """Accept FastCGI connections"""

    command  = binding.requireBinding("IRerunnable command")

    mainLoop = binding.bindTo(IMainLoop)
    ping     = binding.bindTo('mainLoop/activityOccurred')

    fcgi     = binding.bindTo('import:fcgiapp')
    accept   = binding.bindTo('fcgi/Accept')
    finish   = binding.bindTo('fcgi/Finish')


    def fileno(self):
        return 0    # FastCGI is always on 'stdin'


    def doRead(self):

        self.ping()

        i,o,e,env = self.accept()

        try:
            self.command.run(i,o,e,dict(env))

        finally:
            self.finish()
            self.ping()











class CGICommand(EventDriven):

    """Run CGI/FastCGI in an event-driven loop

    If the 'fcgiapp' module is available and 'sys.stdin' is a socket, this
    command will listen for FastCGI connections and process them as they
    arrive.  Otherwise, it will assume that it is being run as a CGI, and
    use its environment attributes as the environment for the CGI command.

    Note that if running in CGI mode, a 'CGICommand' will exit its reactor
    loop immediately upon completion of the request, without running any
    subsequent scheduled events, unless 'os.fork()' is available and
    the 'forkAfterCGI' parameter is true (it defaults to false), in which
    case the process will fork and finish out one reactor iteration.

    Here's a "dirt simple" CGI/FastCGI script example::

        from peak.running.commands import CGICommand
        from my.app import myAppClass

        myApp = myAppClass()

        sys.exit(
            CGICommand(app=myApp).run()
        )

    Yes, that's the whole script.  'myAppClass' needs to be suitable for
    publishing with the default publication objects, otherwise you need
    a slightly more advanced usage scenario, e.g.::

        sys.exit(
            CGICommand(publisher=myPublisher).run()
        )

    where you've first defined 'myPublisher' as an appropriately tweaked
    'CGIPublisher' object, e.g.::

        from peak.running.commands import CGIPublisher

        myPublisher = CGIPublisher(
            app = myApp,
            httpPubClass = MyHTTPPublicationClass
        )

    See the 'CGIPublisher' class for more info on how to create customized
    'CGIPublisher' instances.  Note that 'CGICommand' only uses the 'app'
    parameter to create a default 'publisher' object; if you supply a
    'publisher', as in the above examples, you do not need to also give
    the 'CGICommand' an 'app'."""

    app          = binding.requireBinding("Application to publish")
    forkAfterCGI = False

    reactor      = binding.bindTo(IBasicReactor)
    newAcceptor  = FastCGIAcceptor

    publisher    = binding.Once(
        lambda self,d,a: CGIPublisher(app = self.app)
    )

    def isFastCGI(self):

        """Check for 'fcgiapp' and whether 'sys.stdin' is a listener socket"""

        try:
            import fcgiapp
        except ImportError:
            return False    # Assume no FastCGI if module not present

        import socket, sys

        for family in (socket.AF_UNIX, socket.AF_INET):
            try:
                s=socket.fromfd(sys.stdin.fileno(),family,socket.SOCK_STREAM)
                s.getsockname()
            except:
                pass
            else:
                return True

        return False

    def detatchAfterCGI(self):

        try:
            from os import fork
        except ImportError:
            # We can't fork; force an immediate shutdown
            self.reactor.stop()
            return

        # Flush output to web server
        self.stdout.flush()
        self.stderr.flush()

        if fork():
            # Parent process; shutdown and exit
            self.reactor.stop()

        else:
            # Child process; close file handles and proceed
            self.stdin.close()
            self.stdout.close()
            self.stderr.close()

            # Schedule to exit after next iteration
            self.reactor.callLater(0, self.reactor.stop)
















    def __setupCGI(self, d, a):

        if self.isFastCGI():

            self.reactor.addReader(
                self.newAcceptor(command=self.publisher)
            )

        else:
            # Setup CGI
            self.reactor.callLater(
                0, self.publisher.run,
                self.stdin, self.stdout, self.stderr, self.environ, self.argv
            )

            if self.forkAfterCGI:
                # Schedule fork
                self.reactor.callLater(0, self.detatchAfterCGI)

            else:
                # Schedule straight shutdown
                self.reactor.callLater(0, self.reactor.stop)


            # Disable the task queue immediately, so that tasks won't run
            # before the main CGI process, but schedule it to be re-enabled
            # afterwards.

            tq = self.lookupComponent(ITaskQueue)
            tq.disable()
            self.reactor.callLater(0, tq.enable)


    __setupCGI = binding.Once(__setupCGI, activateUponAssembly=True)










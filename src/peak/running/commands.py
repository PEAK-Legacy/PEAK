"""Base classes for Main Programs (i.e. processes invoked from the OS)"""

from peak.api import *
from interfaces import *
from peak.util.imports import importObject

__all__ = [
    'AbstractCommand', 'AbstractInterpreter', 'IniInterpreter',
    'ZConfigInterpreter', 'EventDriven', 'CGICommand', 'CGIPublisher',
    'FastCGIAcceptor',
]






























class AbstractCommand(binding.Component):

    """Simple, commandline-driven process"""

    __implements__ = ICmdLineApp

    __class_implements__ = ICmdLineAppFactory

    argv    = binding.bindTo('import:sys:argv')
    stdin   = binding.bindTo('import:sys:stdin')
    stdout  = binding.bindTo('import:sys:stdout')
    stderr  = binding.bindTo('import:sys:stderr')
    environ = binding.bindTo('import:os:environ')

    def run(self):
        raise NotImplementedError

    def getSubcommand(self, cmdFactory, **kw):

        """Return a 'ICmdLineApp' with our environment as its defaults"""

        for k in 'argv stdin stdout stderr environ'.split():
            if k not in kw:
                kw[k]=getattr(self,k)

        if 'parentComponent' not in kw:
            kw['parentComponent'] = self.getCommandParent()

        return cmdFactory(**kw)


    def getCommandParent(self):
        """Get or create a component to be used as the subcommand's parent"""
        # Default is to use the interpreter as the parent
        return self






class AbstractInterpreter(AbstractCommand):

    """Creates and runs a subcommand by interpreting the file in 'argv[1]'"""

    def run(self):
        """Interpret argv[1] and run it as a subcommand"""
        return self.interpret(self.argv[1]).run()


    def interpret(self, filename):
        """Interpret the file and return an application object"""
        raise NotImplementedError


    def getSubcommand(self, cmdFactory, **kw):
        """Same as for AbstractCommand, but with shifted 'argv'"""

        if 'argv' not in kw:
            kw['argv'] = self.argv[1:]

        return super(AbstractInterpreter,self).getSubcommand(cmdFactory, **kw)
        

    def commandName(self,d,a):
        """Basename of the file being interpreted"""
        from os.path import basename
        return basename(self.argv[1])

    commandName = binding.Once(commandName)












class IniInterpreter(AbstractInterpreter):

    """Interpret an '.ini' file as a command-line app"""

    def interpret(self, filename):

        """Interpret file as an '.ini' and run the command it specifies"""

        parent = self.getCommandParent()

        config.loadConfigFile(parent, filename)

        # Set up a command factory based on the configuration setting

        factory = importObject(
            config.getProperty('peak.running.appFactory', parent)
        )

        # Now create and return the subcommand
        return self.getSubcommand(factory,
            parentComponent=parent, componentName = self.commandName
        )



















class ZConfigInterpreter(AbstractInterpreter):

    """Interpret a ZConfig file and run it as a subcommand"""

    appSchema = binding.requireBinding("Schema for the config file")
    
    def interpret(self, filename):
        # XXX this should probably use "PEAK-aware" subclasses of ZConfig
        # XXX preferably that act as child components of this one...
        import ZConfig        
        config, handler = ZConfig.loadConfig(
            self.appSchema, 'file://localhost/%s' % filename
        )    
        return config   # XXX Assume the configured object is a suitable app...



























class EventDriven(AbstractCommand):

    """Run an event-driven main loop after setup"""

    stopAfter = 0
    idleTimeout = 0
    runAtLeast = 0

    handlers = binding.New(list)


    def setup(self, parent=None):
        """Install contents of event loop"""

        for handler in self.handlers:
            handler.setup(self)


    mainLoop = binding.bindTo(IMainLoop)


    def run(self):

        """Perform setup, then run the event loop until done"""

        self.setup()

        self.mainLoop.run(
            self.stopAfter,
            self.idleTimeout,
            self.runAtLeast
        )

        # XXX we should probably log start/stop events







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

    __implements__ = IRerunnable

    app       = binding.requireBinding("Application root to publish")
    publish   = binding.bindTo("import:zope.publisher.publish:publish")

    mkXMLRPC  = binding.bindTo("import:zope.publisher.xmlrpc:XMLRPCRequest")
    mkBrowser = binding.bindTo("import:zope.publisher.browser:BrowserRequest")
    mkHTTP    = binding.bindTo("import:zope.publisher.http:HTTPRequest")

    xmlrpcPubClass  = binding.bindTo("peak.running.zpublish:XMLRPC")
    browserPubClass = binding.bindTo("peak.running.zpublish:Browser")
    httpPubClass    = binding.bindTo("peak.running.zpublish:HTTP")

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






class FastCGIAcceptor(binding.Base):

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
            self.handler(i,o,e,env)

        finally:
            self.finish()
            self.ping()











class CGICommand(EventDriven):

    """Run CGI/FastCGI in an event-driven loop

    If the 'fcgiapp' module is available and 'sys.stdin' is a socket, this
    command will listen for FastCGI connections and process them as they
    arrive.  Otherwise, it will assume that it is being run as a CGI, and
    use its environment attributes as the environment for the CGI command.

    If running in CGI mode, a 'CGICommand' will exit its reactor loop at
    the earliest possible moment after the request is served, unless its
    'exitAfterCGI' flag is set to False (in which case the normal
    'EventDriven' command parameters will apply, as they do in FastCGI mode).

    Note that "earliest possible moment" means "after any events which were
    scheduled to execute before the 'CGICommand' finished executing.  This
    means that you can use 'reactor.callLater(0,aCallable)' to schedule
    events which will happen after the CGI command is finished, but before
    the script executes.

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
    exitAfterCGI = True
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

        return not fcgiapp.isCGI()


    def scheduleShutdown(self):
        # Schedule reactor to shutdown on subsequent iteration
        self.reactor.callLater(0, self.reactor.stop)


    def setup(self, parent=None):

        if self.isFastCGI():

            self.reactor.addReader(
                self.newAcceptor(command=self.publisher)
            )

        else:
            self.reactor.callLater(
                0, self.publisher.run,
                self.stdin, self.stdout, self.stderr, self.environ, self.argv
            )
            if self.exitAfterCGI:

                # schedule ourselves to schedule a shutdown; doing it in
                # two steps ensures that events scheduled during the CGI
                # for execution immediately after it have a chance to
                # be processed.

                self.reactor.callLater(0, self.scheduleShutdown)


        # Any periodic tasks, etc., should be scheduled for *after* the
        # main CGI process, if applicable.  Note that this arrangement
        # can still put them ahead of I/O checking, because reactors process
        # events before they go into their I/O loops.  However, for
        # PEAK 'IPeriodicTask' objects this isn't an issue because 'TaskQueue'
        # forward-schedules itself to execute the tasks.  This means that,
        # for a reasonable 'time()'-granularity, it shouldn't be possible for
        # a periodic task to get executed before the first 'select()' occurs,
        # although that 'select()' may be arbitrarily brief.  In effect,
        # 'callLater(0,...)' can only schedule things to occur on the *next*
        # iteration of the event loop, and since 'TaskQueue' uses this to
        # schedule its task execution, it is thus guaranteed that tasks will
        # not execute until the next iteration...  provided that 'time()'
        # has adequate resolution (i.e., you're not on Windows).

        super(CGICommand, self).setup(parent)
























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







_browser_methods = 'GET', 'POST', 'HEAD'

class CGIPublisher(binding.Component):

    """Use 'zope.publisher' to run an application as CGI/FastCGI"""

    __implements__ = IRerunnable

    XMLRPC  = binding.bindTo("import:zope.publisher.xmlrpc:XMLRPCRequest")
    Browser = binding.bindTo("import:zope.publisher.browser:BrowserRequest")
    HTTP    = binding.bindTo("import:zope.publisher.http:HTTPRequest")

    publish = binding.bindTo("import:zope.publisher.publish:publish")

    xmlrpcPublication  = binding.requireBinding("IPublication for XMLRPC")
    browserPublication = binding.requireBinding("IPublication for Browser")
    httpPublication    = binding.requireBinding("IPublication for HTTP")


    def run(self, input, output, errors, environ, argv=[]):

        """Process one request"""

        method = env.get('REQUEST_METHOD', 'GET').upper()

        if method in _browser_methods:
            if (method == 'POST' and
                env.get('CONTENT_TYPE', '').lower().startswith('text/xml')
                ):
                request = self.XMLRPC(input, output, env)
                request.setPublication(self.xmlrpcPublication)
            else:
                request = self.Browser(input, output, env)
                request.setPublication(self.browserPublication)
        else:
            request = self.HTTP(input, output, env)
            request.setPublication(self.httpPublication)
        
        return self.publish(request)


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

    """Run CGI/FastCGI in an event-driven loop"""

    reactor = binding.bindTo(IBasicReactor)

    command = binding.requireBinding("An IRerunnable command")

    newAcceptor = FastCGIAcceptor


    def isFastCGI(self):

        try:
            import fcgiapp
        except ImportError:
            return False    # Assume no FastCGI if module not present

        return not fcgiapp.isCGI()


    def setup(self, parent=None):

        super(CGICommand, self).setup(parent)

        if self.isFastCGI():

            self.reactor.addReader(
                self.newAcceptor(command=self.command)
            )

        else:
            self.reactor.callLater(
                0, self.command.run,
                self.stdin, self.stdout, self.stderr, self.environ, self.argv
            )


























"""Base classes for Main Programs (i.e. processes invoked from the OS)"""

from peak.api import *
from interfaces import *
from peak.util.imports import importObject
from os.path import isfile
import sys, os
from types import ClassType, FunctionType

__all__ = [
    'AbstractCommand', 'AbstractInterpreter', 'IniInterpreter', 'EventDriven',
    'ZConfigInterpreter', 'Bootstrap', 'rerunnableAsFactory',
    'callableAsFactory', 'appAsFactory', 'InvocationError',
]


class InvocationError(Exception):
    """Problem with command arguments or environment"""























class AbstractCommand(binding.Component):

    """Simple, commandline-driven process"""

    protocols.advise(
        instancesProvide = [ICmdLineApp],
        classProvides    = [ICmdLineAppFactory]
    )

    argv    = binding.bindTo('import:sys:argv')
    stdin   = binding.bindTo('import:sys:stdin')
    stdout  = binding.bindTo('import:sys:stdout')
    stderr  = binding.bindTo('import:sys:stderr')
    environ = binding.bindTo('import:os:environ')

    def run(self):
        raise NotImplementedError


    usage = """
Either this is an abstract command class, or somebody forgot to
define a usage message for their subclass.
"""

    def showHelp(self):
        """Display usage message on stderr"""
        print >>self.stderr, self.usage
        return 0


    def isInteractive(self, d, a):
        """True if 'stdin' is a terminal"""
        try:
            isatty = self.stdin.isatty
        except AttributeError:
            return False
        else:
            return isatty()

    isInteractive = binding.Once(isInteractive)

    def getSubcommand(self, executable, **kw):

        """Return a 'ICmdLineApp' with our environment as its defaults

        Any 'IExecutable' may be supplied as the basis for creating
        the 'ICmdLineApp'.  'NotImplementedError' is raised if the
        supplied object is not an 'IExecutable'.
        """

        factory = adapt(executable,ICmdLineAppFactory)

        for k in 'argv stdin stdout stderr environ'.split():
            if k not in kw:
                kw[k]=getattr(self,k)

        if 'parentComponent' not in kw:
            kw['parentComponent'] = self.getCommandParent()

        return factory(**kw)


    def invocationError(self, msg):

        """Write msg and usage to stderr if interactive, otherwise re-raise"""

        if self.isInteractive:
            self.showHelp()
            print >>self.stderr, '\n%s: %s\n' % (self.argv[0], msg)
            # XXX output last traceback frame?
            return 1    # exit errorlevel
        else:
            raise


    def getCommandParent(self):
        """Get or create a component to be used as the subcommand's parent"""
        # Default is to use the interpreter as the parent
        return self



class AbstractInterpreter(AbstractCommand):

    """Creates and runs a subcommand by interpreting the file in 'argv[1]'"""

    def run(self):
        """Interpret argv[1] and run it as a subcommand"""
        try:
            if len(self.argv)<2:
                raise InvocationError("missing argument(s)")
            return self.interpret(self.argv[1]).run()

        except SystemExit, v:
            return v.args[0]

        except InvocationError, msg:
            return self.invocationError(msg)


    def interpret(self, filename):
        """Interpret the file and return an application object"""
        raise NotImplementedError


    def getSubcommand(self, executable, **kw):
        """Same as for AbstractCommand, but with shifted 'argv'"""

        if 'argv' not in kw:
            kw['argv'] = self.argv[1:]

        return super(AbstractInterpreter,self).getSubcommand(executable, **kw)


    def commandName(self,d,a):
        """Basename of the file being interpreted"""
        from os.path import basename
        return basename(self.argv[1])

    commandName = binding.Once(commandName)



class IniInterpreter(AbstractInterpreter):

    """Interpret an '.ini' file as a command-line app

    The supplied '.ini' file must supply a 'running.IExecutable' as the
    value of its 'peak.running.app' property.  The supplied 'IExecutable'
    will be run with the remaining command line arguments."""

    def interpret(self, filename):

        """Interpret file as an '.ini' and run the command it specifies"""

        if not isfile(filename):
            raise InvocationError("Not a file:", filename)

        parent = self.getCommandParent()

        config.loadConfigFile(parent, filename)

        # Set up a command factory based on the configuration setting

        executable = importObject(
            config.getProperty(parent, 'peak.running.app', None)
        )

        if executable is None:
            raise InvocationError(
                "%s doesn't specify a 'peak.running.app'"% filename
            )

        # Now create and return the subcommand
        return self.getSubcommand(executable,
            parentComponent=parent, componentName = self.commandName
        )







    usage="""
Usage: peak runIni CONFIG_FILE arguments...

CONFIG_FILE should be a file in the format used by 'peak.ini'.  (Note that
it does not have to be named with an '.ini' extension.)  The file should
define a 'running.IExecutable' for the value of its 'peak.running.app'
property.  The specified 'IExecutable' will then be run with the remaining
command-line arguments.
"""



class ZConfigInterpreter(AbstractInterpreter):

    """Load a ZConfig schema and run it as a sub-interpreter"""

    def interpret(self, filename):

        from peak.naming.factories.openable import FileURL
        from peak.config.load_zconfig import SchemaLoader

        url = naming.toName(filename, FileURL.mdl_fromString)

        return self.getSubcommand(
            naming.lookup(self, url,
                objectFactories = [SchemaLoader(self)]
            )
        )













class CallableAsCommand(AbstractCommand):

    """Adapts callables to 'ICmdLineApp'"""

    invoke = binding.requireBinding("Any callable")

    def run(self):

        old = sys.stdin, sys.stdout, sys.stderr, os.environ, sys.argv

        try:
            # Set the global environment to our local environment
            for v in 'stdin stdout stderr argv'.split():
                setattr(sys,v,getattr(self,v))

            os.environ = self.environ
            try:
                return self.invoke()
            except SystemExit, v:
                return v.args[0]

        finally:
            # Ensure it's back to normal when we leave
            sys.stdin, sys.stdout, sys.stderr, os.environ, sys.argv = old


class RerunnableAsCommand(AbstractCommand):

    """Adapts 'IRerunnable' to 'ICmdLineApp'"""

    runnable = binding.requireBinding("An IRerunnable")

    def run(self):
        try:
            return self.runnable.run(
                self.stdin, self.stdout, self.stderr, self.environ, self.argv
            )
        except SystemExit, v:
            return v.args[0]


def callableAsFactory(ob,proto=None):

    """Convert a callable object to an 'ICmdLineAppFactory'"""

    if not callable(ob):
        raise NotImplementedError("Object must be callable",ob)

    def factory(**kw):
        kw.setdefault('invoke',ob)
        return CallableAsCommand(**kw)

    protocols.adviseObject(factory, provides=[ICmdLineAppFactory])
    return factory

def appAsFactory(app,proto=None):

    """Convert an 'ICmdLineApp' to an 'ICmdLineAppFactory'"""

    def factory(**kw):
        kw.setdefault('invoke',app.run)
        return CallableAsCommand(**kw)

    protocols.adviseObject(factory, provides=[ICmdLineAppFactory])
    return factory

def rerunnableAsFactory(runnable,proto=None):

    """Convert an 'IRerunnable' to an 'ICmdLineAppFactory'"""

    def factory(**kw):
        kw.setdefault('runnable',runnable)
        return RerunnableAsCommand(**kw)

    protocols.adviseObject(factory, provides=[ICmdLineAppFactory])
    return factory






protocols.declareAdapter(
    callableAsFactory,
    provides=[ICmdLineAppFactory],
    forTypes=[object]
)

protocols.declareAdapter(
    appAsFactory,
    provides=[ICmdLineAppFactory],
    forProtocols=[ICmdLineApp]
)

protocols.declareAdapter(
    rerunnableAsFactory,
    provides=[ICmdLineAppFactory],
    forProtocols=[IRerunnable]
)
























class TestRunner(CallableAsCommand):

    defaultTest = 'peak.tests.test_suite'
    testModule  = None

    def invoke(self):

        from unittest import main

        main(
            module = self.testModule,
            argv = self.argv,
            defaultTest = self.defaultTest
        )

        return 0

























class Bootstrap(AbstractInterpreter):

    """Invoke and use an arbitrary 'IExecutable' object

    This class is designed to allow specification of an arbitrary
    name or URL on the command line to retrieve and invoke the
    designated object.

    If the name is not a scheme-prefixed URL, it is first converted to
    a name in the 'peak.running.shortcuts' configuration property namespace,
    thus allowing simpler names to be used.  For example, 'runIni' is a
    shortcut for '"import:peak.running.commands:IniInterpreter"'.  If you
    use a sitewide PEAK_CONFIG file, you can add your own shortcuts to
    the 'peak.running.shortcuts' namespace.  (See the 'peak.ini' file for
    current shortcuts, and examples of how to define them.)

    The object designated by the name or URL in 'argv[1]' must be an
    'IExecutable'; that is to say it must implement one of the 'IExecutable'
    sub-interfaces, or else be callable without arguments.  (See the
    'running.IExecutable' interface for more details.)

    Here's an example bootstrap script (which is installed as the 'peak'
    script by the PEAK distribution on 'posix' operating systems)::

        #!/usr/bin/env python2.2

        from peak.running.commands import Bootstrap
        from peak.api import config
        import sys

        sys.exit(
            Bootstrap(
                config.makeRoot()
            ).run()
        )

    The script above will look up its first supplied command line argument,
    and then invoke the found object as a command, supplying the remaining
    command line arguments.
    """

    def interpret(self, name):

        if not naming.URLMatch(name):
            name = "config:peak.running.shortcuts.%s/" % name

        try:
            factory = self.lookupComponent(name)
        except exceptions.NameNotFound, v:
            raise InvocationError("Name not found: %s" % v)

        try:
            return self.getSubcommand(factory)

        except NotImplementedError:
            raise InvocationError(
                "Invalid command object", factory, "found at", name
            )
























    usage = """
Usage: peak NAME_OR_URL arguments...

The 'peak' script bootstraps and runs a specified command object or command
class.  The NAME_OR_URL argument may be a shortcut name defined in the
'peak.running.shortcuts' property namespace, or a URL of a type
supported by 'peak.naming'.  For example, if you have a class 'MyAppClass'
defined in 'MyPackage', you can use:

    peak import:MyPackage.MyAppClass

to invoke it.  Arguments to the found object are shifted left one position,
so in the example above it will see 'import:MyPackage.MyAppClass' as its
'argv[0]'.

The named object must implement one of the 'peak.running' command interfaces,
or be callable.  See the 'Bootstrap' class in 'peak.running.commands' for
more details on creating command objects for use with 'peak'.  For the
list of available shortcut names, see '%s'""" % config.fileNearModule(
        'peak','peak.ini'
    )

    if 'PEAK_CONFIG' in os.environ:
        usage += " and '%s'" % os.environ['PEAK_CONFIG']

    usage += ".\n"















class EventDriven(AbstractCommand):

    """Run an event-driven main loop after setup"""

    stopAfter   = binding.bindToProperty('peak.running.stopAfter',   0)
    idleTimeout = binding.bindToProperty('peak.running.idleTimeout', 0)
    runAtLeast  = binding.bindToProperty('peak.running.runAtLeast',  0)

    mainLoop = binding.bindTo(IMainLoop)


    def run(self):

        """Perform setup, then run the event loop until done"""

        self.mainLoop.run(
            self.stopAfter,
            self.idleTimeout,
            self.runAtLeast
        )

        # XXX we should probably log start/stop events




















"""Base classes for Main Programs (i.e. processes invoked from the OS)"""

from peak.api import *
from interfaces import *
from peak.util.imports import importObject

__all__ = [
    'AbstractCommand', 'AbstractInterpreter', 'IniInterpreter',
    'ZConfigInterpreter', 'curriedFactory',
]


def curriedFactory(__factory, parentComponent=None, componentName=None, **kw):

    """Preset parameters for an 'ICmdLineAppFactory' as a curried function"""

    def factory(parentComponent=parentComponent, componentName=componentName,
        **kwargs):
            k = kw.copy(); k.update(kwargs)
            return __factory(parent,name,**k)

    return factory



















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

    def presetFactory(self, cmdFactory, **kw):

        """Return a 'ICmdLineAppFactory' with our environment as its defaults"""

        return curriedFactory(
            cmdFactory,
            argv = self.argv,
            stdin = self.stdin,
            stdout = self.stdout,
            stderr = self.stderr,
            environ = self.environ,
            **kw
        )











class AbstractInterpreter(AbstractCommand):

    """Creates and runs a subcommand by interpreting the file in 'argv[1]'"""

    def run(self):
        """Interpret argv[1] and run it as a subcommand"""
        return self.interpret(self.argv[1]).run()


    def interpret(self, filename):
        """Interpret the file and return an application object"""
        raise NotImplementedError


    def presetFactory(self, cmdFactory):
        """Same as for AbstractCommand, but with shifted 'argv'"""
        factory = super(AbstractInterpreter,self).presetFactory(cmdFactory)
        return curriedFactory(factory, argv = self.argv[1:])


    def commandName(self,d,a):
        """Basename of the file being interpreted"""
        from os.path import basename
        return basename(self.argv[1])

    commandName = binding.Once(commandName)


    def getCommandParent(self):
        """Get or create a component to be used as the subcommand's parent"""
        # Default is to use the interpreter as the parent
        return self


    def getFactoryArgs(self):
        """Get additional keyword args for calling the subcommand factory"""
        # Default is to set 'componentName' to the basename of the launched file
        return {'componentName': self.commandName}



class IniInterpreter(AbstractInterpreter):

    """Interpret an '.ini' file as a command-line app"""

    def interpret(self, filename):

        """Interpret file as an '.ini' and run the command it specifies"""

        parent = self.getCommandParent()
        config.loadConfigFile(parent, filename)

        # Set up a command factory based on the configuration setting

        factory = self.presetFactory(
            importObject(
                config.getProperty('peak.running.appFactory', parent)
            )
        )

        # Now create and return the subcommand
        return factory(parentComponent=parent, **self.getFactoryArgs())



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




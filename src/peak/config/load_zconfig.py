from peak.api import *
import ZConfig.loader
from peak.running.commands import AbstractInterpreter
from peak.naming.factories.openable import FileURL

class BaseLoader(binding.Component, ZConfig.loader.BaseLoader):

    def openResource(self, url):
        url = str(url)
        try:
            factory = naming.lookup(self, url)
            file = factory.open('t')
        except (IOError, OSError), e:
            # Python 2.1 raises a different error from Python 2.2+,
            # so we catch both to make sure we detect the situation.
            error = ZConfig.ConfigurationError("error opening resource %s: %s"
                                               % (url, str(e)))
            error.url = url
            raise error
        return self.createResource(file, url)


    def normalizeURL(self, url):
        url = naming.parseURL(self, url)
        if getattr(url,'fragment',None) is not None:
            raise ZConfig.ConfigurationError(
                "fragment identifiers are not supported")
        return str(url)













class SchemaLoader(BaseLoader, ZConfig.loader.SchemaLoader):

    protocols.advise(
        instancesProvide = [naming.IObjectFactory]
    )

    registry = binding.New(ZConfig.datatypes.Registry)
    _cache   = binding.New(dict)
    __init__ = binding.Component.__init__.im_func

    def getObjectInstance(self, context, refInfo, name, attrs=None):
        ob = adapt(refInfo, naming.IStreamAddress, None)
        if ob is not None:
            ob = ob.getObjectInstance(context, refInfo, name, attrs=None)
            return ConfigLoader(
                context.creationParent, context.creationName,
                schema = self.loadFile(ob.open('t'), str(refInfo))
            )























class ConfigLoader(AbstractInterpreter,BaseLoader,ZConfig.loader.ConfigLoader):

    """Combination config-file loader and interpreter"""

    protocols.advise(
        instancesProvide = [naming.IObjectFactory]
    )

    usage="""
Usage: peak SCHEMA_URL ZCONFIG_FILE arguments...

SCHEMA_URL should be a 'zconfig.schema:' URL referring to the schema used
for the config file.  ZCONFIG_FILE should be the URL of a ZConfig configuration
file that follows the schema specified by SCHEMA_URL.  The object that results
from loading ZCONFIG_FILE should implement or be adaptable to
to 'running.ICmdLineAppFactory'.  It will be run with the remaining
command-line arguments.
"""

    schema = binding.requireBinding("ZConfig schema to use")

    def getObjectInstance(self, context, refInfo, name, attrs=None):
        ob = adapt(refInfo, naming.IStreamAddress, None)
        if ob is not None:
            ob = ob.getObjectInstance(context, refInfo, name, attrs=None)
            component = self.loadFile(ob.open('t'), str(refInfo))
            binding.suggestParentComponent(
                context.creationParent, context.creationName,
                component
            )
            return component

    def interpret(self, filename):
        url = naming.toName(filename, FileURL.fromFilename)
        ob, handler = naming.lookup(self, url, objectFactories=[self])
        return self.getSubcommand(ob)





class ZConfigSchemaURL(naming.URL.Base):

    """'zconfig.schema:' URL scheme - loads body as a schema

    Note that the body of this URL can be any other type of URL, but
    if no URL scheme is present in the body, then the body is interpreted
    as a 'file:' URL.
    """

    supportedSchemes = 'zconfig.schema',

    def getObjectInstance(self, context, refInfo, name, attrs=None):

        url = naming.toName(self.body, FileURL.mdl_fromString)

        return naming.lookup(context, url,
            creationParent = context.creationParent,
            creationName = context.creationName,
            objectFactories = [SchemaLoader(context.creationParent)]
        )





















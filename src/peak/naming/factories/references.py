from peak.core import *
from peak.util.imports import importObject

class refURL(naming.URL.Base):

    """URL that's a 'naming.IReference'"""
    
    protocols.advise(
        instancesProvide=[naming.IReference]
    )
    
    supportedSchemes = ('ref', )

    class factoryName(naming.URL.Field):
        pass

    class addresses(naming.URL.Collection):
        pass

    syntax = naming.URL.Sequence(
        factoryName, '@', addresses
    )

    def restore(self, context, name):
        factory = importObject(
            naming.FACTORY_PREFIX.of(context)[self.factoryName]
        )
        factory = adapt(factory, naming.IObjectFactory)
        return factory.getObjectInstance(context, self, name)



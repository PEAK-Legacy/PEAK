"""Service Provider Interface

    Core functions for implementing naming services.  These are 
    Pythonic adaptations of some of the static methods provided by
    'NamingManager' and 'DirectoryManager' in the JNDI 'javax.naming.spi'
    package.  For Python, it makes more sense to have these as
    module-level functions than as static methods of classes.

    Note that if you just want to *use* naming services, you don't need
    to worry about this.  This basically just implements a few simple
    "policy" methods that control how initial context and URL context
    objects are created, based on component properties.
"""

from peak.util.imports import importObject

from interfaces import *
from properties import *

from names import NNS_Reference


__all__ = [
    'getInitialContext', 'getURLContext',
]


__implements__ = (
    IURLContextFactory, IInitialContextFactory, IObjectFactory
)











def getInitialContext(parentComponent=None, **options):

    """Return an initial context using supplied parent and options

    The initial context created is determined by asking the supplied
    'parentComponent' to the factory found by looking up the
    'peak.naming.initialContextFactory' property (available as the
    constant 'naming.INIT_CTX_FACTORY').  Keyword options are also
    passed through to the actual factory.

    If no 'parentComponent' is supplied, the new initial context will
    be a root component, and acquire its configuration options from a
    default local configuration object.
    """

    factory = importObject( INIT_CTX_FACTORY(parentComponent) )
    return factory(parentComponent, **options)
























def getURLContext(scheme, context=None, iface=IBasicContext):

    """Return a 'Context' object for the given URL scheme and interface."""

    factory = SCHEMES_PREFIX.of(context)[scheme]

    if factory is not None:

        factory = importObject(factory)
    
        if IURLContextFactory.isImplementedBy(factory):
            return factory.getURLContext(scheme, context, iface)

        elif iface.isImplementedByInstancesOf(factory):
            return factory(context)

        elif IAddress.isImplementedByInstancesOf(factory):
            from contexts import GenericURLContext
            return GenericURLContext(context, schemeParser=factory)

    return None



def getObjectInstance(refInfo, name, context, attrs=None):

    """Default rules for loading objects from state"""

    if IAddress.isImplementedBy(refInfo):
        return refInfo.retrieve(refInfo, name, context, attrs)

    elif isinstance(refInfo, NNS_Reference):
        # default is to treat the object as its own NNS
        return refInfo.relativeTo


















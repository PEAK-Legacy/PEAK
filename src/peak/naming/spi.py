"""Service Provider Interface

    Core functions for implementing naming services.  These are mostly
    Pythonic adaptations of some of the static methods provided by
    'NamingManager' and 'DirectoryManager' in the JNDI 'javax.naming.spi'
    package.  For Python, it makes more sense to have these as
    module-level functions than as static methods of classes.

    Note that if you just want to *use* naming services, you can stay
    completely away from this module.  Even if you are implementing a
    naming service, chances are good that you don't need to know a lot
    about the stuff in here.  Which is a good thing, because there are
    so many levels of indirection here that it can make your head spin!
"""

from peak.binding.components import findUtilities, findUtility, Provider
from peak.binding.imports import importObject
from peak.api import config

from interfaces import *
from references import *
from names import *
from properties import *


__all__ = [
    'getInitialContext',
    'getObjectInstance', 
    'getStateToBind', 
    'getURLContext',
]

__implements__ = (
    IURLContextFactory, IInitialContextFactory
)






def getInitialContext(parentComponent=None, **options):

    """Return an initial context using supplied parent and options

    The initial context created is determined by asking the supplied
    'parentComponent' for an 'IInitialContextFactory' utility.  Keyword
    options are passed through to the actual factory.

    If no 'parentComponent' is supplied, the new initial context will
    be a root component, and acquire its configuration options from a
    default local configuration object.
    """

    factory = findUtility(parentComponent, IInitialContextFactory)

    return factory.getInitialContext(parentComponent, **options)

























def getURLContext(scheme, context, iface=IBasicContext):

    """Return a 'Context' object for the given URL scheme and interface."""

    factory = config.getProperty(context, SCHEMES_PREFIX+scheme, None)

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


















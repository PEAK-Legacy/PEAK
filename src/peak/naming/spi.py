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

from peak.binding.imports import importObject, importSequence


from interfaces import *
from references import *
from names import *

import factories

__all__ = [
    'getInitialContext',
    'getObjectInstance', 
    'getStateToBind', 
    'getURLContext',
]

__implements__ = (
    IObjectFactory, IStateFactory, IURLContextFactory, IInitialContextFactory
)



    



def getInitialContext(parentComponent=None, **options):

    """Return an initial context using supplied parent and options

    The initial context created is determined by asking the supplied
    'parentComponent' for an 'IInitialContextFactory' utility.  If no
    'parentComponent' is supplied, a default parent will be created via
    'config.newDefaultConfig()'.  Keyword options are passed through to
    the actual factory."""

    if parentComponent is None:
        from peak.api import config
        parentComponent = config.newDefaultConfig()
        saveConfig = True
    else:
        saveConfig = False
  
    factory = parentComponent.acquireUtility(IInitialContextFactory)
    if factory is None: factory = factories

    context = factory.getInitialContext(parentComponent,**options)

    if saveConfig:
        config.setLocal(context, parentComponent)
        
    return context















def getStateToBind(obj, name, context, attrs=None):

    if IReferenceable.isImplementedBy(obj):
        return (obj.getReference(obj), attrs)

    factory = context.acquireUtility(IStateFactory)
    if factory is None: factory = factories

    if factory is not None:

        result = factory.getStateToBind(
            obj, name, context, attrs
        )

        if result is not None:
            return result

    return obj, attrs


def getObjectInstance(refInfo, name, context, attrs=None):

    if isinstance(refInfo,LinkRef):
        return context[refInfo.linkName]

    factory = context.acquireUtility(IObjectFactory)
    if factory is None: factory = factories

    if factory is not None:

        result = factory.getObjectInstance(
            refInfo, name, context, attrs
        )

        if result is not None:
            return result                      

    return refInfo



def getURLContext(scheme, context, iface=IBasicContext):

    """Return a 'Context' object for the given URL scheme and interface."""

    factory = context.acquireUtility(IURLContextFactory)
    if factory is None: factory = factories

    if factory is not None:

        context = factory.getURLContext(scheme, context, iface)

        if context is not None:
            return context



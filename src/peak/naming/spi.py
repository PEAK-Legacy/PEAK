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

from peak.util.Import import interpretSpec, interpretSequence


from interfaces import *
from names import *

import factories

__all__ = [
    'getInitialContext',
    'getObjectInstance', 
    'getStateToBind', 
    'getURLContext',
]

__implements__ = IObjectFactory, IStateFactory, IURLContextFactory

defaultFactories = factories,

    






def getInitialContext(environ={}):

    """Return an initial context using the specified environment properties

    If the 'environ' mapping contains a 'NAMING_INITIAL_CONTEXT_FACTORY'
    entry, it will be used as the class for the returned context.  The
    entry can be either an import string, or an actual class or factory
    object.

    If the 'environ' does not contain a suitable entry, a default
    implementation ('peak.naming.providers.Initial:DefaultInitialContext')
    is used."""
    
    factory = interpretSpec(
        environ.get(
            'NAMING_INITIAL_CONTEXT_FACTORY',
            'peak.naming.providers.Initial:DefaultInitialContext'
        )
    )

    return factory(environ)




















def getStateToBind(obj, name, context, environment, attrs=None):

    if IReferenceable.isImplementedBy(obj):
        return (obj.getReference(obj), attrs)

    for factory in interpretSequence(
            environment.get(
                'NAMING_STATE_FACTORIES', defaultFactories
            ) 
        ):

        result = factory.getStateToBind(
            obj, name, context, environment, attrs
        )

        if result is not None:
            return result

    return obj,attrs






















def getObjectInstance(refInfo, name, context, environment, attrs=None):

    if isinstance(refInfo,LinkRef):
        return context[refInfo.linkName]

    if isinstance(refInfo,Reference):

        factory = getattr(refInfo,'objectFactory',None)

        if factory:
            factory = interpretSpec(factory)
            return factory.getObjectInstance(refInfo, name, context, environment, attrs)
        
        else:
            for addr in refInfo:
                if addr.type=='URL':
                    url = toName(addr.content,acceptURL=1)
                    ctx = getURLContext(url.scheme, context, environment)
                    if ctx is not None:
                        try:
                            return ctx[url]
                        except NameNotFoundException:
                            pass

    for factory in interpretSequence(
            environment.get(
                'NAMING_OBJECT_FACTORIES', defaultFactories
            ) 
        ):

        result = factory.getObjectInstance(
            refInfo, name, context, environment, attrs
        )

        if result is not None:
            return result                      

    return refInfo



def getURLContext(scheme, context=None, environ=None, iface=IBasicContext):

    """Return a 'Context' object for the given URL scheme and interface.

    This works by walking the list of context factory objects supplied in
    the 'NAMING_URL_CONTEXT_FACTORIES' environment entry, and asking each
    one for an initial context that supports the specified 'scheme'.  If no
    'NAMING_URL_CONTEXT_FACTORIES' entry is supplied, the default factory
    is the 'peak.naming.factories:getURLContext()' function.  (See the
    'peak.naming.factories' package for more information on the default lookup
    policy.)

    Each context factory in the context factory list must be a callable with
    the signature 'factory.getURLContext(scheme,ctx,environ,iface)', returning
    a context which supports the specified naming 'scheme', with 'environ' as
    its environment, 'ctx' as its relative context (if applicable), and
    'iface' as a supported context interface.
    """

    if environ is None:
        if context is None:
            environ = {}
        else:
            environ = context.getEnvironment()

    for contextFactory in interpretSequence(
            environ.get(
                'NAMING_URL_CONTEXT_FACTORIES', defaultFactories
            ) 
        ):

        context = contextFactory.getURLContext(scheme, context, environ, iface)

        if context is not None:
            return context


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

from TW.Utils.Import import interpretSpec, interpretSequence


from Interfaces import *

__all__ = [
    'getInitialContext',
    'getObjectInstance', 
    'getStateToBind', 
    'getURLContext',
    'getContinuationContext',
]




    









def getInitialContext(environ={}):

    """Return an initial context using the specified environment properties

    If the 'environ' mapping contains a 'NAMING_INITIAL_CONTEXT_FACTORY'
    entry, it will be used as the class for the returned context.  The
    entry can be either an import string, or an actual class or factory
    object.

    If the 'environ' does not contain a suitable entry, a default
    implementation ('TW.Naming.InitialContext.DefaultInitialContext')
    is used."""
    
    factory = interpretSpec(
        environ.get(
            'NAMING_INITIAL_CONTEXT_FACTORY',
            'TW.Naming.Contexts:DefaultInitialContext'
        )
    )

    return factory(environ)




















def getContinuationContext(cpe):

    opInterface = cpe.requiredInterface or IBasicContext

    if opInterface.isImplementedBy(cpe.resolvedObj):
        return cpe.resolvedObj

    cctx = getObjectInstance(
        cpe.resolvedObj,
        cpe.altName,
        cpe.altNameCtx,
        cpe.environment
    )

    if opInterface.isImplementedBy(cctx):
        return cctx

    elif IResolver.isImplementedBy(cctx):
        cctx, cpe.remainingName = cctx.resolveToInterface(
            cpe.remainingName, opInterface
        )
        return cctx
        
    else:
        raise NotContextException(
            "Continuation object does not support required interface",
            opInterface, resolvedObj=cctx, rootException=cpe
        )

    

def getStateToBind(obj, name, context, environment, attrs=None):
    pass    # XXX

def getObjectInstance(refInfo, name, context, environment, attrs=None):
    pass    # XXX





def getURLContext(scheme, context=None, environ=None, iface=IBasicContext):

    """Return a 'Context' object for the given URL scheme and interface.

    This works by walking the list of context factory objects supplied in
    the 'NAMING_SCHEME_CONTEXT_FACTORIES' environment entry, and asking each
    one for an initial context that supports the specified 'scheme'.  If no
    'NAMING_SCHEME_CONTEXT_FACTORIES' entry is supplied, the default factory
    is the 'TW.Naming.Schemes:getURLContext()' function.  (See the 'Schemes'
    package for more information on the default lookup policy.)

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
                'NAMING_SCHEME_CONTEXT_FACTORIES',
                'TW.Naming.Schemes'
            ) 
        ):

        context = contextFactory.getURLContext(scheme, context, environ, iface)

        if context is not None:
            return context


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
from TW.Utils.EigenData import EigenCell

__all__ = [
    'getInitialContext',         'setInitialContextHook',
    'getInitialContext_default', 'getURLContext'
]


_initialContextHook = EigenCell()

    














def getInitialContext_default(environ={}):

    """Return an initial context using the specified environment properties

    If the 'environ' mapping contains a 'NAMING_INITIAL_CONTEXT_FACTORY'
    entry, it will be used as the class for the returned context.  The
    entry can be either an import string, or an actual class or factory
    object.

    If the 'environ' does not contain a suitable entry, a default
    implementation ('TW.Naming.InitialContext.DefaultInitialContext')
    is used.

    This function is here for the convenience of those writing initial
    context hooks which need to wrap this default policy in some way.
    You should not normally call this function directly.  Use
    'getInitialContext()' instead."""
    
    factory = interpretSpec(
        environ.get(
            'NAMING_INITIAL_CONTEXT_FACTORY',
            'TW.Naming.InitialContext:DefaultInitialContext'
        )
    )

    return factory(environ)















_initialContextHook.set(getInitialContext_default)


def getInitialContext(environ={}):

    """Return an initial context using the specified environment properties

    This function invokes either the installed initial context hook, or
    the default creation policy ('getInitialContext_default()').
    """

    return _initialContextHook.get()(environ)


def setInitialContextHook(callable):

    """Set the initial context creation hook to 'callable'

        The initial context hook is a callable which is passed a single
        mapping object to be used as an environment, and must return an
        object supporting the 'TW.Naming.Context' interface.  This hook
        will effectively be used in place of the standard
        'getInitialContext()' function.

        The initial context hook may be set as many times as you like,
        but as soon as it has been used to create an initial context, 
        further attempts to set the hook will raise an exception.  You
        should only set the initial context if hook you need to globally
        override the normal policy for creating an initial context.

        This function is the Pythonic equivalent of JNDI's
        'setInitialContextFactoryBuilder', in case you were wondering.  It's
        amazing sometimes how much overhead it can take in Java to do
        something that's trivial in Python.
    """

    _initialContextHook.set(callable)




def getURLContext(scheme, environ={}):

    """Return a 'Context' object for the given URL scheme and interface.

    This works by walking the list of context factory functions supplied in
    the 'NAMING_SCHEME_CONTEXT_FACTORIES' environment entry, and asking each
    one for an initial context that supports the specified 'scheme'.  If no
    'NAMING_SCHEME_CONTEXT_FACTORIES' entry is supplied, the default factory
    is the 'TW.Naming.Schemes:getURLContext()' function.  (See the 'Schemes'
    package for more information on the default lookup policy.)

    Each context factory in the context factory list must be a callable with
    the signature 'factory(scheme,environ)', returning an initial context
    which supports the specified naming 'scheme', with 'environ' as its
    environment.
    """

    for contextFactory in interpretSequence(
            environ.get(
                'NAMING_SCHEME_CONTEXT_FACTORIES',
                'TW.Naming.Schemes:getURLContext'
            ) 
        ):

        context = contextFactory(scheme, environ)

        if context is not None and context is not environ:
            return context


"""Functions directly usable from the TW.Naming package"""

__all__ = ['getInitialContext', 'lookup', 'parseName']


def getInitialContext(environ=None, **kw):

    """Get an initial naming context, based on 'environ' and keyword args

    If no environment or keyword arguments are supplied, a default
    configuration from 'TW.Utils.AppConfig.getDefaultConfig()' is
    used.  If an environment is supplied, it will be updated with any
    supplied keyword arguments.  If only keyword arguments are supplied,
    they will be used as the environment."""

    if environ is None:
        if kw:
            environ, kw = kw, None
        else:
            from TW.Utils.AppConfig import getDefaultConfig
            environ = getDefaultConfig()

    if kw:
        environ.update(kw)

    return SPI.getInitialContext(environ)


def lookup(name, requiredInterface=None):
    """Look up 'name' in default context, returning 'requiredInterface'"""
    return defaultInitialContext().lookup(name, requiredInterface)


def parseName(name):
    """Parse 'name' in default initial context, and return a name object"""
    return defaultInitialContext().parseName(name)





_initCtx = None

def defaultInitialContext():

    """Return the default initial context used for simple lookups/parsing

    Note: any changes made to the default initial context will affect all
    lookups done with 'Naming.lookup()' and 'Naming.parseName()', so be
    sure you know what you're doing if you do something with this!  That's
    why this function isn't exported from the 'Naming.API' module."""

    if _initCtx is None:
        global _initCtx
        _initCtx = getInitialContext()

    return _initCtx


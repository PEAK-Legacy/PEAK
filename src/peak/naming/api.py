"""Functions directly usable from the peak.naming package"""

__all__ = ['InitialContext', 'lookup']

import SPI

def InitialContext(environ=None, **kw):

    """Get an initial naming context, based on 'environ' and keyword args

    If no environment or keyword arguments are supplied, a default
    configuration from 'peak.config.getDefaultConfig()' is
    used.  If an environment is supplied, it will be updated with any
    supplied keyword arguments.  If only keyword arguments are supplied,
    they will be used as the environment."""

    if environ is None:
        if kw:
            environ, kw = kw, None
        else:
            from peak.config import getDefaultConfig
            environ = getDefaultConfig()

    if kw:
        environ.update(kw)

    return SPI.getInitialContext(environ)


def lookup(name):
    """Look up 'name' in a default context, returning 'requiredInterface'"""
    return InitialContext().lookup(name)



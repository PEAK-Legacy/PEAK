"""API functions and classes for the peak.naming package"""

from interfaces import *
from names      import *
from references import *

import spi

def InitialContext(environ=None, **kw):

    """Get an initial naming context, based on 'environ' and keyword args

    If no environment is supplied, a default configuration from
    'peak.config.getDefaultConfig()' is used.  If keyword arguments are
    supplied, the environment will be updated with them.
    """

    if environ is None:
        if kw:
            environ, kw = kw, None
        else:
            #from peak.config import getDefaultConfig
            #environ = getDefaultConfig()
            environ = {} # XXX temporary hack

    if kw:
        environ.update(kw)

    return spi.getInitialContext(environ)


def lookup(name):
    """Look up 'name' in a default context, returning 'requiredInterface'"""
    return InitialContext().lookup(name)


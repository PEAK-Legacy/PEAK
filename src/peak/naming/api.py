"""API functions and classes for the peak.naming package"""

from interfaces import *
from names      import *
from references import *

import spi

def InitialContext(parent=None, **kw):

    """Get an initial naming context, based on 'parent' and keyword args"""

    return spi.getInitialContext(parent, **kw)


def lookup(name):
    """Look up 'name' in a default context, returning 'requiredInterface'"""
    return InitialContext().lookup(name)


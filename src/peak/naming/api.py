"""API functions and classes for the peak.naming package"""

from interfaces import *
from names      import *
from properties import *

import spi

def InitialContext(parent=None, **options):

    """Get an initial naming context, based on 'parent' and keyword options"""

    return spi.getInitialContext(parent, **options)


def lookup(name, parent=None, **options):
    """Look up 'name' in a default context, returning 'requiredInterface'"""
    return InitialContext(parent, **options).lookup(name)


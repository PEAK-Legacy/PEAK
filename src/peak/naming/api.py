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


def parseURL(name, parent=None):

    """Return a parsed URL, based on schemes available to 'parent'"""

    url = toName(name)

    if url.nameKind != URL_KIND:
        raise exceptions.InvalidName("Not a URL", name)

    scheme, body = url.scheme, url.body

    ctx = spi.getURLContext(scheme, context=parent, iface=IResolver)

    if ctx is None:
        raise exceptions.InvalidName("Unknown scheme", scheme)

    return ctx.schemeParser(scheme, body)


"""Functions directly usable from the TW.Naming package"""

__all__ = ['lookup','parseName']


def lookup(name, requiredInterface=None):
    """Look up 'name' and force result to 'requiredInterface'
    """
    return _context().lookup(name, requiredInterface)


def parseName(name):
    """Parse 'name' and return a name object appropriate to its scheme
    """
    return _context().parseName(name)


_initCtx = None

def _context():

    global _initCtx

    if _initCtx is None:

        from TW.Utils.AppConfig import getDefaultConfig
        from SPI import getInitialContext

        _initCtx = getInitialContext( getDefaultConfig() )

    return _initCtx


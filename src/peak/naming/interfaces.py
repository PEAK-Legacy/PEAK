"""Interfaces for TW.Naming package"""

import Interface


__all__ = [
    'IName', 'IBasicContext', 'IReadContext', 'IWriteContext',
    'NamingException', 'InvalidNameException', 'NameNotFoundException',
]


class NamingException(Exception):
    """Base class for all TW.Naming exceptions"""

class InvalidNameException(NamingException):
    """Unparseable string or non-name object"""

class NameNotFoundException(NamingException, LookupError):
    """A name could not be found"""






















class IName(Interface.Base):
    """Abstract name object"""


class IBasicContext(Interface.Base):

    """Basic naming context; supports only configuration and name handling"""
    
    def lookup(name, requiredInterface=None):
        """Lookup 'name' --> object that supports 'requiredInterface'"""
        
    def parseName(name):
        """Parse 'name' string and return a name object"""
        
    def getEnvironment():
        """Return a mapping representing the context's configuration"""

    def addToEnvironment(key, value):
        """Add or alter a configuration entry in the context's environment"""

    def removeFromEnvironment(key):
        """Remove a configuration entry from the context's environment"""

    def close():
        """Close the context"""


    # lookupLink, composeName, getNameParser, getNameInNamespace


class IReadContext(IBasicContext):

    """Context that supports iteration/inspection of contents"""

    # list, listBindings,






class IWriteContext(IBasicContext):

    """Context that supports adding/changing its contents"""

    # bind, rebind, unbind, rename,
    # createSubcontext, destroySubcontext, 

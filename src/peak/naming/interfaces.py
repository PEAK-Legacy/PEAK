"""Interfaces for peak.naming package"""

import Interface


__all__ = [

    'IName', 'ISyntax',

    'IObjectFactory', 'IStateFactory', 'IURLContextFactory',

    'I_NNS_Binding', 'IBasicContext', 'IReadContext', 'IWriteContext',

]



























class ISyntax(Interface.Base):
    """Syntax object"""


class IName(Interface.Base):
    """Abstract name object"""


class IBasicContext(Interface.Base):

    """Basic naming context; supports only configuration and name handling"""
    
    def lookup(name):
        """Lookup 'name' --> object; synonym for __getitem__"""

    def lookup_nns(name=None):
        """Lookup 'name' to retrieve a "next naming system" pointer"""

    def __getitem__(name):
        """Lookup 'name' and return an object"""

    def get(name, default=None):
        """Lookup 'name' and return an object, or 'default' if not found"""

    def __contains__(name):
        """Return a true value if 'name' has a binding in context"""

    def has_key(name):
        """Synonym for __contains__"""

    def getEnvironment():
        """Return a mapping representing the context's configuration"""

    def addToEnvironment(key, value):
        """Add or alter a configuration entry in the context's environment"""

    def removeFromEnvironment(key):
        """Remove a configuration entry from the context's environment"""

    def close():
        """Close the context"""

    def copy():
        """Return a copy of the context"""

    def lookupLink(name):
        """Return terminal LinkRef of 'name', if it's a link"""


class IReadContext(IBasicContext):

    """Context that supports iteration/inspection of contents"""

    def keys():
        """Return a sequence of the names present in the context"""

    def __iter__():
        """Return an iterator of the names present in the context"""

    def items():
        """Return a sequence of (name,boundItem) pairs"""

    def info():
        """Return a sequence of (name,(refInfo,attrs)) pairs"""

    # search, getAttributes


class IWriteContext(IBasicContext):

    """Context that supports adding/changing its contents"""

    def rename(oldName,newName):
        """Rename 'oldName' to 'newName'"""

    def __setitem__(name,object,attrs=None):
        """Bind 'object' under 'name'"""
        
    def __delitem__(name):
        """Remove any binding associated with 'name'"""

    def bind(name,object,attrs=None):
        """Synonym for __setitem__"""

    def unbind(name,object):
        """Synonym for __delitem__"""

    # createSubcontext, destroySubcontext, modifyAttributes


class I_NNS_Binding(IBasicContext):

    def bind_nns_ptr(name, object):
        """Bind 'object' as the NNS pointer for 'name'"""

    def unbind_nns_ptr(name):
        """Remove any NNS pointer bound to 'name'"""



class IObjectFactory(Interface.Base):

    def getObjectInstance(refInfo, name, context, environment, attrs=None):
        """Return the object that should be constructed from 'refInfo'"""


class IStateFactory(Interface.Base):

    def getStateToBind(obj, name, context, environment, attrs=None):
        """Return the state that should be used to save 'obj'"""


class IURLContextFactory(Interface.Base):

    def getURLContext(scheme, context=None, environ=None, iface=IBasicContext):
        """Return a context that can provide 'iface' for 'scheme' URLs"""



















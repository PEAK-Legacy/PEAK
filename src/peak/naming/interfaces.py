"""Interfaces and Exceptions for peak.naming package"""

import Interface


__all__ = [

    'IName', 'ISyntax', 'IAddress',
    'IObjectFactory', 'IStateFactory', 'IURLContextFactory',
    'I_NNS_Binding', 'IBasicContext', 'IReadContext', 'IWriteContext',

    'NamingException', 'InvalidNameException', 'NameNotFoundException',
    'NotContextException',
]



























class NamingException(Exception):

    """Base class for all peak.naming exceptions

        Supports the following constructor keyword arguments, which then
        become attributes of the exception object:

            rootException -- Exception that caused this exception to be thrown.
        
            rootTraceback -- Traceback of the root exception.
        
            resolvedName -- The portion of the name that was successfully
                resolved.

            resolvedObj -- The object through which resolution was successful,
                i.e., the object to which 'resolvedName' is bound.
            
            remainingName -- The remaining portion of the name which could not
                be resolved.

        The constructor also accepts an arbitrary number of unnamed arguments,
        which are treated the way arguments to the standard Exception class
        are treated.  (That is, saved in the 'args' attribute and used in the
        '__str__' method for formatting.)
    """

    formattables = ('resolvedName', 'remainingName', 'rootException',)
    otherattrs   = ('resolvedObj', 'rootTraceback', 'args', )

    __slots__ = list( formattables + otherattrs )


    def __init__(self, *args, **kw):

        for k in self.otherattrs:
            setattr(self,k,kw.get(k))

        self.args = args



    def __str__(self):

        """Format the exception"""

        txt = Exception.__str__(self)
        
        extras = [
            '%s=%s' % (k,getattr(self,k))
            for k in self.formattables if getattr(self,k,None) is not None
        ]

        if extras:
            return "%s [%s]" % (txt, ','.join(extras))
            
        return txt


class InvalidNameException(NamingException):
    """Unparseable string or non-name object"""
   

class NameNotFoundException(NamingException, LookupError):
    """A name could not be found"""

class NotContextException(NamingException):
    """Continuation is not a context/does not support required interface"""















class ISyntax(Interface.Base):
    """Syntax object"""


class IName(Interface.Base):
    """Abstract name object"""

    isComposite = Interface.Attribute("True, if name is composite")
    isCompound  = Interface.Attribute("True, if name is compound")
    isURL       = Interface.Attribute("True, if name is URL")


class IAddress(IName):
    """Name that supports in-context self-retrieval"""

    def retrieve(refInfo, name, context, environment, attrs=None):
        """Retrieve the address"""
























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



















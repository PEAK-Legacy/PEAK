"""Interfaces and Exceptions for peak.naming package"""

from Interface import Interface
from Interface.Attribute import Attribute


__all__ = [

    'IName', 'ISyntax', 'IAddress', 'IInitialContextFactory',
    'IObjectFactory', 'IStateFactory', 'IURLContextFactory',
    'I_NNS_Binding', 'IBasicContext', 'IReadContext', 'IWriteContext',
    'IParentForRetrievedObject',

]



class ISyntax(Interface):
    """Syntax object"""


class IName(Interface):
    """Abstract name object"""

    isComposite = Attribute("True, if name is composite")
    isCompound  = Attribute("True, if name is compound")
    isURL       = Attribute("True, if name is URL")


class IAddress(IName):
    """Name that supports in-context self-retrieval"""

    def retrieve(refInfo, name, context, attrs=None):
        """Retrieve the address"""


class IParentForRetrievedObject(Interface):
    """Marker for component which will be a newly created target's parent"""



class IBasicContext(Interface):

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

    def close():
        """Close the context"""

    def lookupLink(name):
        """Return terminal LinkRef of 'name', if it's a link"""

    creationParent = Attribute(
        """The object which should be used as the parent of any newly-created
        components during retrieval from this context.

        This attribute is for the use of object factories and the like, which
        must create a new object relative to some context.  It *must* be
        implemented as a findUtility lookup for 'IParentForRetrievedObject',
        except in InitialContext objects, where it must be an actual object
        reference.  (Since all naming lookups begin from an InitialContext,
        that is where the search must "top out".)"""
    )


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


class IInitialContextFactory(Interface):

    def getInitialContext(parentComponent, **options):
        """Return a naming context for 'parentComponent' with 'options'"""


class IObjectFactory(Interface):

    def getObjectInstance(refInfo, name, context, attrs=None):
        """Return the object that should be constructed from 'refInfo'"""


class IStateFactory(Interface):

    def getStateToBind(obj, name, context, attrs=None):
        """Return the '(obj,attrs)' state that should be used to save 'obj'"""


class IURLContextFactory(Interface):

    def getURLContext(scheme, context, iface=IBasicContext):
        """Return a context that can provide 'iface' for 'scheme' URLs"""



















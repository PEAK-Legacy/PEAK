"""Interfaces and Exceptions for peak.naming package"""

from Interface import Interface
from Interface.Attribute import Attribute


__all__ = [

    'IName', 'IAddress', 'IInitialContextFactory', 'IResolver',
    'IObjectFactory', 'IStateFactory', 'IURLContextFactory',
    'I_NNS_Binding', 'IBasicContext', 'IReadContext', 'IWriteContext',
    'COMPOUND_KIND', 'COMPOSITE_KIND', 'URL_KIND', 'isName', 'isAddress',
    'isAddressClass',
]



























COMPOUND_KIND  = 1
COMPOSITE_KIND = 2
URL_KIND       = 3


class IName(Interface):

    """Abstract name object"""

    nameKind = Attribute("One of COMPOUND_KIND, COMPOSITE_KIND, or URL_KIND")

    def __add__(other):
        """Add 'other' to name, composing a name that is relative to this one"""

    def __radd__(other):
        """Add name to 'other', using this name as a relative name to it"""
        

isName = IName.isImplementedBy



class IAddress(IName):

    """Name that supports in-context self-retrieval"""

    def retrieve(refInfo, name, context, attrs=None):
        """Retrieve the address"""


isAddress = IAddress.isImplementedBy

isAddressClass = IAddress.isImplementedByInstancesOf








class IResolver(Interface):

    """Thing which can participate in name resolution"""

    def resolveToInterface(name,iface):
        """Find nearest ctx to 'name' supporting 'iface', return rest of name
        
            Return a tuple of the form '(ctx,remainingName)', where 'ctx' is
            the context nearest to 'name' that supports interface 'iface', and
            'remainingName' is the portion of 'name' that is relative to
            'ctx'.  That is, 'remainingName' interpreted relative to 'ctx'
            should be the same name as 'name' relative to the context this
            method is called on.
        """



























class IBasicContext(IResolver):

    """Basic naming context; supports only name retrieval"""

    def lookup(name):
        """Lookup 'name' --> object; synonym for __getitem__"""

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

    # XXX search, getAttributes
























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

    def mksub(name, attrs=None):
        """Create a subcontext of the same kind under 'name', with 'attrs'"""
        
    def rmsub(name):
        """Remove sub-context 'name'"""
        
    # XXX modifyAttributes















class I_NNS_Binding(IBasicContext):

    def bind_nns_ptr(name, object):
        """Bind 'object' as the NNS pointer for 'name'"""

    def unbind_nns_ptr(name):
        """Remove any NNS pointer bound to 'name'"""


class IInitialContextFactory(Interface):

    def getInitialContext(parentComponent=None, **options):
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



















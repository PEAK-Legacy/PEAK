"""Interfaces, constants, property names, etc. for peak.naming"""

from Interface import Interface
from Interface.Attribute import Attribute
from peak.api import PropertyName


__all__ = [

    'IName', 'IAddress', 'IInitialContextFactory', 'IResolver',
    'IObjectFactory', 'IStateFactory', 'IURLContextFactory',
    'IBasicContext', 'IReadContext', 'IWriteContext',
    'COMPOUND_KIND', 'COMPOSITE_KIND', 'URL_KIND', 'isName', 'isAddress',
    'isAddressClass', 'isResolver',

    'CREATION_PARENT', 'OBJECT_FACTORIES', 'STATE_FACTORIES', 'SCHEMES_PREFIX',
    'CREATION_NAME', 'INIT_CTX_FACTORY', 'SCHEME_PARSER',

]


INIT_CTX_FACTORY = PropertyName('peak.naming.initialContextFactory')

CREATION_NAME    = PropertyName('peak.naming.creationName')
CREATION_PARENT  = PropertyName('peak.naming.creationParent')
OBJECT_FACTORIES = PropertyName('peak.naming.objectFactories')
STATE_FACTORIES  = PropertyName('peak.naming.stateFactories')
SCHEME_PARSER    = PropertyName('peak.naming.schemeParser')

SCHEMES_PREFIX   = PropertyName('peak.naming.schemes')











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

isResolver = IResolver.isImplementedBy

























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















# Framework interfaces

class IInitialContextFactory(Interface):
    """Get access to an initial naming context"""

    def getInitialContext(parentComponent=None, componentName=None, **options):
        """Return a naming context for 'parentComponent' with 'options'"""


class IObjectFactory(Interface):
    """Convert data in a naming system into a useful retrieved object"""

    def getObjectInstance(refInfo, name, context, attrs=None):

        """Return the object that should be constructed from 'refInfo'

        This function or method should return the object which is referenced
        by 'refInfo', or 'None' if it does not know how or does not wish to
        interpret 'refInfo'.

        'refInfo' is an object representing a reference, address, or state of
        an object found in 'context' under 'name', with attributes 'attrs'.
        The specific contents of 'refInfo', 'name', and 'attrs', are entirely
        dependent upon the implementation details of the 'context' object.

        (Note: the official semantics of the 'attrs' parameter is not yet
        defined; it is reserved for implementing JNDI 'DirContext'-style
        operations.  Currently 'None' is the only correct value for 'attrs'.)

        There is a default implementation of this interface supplied by the
        'peak.naming.spi' module, and registered by the '"peak.ini"' file.
        See the 'peak.naming.spi' module for more details on the default
        behavior."""


class IStateFactory(Interface):
    """Convert an object into state that can be stored in a naming system"""

    def getStateToBind(obj, name, context, attrs=None):
        """Return the '(obj,attrs)' state that should be used to save 'obj'"""

class IURLContextFactory(Interface):

    """Obtain a context implementation for a URL scheme"""
    
    def getURLContext(scheme,iface,parent=None,componentName=None,**options):

        """Return a context that can provide 'iface' for 'scheme' URLs

        'scheme' is a URL scheme as defined by RFC 1738.  The trailing ':'
        should *not* be included.  Per RFC 1738, the '-', '+', and '.'
        characters are allowed.  Also per the RFC, any implementation of
        this interface should use the lowercase form of any scheme name
        supplied.

        This function or method should return a context implementation bound
        to 'parent', with name 'componentName' and providing '**options'.
        If no context implementation supporting 'iface' can be found, return
        'None'.

        'IURLContextFactory' is not normally used as a utility; naming context
        implementations should use the primary 'naming.spi.getURLContext()'
        function to obtain URL context providers when needed.  But, it is
        possible to register implementations of this interface under part
        of the 'peak.naming.schemes' property space, and they will then be
        used to find a more specific URL context.

        For example, if you have a set of schemes 'foo.bar', 'foo.baz',
        and 'foo.spam', you could register the following in an application
        configuration file::

            [peak.naming.schemes]
            foo.* = "some.module"

        and put this in 'some.module'::

            from peak.api import *

            __implements__ = naming.IURLContextFactory

            def getURLContext(scheme,iface,parente,componentName,**options):
                # code to pick between 'foo.bar', 'foo.baz', etc. and
                # return a context implementation
                
        Of course, the only reason to do this is if the contexts are created
        dynamically in some fashion, otherwise it would suffice to register
        'foo.bar', etc. directly in your application's configuration.

        Alternately, you could register your context factory under
        'peak.naming.schemes.*', in which case it would be used as a default
        for any schemes not specifically defined or registered.
        """



















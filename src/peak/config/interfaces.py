from Interface import Interface
from Interface.Attribute import Attribute
from peak.api import exceptions

__all__ = [
    'IRuleFactory', 'IRule', 'IPropertyMap', 'IConfigKey',
]


































class IRuleFactory(Interface):

    """Thing that instantiates a rule for a propertyMap and name"""

    def __call__(propertyMap, propName):
        """Return an IRule instance suitable for the given IPropertyMap"""


class IRule(Interface):

    """Rule to compute a property value for a target object"""

    def __call__(propertyMap, configKey, targetObject):

        """Retrieve 'configKey' for 'targetObject' or return 'NOT_FOUND'

        The rule object is allowed to call any 'IPropertyMap' methods on the
        'propertyMap' that is requesting computation of this rule.  It is
        also allowed to call 'config.getProperty()' relative to 'targetObject'
        or 'propertyMap'.

        What an IRule must *not* do, however, is return different results over
        time for the same input parameters.  If it cannot guarantee this
        algorithmically, it must cache its results keyed by the parameters it
        used, and not compute the results a second time.
        """















class IPropertyMap(Interface):

    def setRule(propName, ruleFactory):
        """Add IRuleFactory's rule to rules for computing a property

        Note that if the specified property (or any more-specific form)
        has already been accessed, an 'AlreadyRead' exception results.

        'propName' may be a "wildcard", of the form '"part.of.a.name.*"'
        or '"*"' by itself in the degenerate case.  Wildcard rules are
        checked in most-specific-first order, after the non-wildcard name,
        and before the property's default."""


    def setDefault(propName, ruleObj):
        """Set 'IRule' 'defaultObj' as function to compute 'propName' default

        Note that if a default for the specified property has already been
        accessed, an 'AlreadyRead' exception results.  Also, if a value has
        already been set for the property, the default will be ignored.  The
        default will also be ignored if a rule exists for the same 'propName'
        (or parent wildcard thereof), unless the rule returns 'NOT_FOUND' or
        'NOT_GIVEN'.  Note: like values and unlike rules, defaults can *not*
        be registered for a wildcard 'propName'."""


    def setValue(propName, value):
        """Set property 'propName' to 'value'

        No wildcards allowed.  'AlreadyRead' is raised if the property
        has already been accessed for the target object."""


    def getValueFor(propName, forObj=None):
        """Return value of property for 'forObj' or return 'NOT_FOUND'"""


    def registerProvider(ifaces, ruleObj):
        """Register 'IRule' 'ruleObj' as a provider for 'ifaces'"""


class IConfigKey(Interface):

    """Marker interface for configuration data keys
    
    This is effectively just the subset of 'Interface.IInterface' that's
    needed by PropertyMap and EigenRegistry instances to use as interface-like
    utility keys."""


    def getBases():
        """Return a sequence of the base interfaces, or empty sequence
           if object is a property name"""

    def extends(other, strict=1):
        """Test whether the interface extends another interface
            (Meaningless for property names)"""


from Interface.Implements import implements
from peak.naming.names import PropertyName

implements(Interface, IConfigKey)
implements(PropertyName, IConfigKey)


















        

from Interface import Interface
from Interface.Attribute import Attribute

__all__ = [
    'IRule', 'IPropertyMap',
    'PropertyNotFound', 'NoPropertyMap', 
]


class PropertyNotFound(Exception):
    """A required configuration property could not be found/computed"""


class NoPropertyMap(Exception):
    """No property map was found to do a 'setRule()' or 'setProperty()' on"""


class IRule(Interface):

    """Rule to compute a default property value"""

    def __call__(propertyMap, targetObject, propName):

        """Compute property 'propName' for 'targetObject' or return 'NOT_FOUND'

        The rule object is allowed to call any 'IPropertyMap' methods on the
        'propertyMap' that is requesting computation of this rule.  It is
        also allowed to call 'config.getProperty()' relative to 'targetObject'.

        What an IRule must *not* do, however, is return different results over
        time for the same input parameters.  If it cannot guarantee this
        algorithmically, it must cache its results keyed by the parameters it
        used, and not compute the results a second time."""








class IPropertyMap(Interface):

    def setRule(propName, ruleObj):
        """Use IRule 'ruleObj' to compute 'propName' in future
        
        Note that if the specified property has already been accessed for
        any target object, an 'AlreadyRead' exception results.  Also, if
        a value has already been set for the property, the rule will be
        ignored.

        Note also that 'propName' may be a "wildcard", of the form
        '"part.of.a.name.*"' or '"*"' by itself in the degenerate case.
        Wildcard rules are checked in order of specificity, after
        non-wildcard property names.
        """

    def setProperty(propName, value):
        """Set property 'propName' to 'value'

        No wildcards allowed.  'AlreadyRead' is raised if the property
        has already been accessed, for any target object."""


    def getPropertyFor(obj, propName):
        """Return value of property for 'obj' or return 'NOT_FOUND'"""

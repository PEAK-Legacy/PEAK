from Interface import Interface
from Interface.Attribute import Attribute

__all__ = [
    'IRule', 'IDefault', 'IPropertyMap',
    'PropertyNotFound', 'NoPropertyMap', 'ObjectOutOfScope',
]


class PropertyNotFound(Exception):
    """A required configuration property could not be found/computed"""


class NoPropertyMap(Exception):
    """No property map was found to do a 'setRule()' or 'setProperty()' on"""


class ObjectOutOfScope(Exception):
    """Property map doesn't support managing properties for other objects"""






















class IRule(Interface):

    """Rule to compute a property value for a target object"""

    def __call__(propertyMap, propName, targetObject):

        """Compute property 'propName' for 'targetObject' or return 'NOT_FOUND'

        The rule object is allowed to call any 'IPropertyMap' methods on the
        'propertyMap' that is requesting computation of this rule.  It is
        also allowed to call 'config.getProperty()' relative to 'targetObject'.

        What an IRule must *not* do, however, is return different results over
        time for the same input parameters.  If it cannot guarantee this
        algorithmically, it must cache its results keyed by the parameters it
        used, and not compute the results a second time."""


class IDefault(Interface):

    """Rule to compute a default property value, irrespective of target"""

    def __call__(propertyMap, propName):
        """Compute default for property 'propName' or return 'NOT_FOUND'"""

















class IPropertyMap(Interface):

    def setRule(propName, ruleObj):
        """Use IRule 'ruleObj' to compute 'propName' in future

        Note that if a rule or value for the specified property has already
        been accessed for any target object, an 'AlreadyRead' exception
        results.  Also, if a value has already been set for the property,
        the rule will be ignored.

        Note also that 'propName' may be a "wildcard", of the form
        '"part.of.a.name.*"' or '"*"' by itself in the degenerate case.
        Wildcard rules and defaults are checked in most-specific-first
        order, after the non-wildcard name."""


    def setDefault(propName, defaultObj):
        """Use IDefault 'defaultObj' to compute 'propName' default

        Note that if a default for the specified property has already been
        accessed, an 'AlreadyRead' exception results.  Also, if a value has
        already been set for the property, the default will be ignored.  The
        default will also be ignored if a rule exists for the same 'propName',
        unless the rule returns 'NOT_FOUND'.

        As with 'setRule()', 'propName' may be a "wildcard"."""


    def setPropertyFor(obj, propName, value):
        """Set property 'propName' to 'value' for 'obj'

        No wildcards allowed.  'AlreadyRead' is raised if the property
        has already been accessed, for the target object.  If 'obj' is
        outside the property map's scope or it only manages properties for
        its owner, an 'ObjectOutOfScope' exception will be raised."""


    def getPropertyFor(obj, propName):
        """Return value of property for 'obj' or return 'NOT_FOUND'"""

from __future__ import generators
from Interface import Interface
from Interface.Attribute import Attribute
from peak.api import exceptions

__all__ = [
    'IRuleFactory', 'IRule', 'IDefault', 'IPropertyMap', 'IConfigKey',
    'Property',
]
































class IRuleFactory(Interface):

    def __call__(propertyMap, propName):
        """Return an IRule instance suitable for the given IPropertyMap"""


class IRule(Interface):

    """Rule to compute a property value for a target object"""

    def __call__(propName, targetObject):

        """Compute property 'propName' for 'targetObject' or return 'NOT_FOUND'

        The rule object is allowed to call any 'IPropertyMap' methods on the
        'propertyMap' that is requesting computation of this rule.  It is
        also allowed to call 'config.getProperty()' relative to 'targetObject'
        or 'propertyMap'.

        What an IRule must *not* do, however, is return different results over
        time for the same input parameters.  If it cannot guarantee this
        algorithmically, it must cache its results keyed by the parameters it
        used, and not compute the results a second time.

        In the event a rule cannot speak to the presence or absence of a
        property value for a given name and target, it may return the
        'NOT_GIVEN' singleton.  In this case, the 'propertyMap' will continue
        the search for a value, but will not consider the rule to have
        participated in the determination of the value.  This is important
        for rules that load configuration values, rules, or defaults, but do
        not directly involve themselves in the computation of property values.
        Such rules should return 'NOT_GIVEN' for every call after the first
        one, in order to "bow out" of the property calculation process once
        they've done their job.  They can also return 'NOT_GIVEN' on the first
        call, so long as all the data they load is either values or defaults.
        """





class IDefault(Interface):

    """Rule to compute a default property value, irrespective of target"""

    def __call__(propertyMap, propName):
        """Compute default for property 'propName' or return 'NOT_FOUND'"""



































class IPropertyMap(Interface):

    def setRule(propName, ruleFactory):
        """Add IRuleFactory's rule to rules for computing a property

        Note that if a rule or value for the specified property has already
        been accessed for any target object, an 'AlreadyRead' exception
        results.  Also, if a value has already been set for the property,
        the rule will be ignored.

        Note also that 'propName' may be a "wildcard", of the form
        '"part.of.a.name.*"' or '"*"' by itself in the degenerate case.
        Wildcard rules are checked in most-specific-first order, after
        the non-wildcard name, and before the property's default."""

    def setDefault(propName, defaultObj):
        """Set IDefault 'defaultObj' as function to compute 'propName' default

        Note that if a default for the specified property has already been
        accessed, an 'AlreadyRead' exception results.  Also, if a value has
        already been set for the property, the default will be ignored.  The
        default will also be ignored if a rule exists for the same 'propName'
        (or parent wildcard thereof), unless the rule returns 'NOT_FOUND' or
        'NOT_GIVEN'.  Note: like values and unlike rules, defaults can *not*
        be registered for a wildcard 'propName'."""

    def setPropertyFor(obj, propName, value):
        """Set property 'propName' to 'value' for 'obj'

        No wildcards allowed.  'AlreadyRead' is raised if the property
        has already been accessed for the target object.  If 'obj' is
        outside the property map's scope or it only manages properties for
        its owner, an 'ObjectOutOfScope' exception will be raised.
        'obj' may be 'None', in which case it is assumed that the property
        should be set for all objects within the map's scope, unless they
        have properties more specifically set upon them."""

    def getPropertyFor(obj, propName):
        """Return value of property for 'obj' or return 'NOT_FOUND'"""


class IConfigKey(Interface):

    """This is a marker interface used to indicate that XXX"""

    def getBases():
        """Return a sequence of the base interfaces, or empty sequence
           for a 
        """

    def extends(other, strict=1):
        """Test whether the interface extends another interface"""


from Interface.Implements import implements
implements(Interface, IConfigKey)


























import re

validChars = re.compile( r"([-+*._a-z0-9]+)", re.I ).match

class Property(str):

    __implements__ = IConfigKey

    def __new__(klass, *args):

        self = super(Property,klass).__new__(klass,*args)

        valid = validChars(self)

        if valid.end()<len(self):
            raise exceptions.InvalidName(
                "Invalid characters in property name", self
            )

        parts = self.split('.')

        if '' in parts or not parts:
            raise exceptions.InvalidName(
                "Empty part in property name", self
            )

        if '*' in self:
            if '*' not in parts or parts.index('*') < (len(parts)-1):
                raise exceptions.InvalidName(
                    "'*' must be last part of wildcard property name", self
                )
            
        return self








    def isWildcard(self):
        return self.endswith('*')


    def matchPatterns(self):
    
        yield self

        while '.' in self:
            self = self[:self.rindex('.')]
            yield self+'.*'

        yield '*'


    def getBases(self):
        return ()


    def extends(self, other, strict=1):
        return not strict and self==other
        

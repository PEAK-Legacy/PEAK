from peak.interface import Interface, Attribute, addDeclarationToType
from peak.api import exceptions, PropertyName

__all__ = [
    'IConfigKey', 'IConfigurable', 'IConfigSource',
    'IRule', 'IPropertyMap', 'ISettingLoader',
]


class IConfigKey(Interface):

    """Marker interface for configuration data keys
    
    Both 'PropertyName()' and 'Interface' objects are usable as
    configuration keys.  The common interface required is a subset of
    'Interface.IInterface' that's needed by property maps and EigenRegistry
    instances to use as dictionary keys.

    This module automatically marks both 'PropertyName' and 'Interface' as
    supporting this interface."""


    def getBases():
        """Return a sequence of the base interfaces, or empty sequence
           if object is a property name"""

    def extends(other, strict=1):
        """Test whether the interface extends another interface
            (Meaningless for property names)"""



# XXX when we can 'adapt()' to protocols, IConfigKey can just know that
# XXX Interface and PropertyName are valid supporters.

addDeclarationToType(Interface.__class__, IConfigKey)
addDeclarationToType(PropertyName, IConfigKey)




class IConfigSource(Interface):

    """Something that can be queried for configuration data"""

    def _getConfigData(configKey, forObj):

        """Return a value of 'configKey' for 'forObj' or 'NOT_FOUND'

        Note that 'configKey' is an 'IConfigKey' instance and may therefore be
        a 'PropertyName' or an 'Interface' object.

        Also note that 'binding.Base' implements this method by simply
        returning 'NOT_FOUND', and that is a perfectly acceptable
        implementation for many purposes."""


class IConfigurable(IConfigSource):

    """Object which can be configured with rules for configuration keys"""

    def registerProvider(configKeys, ruleObj):

        """Register 'IRule' 'ruleObj' as a provider for 'configKeys'

            'configKeys' may be an object that implements 'IConfigKey',
            or a (possibly nested) tuple of such objects.  'ruleObj' will
            be registered as a provider for all the provided keys.

            If a provider has already been registered for a given key, the
            new provider will replace it, provided that it has not yet been
            used.  (If it has, 'AlreadyRead' should be raised.)

            If a key is an 'Interface' with bases, the provider will also
            be registered for any base interfaces of the supplied key(s),
            unless a provider was previously registered under a base of
            the supplied key.
        """




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
        used, and not compute the results a second time."""
























class ISettingLoader(Interface):

    """Callable used to load configuration data"""

    def __call__(propertyMap, *args, **kw):
        """Load settings into 'propertyMap'

        Loading functions can require whatever arguments are useful or desired.
        The value of each "Load Settings From" config file entry will be
        interpreted as part of a call to the loader.  For example, this entry::

            [Load Settings From]
            mapping = importString('os.environ'), prefix='environ.*'

        will be interpereted as::

            loader(propertyMap, importString('os.environ'), prefix='environ.*')

        So it's up to the author of the loader to choose and document the
        arguments to be used in configuration files.

        However, one keyword argument which all 'ISettingLoader' functions
        must accept is 'includedFrom'.  This is an implementation-defined
        object which represents the state of the 'ISettingLoader' which is the
        caller.  Currently, this argument is only supplied by the default
        'config.loadConfigFile()' loader, and the value passed is a
        'ConfigReader' instance.
        """













class IPropertyMap(IConfigurable):

    """Specialized component for storing configuration data"""

    def setRule(propName, ruleObj):
        """Set rule for computing a property

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





        

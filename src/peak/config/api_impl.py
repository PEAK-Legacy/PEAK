"""Configuration Management API"""

from peak.api import exceptions, NOT_FOUND, NOT_GIVEN, PropertyName
from interfaces import *
from config_components import findUtility, iterParents, ConfigurationRoot
from peak.interface import adapt

__all__ = [
    'getProperty', 'setPropertyFor', 'setRuleFor', 'setDefaultFor',
    'makeRoot',
]



def setPropertyFor(obj, propName, value):

    pm = findUtility(obj, IPropertyMap)
    pm.setValue(propName, value)


def setRuleFor(obj, propName, ruleObj):

    pm = findUtility(obj, IPropertyMap)
    pm.setRule(propName, ruleObj)


def setDefaultFor(obj, propName, defaultObj):

    pm = findUtility(obj, IPropertyMap)
    pm.setDefault(propName, defaultObj)











def makeRoot(**options):

    """Create a configuration root, suitable for use as a parent component

    This creates and returns a new 'IConfigurationRoot' with its default
    configuration loading from 'peak.ini'.  The returned root component
    will "know" it is a root, so any components that use it as a parent
    will get their 'uponAssembly()' events invoked immediately.

    Normally, this function is called without any parameters, but it will
    also accept keyword arguments that it will pass along when it calls the
    'peak.config.config_components.ConfigurationRoot' constructor.

    Currently, the only acceptable keyword argument is 'iniFiles', which must
    be a sequence of filename strings or '(moduleName,fileName)' tuples.

    The default value of 'iniFiles' is '[("peak","peak.ini")]', which loads
    useful system defaults from 'peak.ini' in the 'peak' package directory.
    Files are loaded in the order specified, with later files overriding
    earlier ones, unless the setting to be overridden has already been used
    (in which case an 'AlreadyRead' error occurs)."""

    return ConfigurationRoot(None, **options)


















def getProperty(obj, propName, default=NOT_GIVEN):

    """Find property 'propName' for 'obj'

        Returns 'default' if the property is not found.  If no 'default'
        is supplied, raises 'PropertyNotFound'.

        Properties are located by querying all the 'IPropertyMap' utilities
        available from 'obj' and its parent components, up through the local
        and global configuration objects, if applicable.
    """

    if not isinstance(propName,PropertyName):
        propName = PropertyName(propName)

    if not propName.isPlain():
        raise exceptions.InvalidName(
            "getProperty() can't use wildcard/default properties", propName
        )

    forObj = component = obj

    for component in iterParents(obj):
        try:
            prop = component._getConfigData
        except AttributeError:
            continue

        prop = prop(forObj, propName)

        if prop is not NOT_FOUND:
            return prop

    return adapt(
        component, IConfigurationRoot, NullConfigRoot
    ).propertyNotFound(
        component, propName, forObj, default
    )




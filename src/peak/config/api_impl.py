"""Configuration Management API"""

from peak.api import exceptions, NOT_FOUND, NOT_GIVEN, PropertyName
from interfaces import *
from config_components import *
from peak.interface import adapt

__all__ = [
    'getProperty', 'setPropertyFor', 'setRuleFor', 'setDefaultFor',
]



def setPropertyFor(obj, propName, value):

    pm = findUtility(IPropertyMap, obj)
    pm.setValue(propName, value)


def setRuleFor(obj, propName, ruleObj):

    pm = findUtility(IPropertyMap, obj)
    pm.setRule(propName, ruleObj)


def setDefaultFor(obj, propName, defaultObj):

    pm = findUtility(IPropertyMap, obj)
    pm.setDefault(propName, defaultObj)












def getProperty(propName, obj, default=NOT_GIVEN):

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
            prop = component.__class__._getConfigData
        except AttributeError:
            continue

        prop = prop(component, propName, forObj)

        if prop is not NOT_FOUND:
            return prop

    return adapt(
        component, IConfigurationRoot, NullConfigRoot
    ).propertyNotFound(
        component, propName, forObj, default
    )





























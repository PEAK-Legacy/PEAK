"""Configuration Management API"""

from peak.api import binding, exceptions, NOT_FOUND, NOT_GIVEN, PropertyName
from interfaces import *
from peak.util.EigenData import *
from config_components import *
from weakref import WeakKeyDictionary

__all__ = [
    'getSysConfig', 'setSysConfig', 'registerSystemProvider',
    'getAppConfig', 'setAppConfig', 'registerAppProvider',

    'getProperty',

    'setSystemProperty', 'setSystemRule', 'setSystemDefault',
    'setPropertyFor',    'setRuleFor',    'setDefaultFor',
]

_systemCfg = EigenCell()


def getSysConfig():

    """Return the system (per-interpreter) configuration object"""

    def defaultSysConfig():
        cfg = SystemConfig()
        setAppConfig(cfg, None) # force app config for sys. config to be None
        return cfg
        
    return _systemCfg.get(defaultSysConfig)


def setSysConfig(cfg):

    """Replace the system configuration, as long as it hasn't been used yet"""

    _systemCfg.set(cfg)
    setAppConfig(cfg, None)     # force app config for system config to be None


_defaultCfg = EigenCell()
_appConfigs = EigenDict()
_appConfigs.data = WeakKeyDictionary()


def getAppConfig(forRoot=None):

    """Return app configuration object for 'forRoot'"""

    forRoot = binding.getRootComponent(forRoot)

    # Only weakref-able objects can have a root assigned

    if type(forRoot).__weakrefoffset__ and forRoot in _appConfigs:
        return _appConfigs[forRoot]
        
    return _defaultCfg.get( lambda: AppConfig(getSysConfig()) )


def setAppConfig(forRoot, cfg):

    """Replace app config for 'forRoot', as long as it hasn't been used"""

    forRoot = binding.getRootComponent(forRoot)

    if forRoot is None:
        _defaultCfg.set(cfg)

    elif type(forRoot).__weakrefoffset__:
        _appConfigs[forRoot] = cfg

    else:
        raise TypeError(
            "Root object w/custom AppConfig must be weak-referenceable",
            forRoot
        )





def getProperty(propName, obj=None, default=NOT_GIVEN):

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

    prop = findUtility(propName, obj, NOT_FOUND)

    if prop is not NOT_FOUND:
        return prop

    if default is NOT_GIVEN:
        raise exceptions.PropertyNotFound(propName, obj)

    return default












def registerSystemProvider(ifaces, provider):
    getSysConfig().registerProvider(ifaces, provider)


def setSystemProperty(propName, value):

    pm = findUtility(IPropertyMap, getSysConfig())
    pm.setValue(propName, value)


def setSystemRule(propName, ruleObj):

    pm = findUtility(IPropertyMap, getSysConfig())
    pm.setRule(propName, ruleObj)


def setSystemDefault(propName, defaultObj):

    pm = findUtility(IPropertyMap, getSysConfig())
    pm.setDefault(propName, defaultObj)





















def registerAppProvider(forRoot, ifaces, provider):
    getAppConfig(forRoot).registerProvider(ifaces, provider)


def setPropertyFor(obj, propName, value):

    pm = findUtility(IPropertyMap, obj)
    pm.setValue(propName, value)


def setRuleFor(obj, propName, ruleObj):

    pm = findUtility(IPropertyMap, obj)
    pm.setRule(propName, ruleObj)


def setDefaultFor(obj, propName, defaultObj):

    pm = findUtility(IPropertyMap, obj)
    pm.setDefault(propName, defaultObj)



"""Configuration Management API"""

from peak.api import binding, NOT_FOUND, NOT_GIVEN
from interfaces import *
from peak.util.EigenData import *
from config_components import *
from weakref import WeakKeyDictionary


__all__ = [
    'getGlobal','setGlobal', 'registerGlobalProvider',
    'getLocal', 'setLocal',  'registerLocalProvider',  'newDefaultConfig',

    'getProperty',

    'setGlobalProperty', 'setGlobalRule', 'setGlobalDefault',
    'setPropertyFor',    'setRuleFor',    'setDefaultFor',
]


_globalCfg = EigenCell()


def getGlobal():

    """Return the global configuration object"""

    if not _globalCfg.locked:
        setGlobal(GlobalConfig())

    return _globalCfg.get()


def setGlobal(cfg):

    """Replace the global configuration, as long as it hasn't been used yet"""

    _globalCfg.set(cfg)
    setLocal(cfg, None)     # force local config for global config to be None


_defaultCfg = EigenCell()
_localCfgs = EigenDict()
_localCfgs.data = WeakKeyDictionary()


def getLocal(forRoot=None):

    """Return a local configuration object for 'forRoot'"""

    if forRoot is not None and _localCfgs.has_key(forRoot):
        return _localCfgs[forRoot]
        
    if not _defaultCfg.locked:
        setLocal(None, newDefaultConfig())

    return _defaultCfg.get()


def setLocal(forRoot, cfg):

    """Replace local config for 'forRoot', as long as it hasn't been used"""

    if forRoot is None:
        _defaultCfg.set(cfg)
    else:
        _localCfgs[forRoot] = cfg



def newDefaultConfig():

    """Return a new, default local configuration object based on getGlobal()"""

    return LocalConfig(getGlobal())







def getProperty(obj, propName, default=NOT_GIVEN):

    """Find property 'propName' for 'obj'

        Returns 'default' if the property is not found.  If no 'default'
        is supplied, raises 'PropertyNotFound'.

        Properties are located by querying all the 'IPropertyMap' utilities
        available from 'obj' and its parent components, up through the local
        and global configuration objects, if applicable.
    """

    for pm in binding.findUtilities(obj, IPropertyMap):

        prop = pm.getPropertyFor(obj,propName)

        if prop is not NOT_FOUND:
            return prop

    else:

        if default is NOT_GIVEN:
            raise PropertyNotFound(propName, obj)

        return default
















def registerGlobalProvider(ifaces, provider):
    getGlobal().registerProvider(ifaces, provider)


def setGlobalProperty(propName, value):

    g = getGlobal()

    pm = binding.findUtility(g, IPropertyMap)

    if pm is None:
        raise NoPropertyMap(
            "No global property map for setGlobalProperty:", propName, value
        )

    pm.setPropertyFor(g, propName, value)


def setGlobalRule(propName, ruleObj):

    pm = binding.findUtility(getGlobal(), IPropertyMap)

    if pm is None:
        raise NoPropertyMap(
            "No global property map for setGlobalRule:", propName, ruleObj
        )

    pm.setRule(propName, ruleObj)


def setGlobalDefault(propName, defaultObj):

    pm = binding.findUtility(getGlobal(), IPropertyMap)

    if pm is None:
        raise NoPropertyMap(
            "No global property map for setGlobalDefault:", propName, ruleObj
        )

    pm.setDefault(propName, ruleObj)

def registerLocalProvider(forRoot, ifaces, provider):
    getLocal(forRoot).registerProvider(ifaces, provider)


def setPropertyFor(obj, propName, value):

    pm = binding.findUtility(obj, IPropertyMap)

    if pm is None:
        raise NoPropertyMap(
            "No property map found for setPropertyFor:", obj, propName, value
        )

    pm.setPropertyFor(obj, propName, value)


def setRuleFor(obj, propName, ruleObj):

    pm = binding.findUtility(obj, IPropertyMap)

    if pm is None:
        raise NoPropertyMap(
            "No property map found for setRuleFor:", obj, propName, ruleObj
        )

    pm.setRule(propName, ruleObj)


def setDefaultFor(obj, propName, ruleObj):

    pm = binding.findUtility(obj, IPropertyMap)

    if pm is None:
        raise NoPropertyMap(
            "No property map found for setDefaultFor:", obj, propName, ruleObj
        )

    pm.setDefault(propName, ruleObj)



"""Configuration Management API"""

from peak.api import binding, exceptions, NOT_FOUND, NOT_GIVEN
from interfaces import *
from peak.util.EigenData import *
from config_components import *
from weakref import WeakKeyDictionary
from peak.naming.names import PropertyName

__all__ = [
    'getGlobal','setGlobal', 'registerGlobalProvider',
    'getLocal', 'setLocal',  'registerLocalProvider',

    'getProperty',

    'setGlobalProperty', 'setGlobalRule', 'setGlobalDefault',
    'setPropertyFor',    'setRuleFor',    'setDefaultFor',
]

_globalCfg = EigenCell()


def getGlobal():

    """Return the global configuration object"""

    if not hasattr(_globalCfg,'value'):
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

    forRoot = binding.getRootComponent(forRoot)

    # Only weakref-able objects can have a root assigned

    if type(forRoot).__weakrefoffset__ and forRoot in _localCfgs:
        return _localCfgs[forRoot]
        
    if not hasattr(_defaultCfg,'value'):
        setLocal(None, LocalConfig(getGlobal()))
        
    return _defaultCfg.get()


def setLocal(forRoot, cfg):

    """Replace local config for 'forRoot', as long as it hasn't been used"""

    forRoot = binding.getRootComponent(forRoot)

    if forRoot is None:
        _defaultCfg.set(cfg)

    elif type(forRoot).__weakrefoffset__:
        _localCfgs[forRoot] = cfg

    else:
        raise TypeError(
            "Root objects w/custom LocalConfigs must be weak-referenceable"
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

    prop = binding.findUtility(propName, obj, NOT_FOUND)

    if prop is not NOT_FOUND:
        return prop

    if default is NOT_GIVEN:
        raise exceptions.PropertyNotFound(propName, obj)

    return default












def registerGlobalProvider(ifaces, provider):
    getGlobal().registerProvider(ifaces, provider)


def setGlobalProperty(propName, value):

    pm = binding.findUtility(IPropertyMap, getGlobal())
    pm.setValue(propName, value)


def setGlobalRule(propName, ruleObj):

    pm = binding.findUtility(IPropertyMap, getGlobal())
    pm.setRule(propName, ruleObj)


def setGlobalDefault(propName, defaultObj):

    pm = binding.findUtility(IPropertyMap, getGlobal())
    pm.setDefault(propName, defaultObj)





















def registerLocalProvider(forRoot, ifaces, provider):
    getLocal(forRoot).registerProvider(ifaces, provider)


def setPropertyFor(obj, propName, value):

    pm = binding.findUtility(IPropertyMap, obj)
    pm.setValue(propName, value)


def setRuleFor(obj, propName, ruleObj):

    pm = binding.findUtility(IPropertyMap, obj)
    pm.setRule(propName, ruleObj)


def setDefaultFor(obj, propName, defaultObj):

    pm = binding.findUtility(IPropertyMap, obj)
    pm.setDefault(propName, defaultObj)



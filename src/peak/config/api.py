"""Configuration API"""

from peak.util.EigenData import *
from config_components import *
from modules import *
from interfaces import *; from interfaces import __all__ as allInterfaces
from weakref import WeakKeyDictionary

__all__ = allInterfaces + [
    'getLocal','getGlobal','setLocal','setGlobal',
    'registerLocalProvider','registerGlobalProvider',
    'GlobalConfig', 'LocalConfig', 'newDefaultConfig'
]

_globalCfg = EigenCell()
_defaultCfg = EigenCell()
_localCfgs = EigenDict()
_localCfgs.data = WeakKeyDictionary()

def getGlobal():

    if not _globalCfg.locked:
        setGlobal(GlobalConfig())

    return _globalCfg.get()

def setGlobal(cfg):
    _globalCfg.set(cfg)
    setLocal(cfg, None)     # force local config for global config to be None
    
def getLocal(forRoot=None):

    if forRoot is not None and _localCfgs.has_key(forRoot):
        return _localCfgs[forRoot]
        
    if not _defaultCfg.locked:
        setLocal(None, newDefaultConfig())

    return _defaultCfg.get()


def setLocal(forRoot, cfg):
    if forRoot is None:
        _defaultCfg.set(cfg)
    else:
        _localCfgs[forRoot] = cfg


def newDefaultConfig():
    return LocalConfig(getGlobal())


def registerLocalProvider(forRoot, ifaces, provider):
    getLocal(forRoot).registerProvider(ifaces, provider)


def registerGlobalProvider(ifaces, provider):
    getGlobal().registerProvider(ifaces, provider)


"""Configuration API"""

from peak.util.EigenData import *
from config_components import *
from weakref import WeakKeyDictionary

__all__ = [
    'getLocal','getGlobal','setLocal','setGlobal',
    'registerLocalProvider','registerGlobalProvider',
    'GlobalConfig', 'LocalConfig', 'newDefaultConfig'
]

_globalCfg = EigenCell()
_localCfgs = EigenDict()
_localCfgs.data = WeakKeyDictionary()


def getGlobal():

    if not _globalCfg.locked:
        setGlobal(GlobalConfig())

    return _globalCfg.get()


def setGlobal(cfg):
    _globalCfg.set(cfg)
    setLocal(cfg, None)     # force local config for global config to be None
    

def getLocal(forRoot):

    if forRoot is None:
        return newDefaultConfig()
        
    if not _localCfgs.data.has_key(forRoot):
        setLocal(forRoot, newDefaultConfig())

    return _localCfgs[forRoot]


def setLocal(forRoot, cfg):
    _localCfgs[forRoot] = cfg


def newDefaultConfig():
    return LocalConfig(getGlobal())

def registerLocalProvider(forRoot, ifaces, provider):
    getLocal(forRoot).registerProvider(ifaces, provider)


def registerGlobalProvider(ifaces, provider):
    getGlobal().registerProvider(ifaces, provider)


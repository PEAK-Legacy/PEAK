from __future__ import generators

from peak.api import *
from peak.util.imports import importString, importObject
from peak.binding.components import Component, New, Base, Once

from peak.util.EigenData import EigenCell, AlreadyRead
from peak.util.FileParsing import AbstractConfigParser

from interfaces import *
from Interface import Interface


__all__ = [
    'GlobalConfig', 'LocalConfig', 'PropertyMap', 'LazyLoader', 'ConfigReader',
    'loadConfigFile', 'loadMapping', 'PropertySet', 'fileNearModule',
    'Provider','CachingProvider'
]


def _setCellInDict(d,key,value):

    cell = d.get(key)

    if cell is None:
        cell = d[key] = EigenCell()

    cell.set(value)


_emptyRuleCell = EigenCell()
_emptyRuleCell.set(lambda *args: NOT_FOUND)
_emptyRuleCell.exists()


def fileNearModule(moduleName,filename):
    filebase = importString(moduleName+':__file__')
    import os; return os.path.join(os.path.dirname(filebase), filename)



class PropertyMap(Base):

    rules     = New(dict)
    provided  = New(dict)   
    _provides = IPropertyMap
    __implements__ = IPropertyMap, Base.__implements__

    def setRule(self, propName, ruleObj):
        _setCellInDict(self.rules, PropertyName(propName), ruleObj)

    def setDefault(self, propName, defaultRule):
        _setCellInDict(self.rules, PropertyName(propName+'?'), defaultRule)

    def setValue(self, propName, value):
        _setCellInDict(self.rules, PropertyName(propName), lambda *args: value)

    def registerProvider(self, ifaces, provider):

        """Register 'item' under 'implements' (an Interface or nested tuple)"""

        if isinstance(ifaces,tuple):
            for iface in ifaces:
                self.registerProvider(iface,provider)
        else:
            self._register(ifaces,provider,ifaces)

    def _register(self, iface, item, primary_iface):

        old = self.provided.get(iface)

        # We want to keep more-general registrants
        if old is None or old.extends(primary_iface, False):
        
            _setCellInDict(self.rules, iface, item)
            self.provided[iface]=primary_iface

            for base in iface.getBases():
                if base is not Interface:
                    self._register(base,item,primary_iface)


    def getValueFor(self, configKey, forObj=None):

        rules      = self._getBinding('rules')
        value      = NOT_FOUND

        if not rules:
            return value

        xRules     = []

        if isinstance(configKey,PropertyName):
            lookups = configKey.matchPatterns()
        else:
            lookups = configKey,


        for name in lookups:

            rule = rules.get(name)

            if rule is None:
                xRules.append(name)     # track unspecified rules

            elif rule is not _emptyRuleCell:

                value = rule.get()(self, configKey, forObj)

                if value is not NOT_FOUND:
                    break

        # ensure that unspecified rules stay that way, if they
        # haven't been replaced in the meanwhile by a higher-level
        # wildcard rule

        for name in xRules:
            rules.setdefault(name,_emptyRuleCell)
       
        return value

    _getConfigData = getValueFor

class LazyLoader(object):

    loadNeeded = True

    def __init__(self, loadFunc, prefix='*', **kw):
        self.load = loadFunc
        self.prefix = prefix
        self.__dict__.update(kw)


    def __call__(self, propertyMap, propName, targetObj):

        if self.loadNeeded:

            try:
                self.loadNeeded = False
                return self.load(propertyMap, self.prefix, propName)

            except:
                del self.loadNeeded
                raise

        return NOT_FOUND


















def _value(v):
    return lambda *x: v


def loadMapping(pMap, mapping, prefix='*', includedFrom=None):

    prefix = PropertyName(prefix).asPrefix()

    for k,v in mapping.items():
        pMap.registerProvider(PropertyName(prefix+k), _value(v))

loadMapping.__implements__ = ISettingLoader


def loadConfigFile(pMap, filename, prefix='*', includedFrom=None):

    if filename:
        ConfigReader(pMap,prefix).readFile(filename)

loadConfigFile.__implements__ = ISettingLoader





















class ConfigReader(AbstractConfigParser):

    def __init__(self, propertyMap, prefix='*'):
        self.pMap = propertyMap
        self.prefix = PropertyName(prefix).asPrefix()


    def add_setting(self, section, name, value, lineInfo):
        _ruleName = PropertyName(section+name)
        def f(propertyMap, propertyName, targetObj):
                ruleName = _ruleName
                return eval(value)
        self.pMap.registerProvider(_ruleName,f)


    def do_include(self, section, name, value, lineInfo):
        from api_impl import getProperty
        propertyMap = self.pMap
        loader = getProperty("peak.config.loaders."+name, propertyMap)
        loader = importObject(loader)
        eval("loader(propertyMap,%s,includedFrom=self)" % value)


    def on_demand(self, section, name, value, lineInfo):
        self.pMap.registerProvider(
            PropertyName(name),
            LazyLoader(
                lambda propertyMap, ruleName, propertyName: eval(value),
                prefix = name
            )
        )
            

    def provide_utility(self, section, name, value, lineInfo):
        self.pMap.registerProvider(importString(name), eval(value))






    section_handlers = {
        'load settings from': 'do_include',
        'provide utilities':  'provide_utility',
        'load on demand':     'on_demand',
    }


    def add_section(self, section, lines, lineInfo):

        if section is None:
            section='*'
            
        s = ' '.join(section.strip().lower().split())

        if ' ' in s:
            handler = self.section_handlers.get(s)

            if handler:
                handler = getattr(self,handler)
            else:
                raise SyntaxError("Invalid section type", section, lineInfo)
        
        else:
            section = self.prefix + PropertyName(section).asPrefix()
            handler = self.add_setting

        self.process_settings(section, lines, handler)














class BasicConfig(Component):

    def __instance_provides__(self,d,a):
        pm=PropertyMap()
        pm.setParentComponent(self)
        d[a]=pm
        self.setup(pm)
        return pm

    __instance_provides__ = Once(__instance_provides__, provides=IPropertyMap)
    

    def _getConfigData(self, configKey, forObj):
        self.__instance_provides__  # ensure existence & setup
        return super(BasicConfig,self)._getConfigData(configKey,forObj)


    def setup(self, propertyMap):
        pass
        





















class GlobalConfig(BasicConfig):

    def setup(self, propertyMap):
        loadConfigFile(propertyMap, fileNearModule('peak','peak.ini'))
            

    def setParentComponent(self,parentComponent,componentName=None):
        if parentComponent is not None or componentName is not None:
            raise TypeError("Global config can't have a parent or name")



class LocalConfig(BasicConfig):

    def setParentComponent(self,parentComponent,componentName=None):

        assert isinstance(parentComponent,GlobalConfig), \
            "LocalConfig parent must be GlobalConfig"

        super(LocalConfig,self).setParentComponent(
            parentComponent,componentName
        )



















class PropertySet(object):

    def __init__(self, prefix, targetObj=None):
        self.prefix = PropertyName(prefix).asPrefix()
        self.target = targetObj

    def __getitem__(self, key, default=NOT_GIVEN):
        return config.getProperty(self.prefix+key,self.target,default)

    def get(self, key, default=None):
        return config.getProperty(self.prefix+key,self.target,default)

    def __getattr__(self,attr):
        return self.__class__(self.prefix+attr, self.target)

    def of(self, target):
        return self.__class__(self.prefix[:-1], target)
    
    def __call__(self, default=None, forObj=NOT_GIVEN):

        if forObj is NOT_GIVEN:
            forObj = self.target

        return config.getProperty(self.prefix[:-1], forObj, default)

















def Provider(callable):
    return lambda foundIn, configKey, forObj: callable(forObj)


def CachingProvider(callable, weak=False, local=False):

    def provider(foundIn, configKey, forObj):

        if local:

            foundIn = config.getLocal(forObj)

            if foundIn is None:
                foundIn = config.getGlobal()

        else:
            # get the owner of the property map
            foundIn = binding.getParentComponent(foundIn)

        utility = provider.cache.get(foundIn)

        if utility is None:
            utility = provider.cache[foundIn] = callable(foundIn)

        return utility

    if weak:
        provider.cache = WeakValueDictionary()
    else:
        provider.cache = {}

    return provider




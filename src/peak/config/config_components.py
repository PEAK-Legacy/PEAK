from __future__ import generators

from peak.api import *
from peak.util.imports import importString, importObject
from peak.binding.components import Component, New, Base, Once

from peak.util.EigenData import EigenCell, AlreadyRead
from peak.util.FileParsing import AbstractConfigParser

from peak.naming.names import PropertyName

from interfaces import *
from Interface import Interface


__all__ = [
    'GlobalConfig', 'LocalConfig', 'PropertyMap', 'LazyLoader', 'ConfigReader',
    'loadConfigFile', 'loadMapping', 'PropSet',
]


def _setCellInDict(d,key,value):

    cell = d.get(key)

    if cell is None:
        cell = d[key] = EigenCell()

    cell.set(value)


_emptyRuleCell = EigenCell()
_emptyRuleCell.set(lambda *args: NOT_FOUND)
_emptyRuleCell.exists()







class PropertyMap(Base):

    rules     = New(dict)
    provided  = New(dict)   
    _provides = IPropertyMap


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
        if old is None or old.extends(primary_iface):
        
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
        self.prefix = PropertyName(prefix).asPrefix()
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



def loadMapping(pMap, mapping, prefix='*'):

    prefix = PropertyName(prefix).asPrefix()

    for k,v in mapping.items():
        pMap.setValue(prefix+k, v)


def loadConfigFile(pMap, filename, prefix='*'):
    if filename:
        ConfigReader(pMap,prefix).readFile(filename)




class ConfigReader(AbstractConfigParser):

    def __init__(self, propertyMap, prefix='*'):
        self.pMap = propertyMap
        self.prefix = PropertyName(prefix).asPrefix()

    def add_setting(self, section, name, value, lineInfo):
        _ruleName = section+name
        def f(propertyMap, propertyName, targetObj):
                ruleName = _ruleName
                return eval(value)
        self.pMap.setRule(_ruleName,f)

    def do_include(self, section, name, value, lineInfo):
        from api_impl import getProperty
        propertyMap = self.pMap
        loader = getProperty("peak.config.loaders."+name, propertyMap)
        loader = importObject(loader)
        eval("loader(propertyMap,%s)" % value)


    def provide_utility(self, section, name, value, lineInfo):
        self.pMap.registerProvider(importString(name), eval(value))

    def add_section(self, section, lines, lineInfo):
        if section is None:
            section='*'
            
        s = ' '.join(section.strip().lower().split())

        if s=='load settings from':
            handler = self.do_include
        elif s=='provide utilities':
            handler = self.provide_utility
        else:
            section = self.prefix + PropertyName(section).asPrefix()
            handler = self.add_setting

        self.process_settings(section, lines, handler)


class GlobalConfig(Component):

    def __init__(self):
        pass

    def startup(self):
        self.setup(self.__instance_provides__)
    
    def config_filenames(self,d,a):
        import os; from peak import __file__ as filebase
        return [os.path.join(os.path.dirname(filebase), 'peak.ini')]

    config_filenames = Once(config_filenames)

        
    def setup(self, propertyMap):

        for file in self.config_filenames:
            loadConfigFile(propertyMap, file)
            

    def setParentComponent(self,parent):
        raise TypeError("Global config can't have a parent")


















class LocalConfig(Component):

    def __init__(self,parent):
        self.setParentComponent(parent)

    def startup(self):
        self.setup(self.__instance_provides__)

    def setup(self, propertyMap):
        pass

    def setParentComponent(self,parent):

        assert isinstance(parent,GlobalConfig), \
            "LocalConfig parent must be GlobalConfig"

        super(LocalConfig,self).setParentComponent(parent)


class PropSet(object):

    def __init__(self, prefix, targetObj=None):
        self.prefix = PropertyName(prefix).asPrefix()
        self.target = targetObj

    def __getitem__(self, key, default=NOT_GIVEN):
        return config.getProperty(self.prefix+key,self.target,default)

    def get(self, key, default=None):
        return config.getProperty(self.prefix+key,self.target,default)

from __future__ import generators

from peak.binding.components import Component, New, Base, Provider, Once

from peak.api import NOT_FOUND, NOT_GIVEN
from peak.util.EigenData import EigenCell, AlreadyRead

from peak.naming.names import PropertyName

from interfaces import *
from Interface import Interface

__all__ = [
    'GlobalConfig', 'LocalConfig', 'PropertyMap', 'LoadingRule', 'ConfigFile',
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


    def setRule(self, propName, ruleFactory):
        ruleObj = ruleFactory(self, propName)
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

        rules      = self.getBindingIfPresent('rules')
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

class LoadingRule(object):

    def __init__(self, loadFunc, **kw):
        self.load = loadFunc
        self.__dict__.update(kw)

    def __call__(self, propertyMap, propName):

        mask = propName

        assert mask.endswith('*'), "LoadingRules are for wildcard rules only"
        prefix = mask[:-1]

        if prefix and not prefix.endswith('.'):
            prefix+='.'
        
        def compute(propertyMap, propName, targetObj):

            if compute.loadNeeded:

                try:
                    compute.loadNeeded = False
                    return self.load(self, propertyMap, prefix, propName)
                except:
                    compute.loadNeeded = True
                    raise

            return NOT_FOUND

        compute.loadNeeded = True
        return compute


def loadEnviron(factory, pMap, prefix, name):
    from os import environ

    for k,v in environ.items():
        pMap.setValue(prefix+k, v)

    return NOT_FOUND

class ConfigFile(object):

    def __init__(self, filenames):
        self.filenames = filenames

    def __call__(self, factory, pMap, prefix, name):

        # load from config file
        from ConfigParser import ConfigParser
        cp = self.cp = ConfigParser()
        cp.optionxform = str
        cp.read(self.filenames)
        options, get = cp.options, cp.get

        for section in cp.sections():

            section = section.strip()

            if section and not section.endswith('.'):
                sp = prefix + section + '.'
            else:
                sp = prefix + section

            for opt in options(section):
                pMap.setValue(sp+opt, eval(get(section,opt,1)))

        return NOT_FOUND














class GlobalConfig(Component):

    def __init__(self):
        self.setup(self.__instance_provides__)

    def config_filenames(self,d,a):
        import os; from peak import __file__ as filebase
        return [os.path.join(os.path.dirname(filebase), 'peak.ini')]

    config_filenames = Once(config_filenames)

        
    def setup(self, propertyMap):
        
        propertyMap.setRule(
            'environ.*', LoadingRule(loadEnviron)
        )

        propertyMap.setRule(
            '*', LoadingRule(ConfigFile(self.config_filenames))
        )

        from peak.naming import factories

        propertyMap.registerProvider(
            factories.__implements__, Provider(lambda *x: factories)
        )


    def setParentComponent(self,parent):
        raise TypeError("Global config can't have a parent")










class LocalConfig(Component):

    def __init__(self,parent):
        self.setParentComponent(parent)
        self.setup()

    def setup(self):
        pass

    def setParentComponent(self,parent):

        assert isinstance(parent,GlobalConfig), \
            "LocalConfig parent must be GlobalConfig"

        super(LocalConfig,self).setParentComponent(parent)



from __future__ import generators

from peak.binding.components import Component, New, AutoCreated

from peak.api import NOT_FOUND, NOT_GIVEN
from peak.util.EigenData import EigenCell, AlreadyRead

from interfaces import *
from Interface import Interface

__all__ = [
    'GlobalConfig', 'LocalConfig', 'PropertyMap', 'LoadingRule',
]


def _setCellInDict(d,key,value):

    cell = d.get(key)

    if cell is None:
        cell = d[key] = EigenCell()

    cell.set(value)


_emptyRuleCell = EigenCell()
_emptyRuleCell.set(lambda *args: NOT_FOUND)
_emptyRuleCell.exists()













class PropertyMap(AutoCreated):

    rules     = New(dict)
    provided  = New(dict)   
    _provides = IPropertyMap


    def setRule(self, propName, ruleFactory):
        ruleObj = ruleFactory(self, propName)
        _setCellInDict(self.rules, Property(propName), ruleObj)

    def setDefault(self, propName, defaultRule):
        _setCellInDict(self.rules, Property(propName+'?'), defaultRule)

    def setValue(self, propName, value):
        _setCellInDict(self.rules, Property(propName), lambda *args: value)

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

        rules      = self.rules
        value      = NOT_FOUND

        if not rules:
            return value

        xRules     = []

        if isinstance(configKey,Property):
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

class GlobalConfig(Component):

    def __init__(self):
        self.setup()

    def setup(self):
        self.__instance_provides__.setRule(
            'environ.*', LoadingRule(loadEnviron)
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



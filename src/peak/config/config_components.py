from __future__ import generators

from peak.binding.components import Component, getRootComponent, New, \
    AutoCreated

from peak.api import NOT_FOUND
from peak.util.EigenData import EigenCell, AlreadyRead
from interfaces import *


__all__ = [
    'GlobalConfig', 'LocalConfig', 'PropertyMap'
]


def _enumWildcards(name):

    yield name

    while '.' in name:
        name = name[:name.rindex('.')-1]
        yield name+'*'

    yield '*'


def _setCellInDict(d,key,value):

    cell = d.get(key)

    if cell is None:
        cell = d[key] = EigenCell()

    cell.set(value)


_emptyRuleCell = EigenCell()
_emptyRuleCell.set(lambda *args: NOT_FOUND)
_emptyRuleCell.exists()


class PropertyMap(AutoCreated):

    values   = New(dict)
    rules    = New(dict)
    defaults = New(dict)

    _provides = IPropertyMap

    def setRule(self, propName, ruleObj):
        if self.values.has_key(propName): raise AlreadyRead
        _setCellInDict(self.rules, propName, ruleObj)

    def setDefault(self, propName, defaultRule):
        _setCellInDict(self.defaults, propName, defaultRule)

    def setPropertyFor(self, obj, propName, value):
        if obj is not self.getParentComponent():
            raise ObjectOutOfScope(
                "PropertyMap only sets properties for its parent"
            )
        _setCellInDict(self.values, propName, value)


    def getPropertyFor(self, obj, propName):

        cell = self.values.get(propName)

        if cell is not None:
            return cell.get()

        rules      = self.rules
        defaults   = self.defaults

        # Initialize loop invariants
        
        rulesUsed  = False
        value      = NOT_FOUND
        xRules     = []
        xDefaults  = []


        for name in _enumWildcards(propName):

            rule = rules.get(name)

            if rule is None:
                xRules.append(name)

            elif rule is not _emptyRuleCell:
                rulesUsed = True
                value = rule.get()(self, propName, obj)
                if value is not NOT_FOUND: break

            default = rules.get(name)

            if default is None:
                xDefaults.append(name)

            elif default is not _emptyRuleCell:
                value = default.get()(self, propName)
                if value is not NOT_FOUND: break


        # ensure that undefined rules/defaults stay that way, if they
        # haven't been replaced in the meanwhile by a higher-level
        # wildcard rule

        for name in xDefaults: defaults.setdefault(name,emptyRuleCell)
        for name in xRules:       rules.setdefault(name,emptyRuleCell)

        if rulesUsed:
            return value


        # If no non-null rules were used, then the value we found is
        # independent of the target object: we can cache it in the values map!

        cell = self.values[propName] = EigenCell()
        cell.set(value)

        return cell.get()

class GlobalConfig(Component):

    propertyMap = PropertyMap

    def _getUtility(self, iface, forObj):

        # use the global configuration registry, but wrap anything found
        # around forObj's local config, so that it has access to the local
        # configuration, and will be specific to that configuration root.

        provider = self.__instance_provides__.get(iface)

        if provider is not None:

            if forObj is self:
                raise TypeError(
                    "Global config can't provide utilities for itself"
                )

            from api import getLocal
            localCfg = getLocal(getRootComponent(forObj))
            return provider(localCfg, forObj)

        return super(GlobalConfig,self)._getUtility(iface, forObj)


    def setParentComponent(self,parent):
        raise TypeError("Global config can't have a parent")













class LocalConfig(Component):

    propertyMap = PropertyMap

    def __init__(self,parent):
        self.setParentComponent(parent)

    def setParentComponent(self,parent):

        assert isinstance(parent,GlobalConfig), \
            "LocalConfig parent must be GlobalConfig"

        super(LocalConfig,self).setParentComponent(parent)


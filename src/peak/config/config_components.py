from __future__ import generators

from peak.binding.components import Component, getRootComponent, New, \
    AutoCreated

from peak.api import NOT_FOUND, NOT_GIVEN
from peak.util.EigenData import EigenCell, AlreadyRead
from interfaces import *


__all__ = [
    'GlobalConfig', 'LocalConfig', 'PropertyMap', 'LoadingRule',
]


def _enumWildcards(name):

    yield name

    while '.' in name:
        name = name[:name.rindex('.')]
        yield name+'.*'

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
    used     = New(dict)

    _provides = IPropertyMap


    def setRule(self, propName, ruleFactory):

        ruleObj = ruleFactory(self, propName)

        if propName in self.values or propName in self.used:
            raise AlreadyRead, propName

        _setCellInDict(self.rules, propName, ruleObj)


    def setDefault(self, propName, defaultRule):

        _setCellInDict(self.defaults, propName, defaultRule)


    def setPropertyFor(self, obj, propName, value):

        if obj is not None and obj is not self.getParentComponent():
            raise ObjectOutOfScope(
                "PropertyMap only sets properties for its parent"
            )

        if propName in self.used:
            raise AlreadyRead, propName

        _setCellInDict(self.values, propName, value)





    def getPropertyFor(self, obj, propName):

        # First we try values
        
        cell = self.values.get(propName)

        if cell is not None:
            return cell.get()
            
        # Initialize loop invariants
        
        rules      = self.rules
        xRules     = []
        rulesUsed  = False
        value      = NOT_FOUND


        # Check regular & wildcard rules
        
        for name in _enumWildcards(propName):

            rule = rules.get(name)

            if rule is None:
                xRules.append(name)     # track unspecified rules

            elif rule is not _emptyRuleCell:

                value = rule.get()(propName, obj)

                if value is NOT_GIVEN:
                    value = NOT_FOUND
                    continue
                    
                rulesUsed = True    # we depended on the rule's return value

                if value is not NOT_FOUND:
                    break



        # ensure that unspecified rules stay that way, if they
        # haven't been replaced in the meanwhile by a higher-level
        # wildcard rule

        for name in xRules:
            rules.setdefault(name,_emptyRuleCell)


        if value is NOT_FOUND:

            # Rules didn't work, or else they loaded something
            # let's try values again, then defaults...

            cell = self.values.get(propName)

            if cell is not None:
                return cell.get()

            default = self.defaults.setdefault(propName, _emptyRuleCell)
            value = default.get()(self, propName)


        # prevent setting a value for this property in future
        self.used.setdefault(propName,1)    

        
        if rulesUsed:
            return value

        # If no non-null rules were used, then the value we found is
        # independent of the target object: we can cache it in the values map!

        cell = self.values[propName] = EigenCell()
        cell.set(value)

        return cell.get()





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
        
        def compute(propName,targetObj):

            if compute.loadNeeded:

                try:
                    compute.loadNeeded = False
                    return self.load(self, propertyMap, prefix, propName)
                except:
                    compute.loadNeeded = True
                    raise

            return NOT_GIVEN

        compute.loadNeeded = True
        return compute


def loadEnviron(factory, pMap, prefix, name):
    from os import environ

    for k,v in environ.items():
        pMap.setPropertyFor(None, prefix+k, v)

    return NOT_GIVEN

class GlobalConfig(Component):

    propertyMap = PropertyMap

    def __init__(self):
        self.propertyMap.setRule('environ.*', LoadingRule(loadEnviron))


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


from __future__ import generators

from peak.binding.components import Component, getRootComponent, New, \
    AutoCreated

from peak.api import NOT_FOUND
from peak.util.EigenData import EigenCell, EigenDict
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



UnfoundCell = EigenCell()
UnfoundCell.set(NOT_FOUND)
UnfoundCell.exists()











class PropertyMap(AutoCreated):

    values   = New(dict)
    rules    = New(EigenDict)
    defaults = New(EigenDict)

    _provides = IPropertyMap


    def setRule(self, propName, ruleObj):
        self.rules[propName] = ruleObj


    def setDefault(self, propName, ruleObj):
        self.defaults[propName] = ruleObj


    def setProperty(self, propName, value):

        cell = self.values.get(propName)

        if cell is None:
            cell = self.values[propName] = EigenCell()

        cell.set(value)


    def getPropertyFor(self, obj, propName):

        cell = self.values.get(propName)

        if cell is not None:
            return cell.get()

        cell = self.values[propName] = UnfoundCell  # XXX

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


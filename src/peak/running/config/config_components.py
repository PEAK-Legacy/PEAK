from peak.api import NOT_FOUND
from peak.binding.components import Component, getRootComponent

__all__ = ['GlobalConfig', 'LocalConfig']

class GlobalConfig(Component):

    def _getUtility(self, iface, forObj):

        if forObj is self:
            raise TypeError("Global config can't provide utilities for itself")

        # use the global configuration registry, but wrap anything found
        # around forObj's local config, so that it has access to the local
        # configuration, and will be specific to that configuration root.
        
        provider = self.__instance_provides__.get(iface)
        
        if provider is not None:
            from api import getLocal
            localCfg = getLocal(getRootComponent(forObj))
            return provider(localCfg, forObj)


    def setParentComponent(self,parent):
        raise TypeError("Global config can't have a parent")


class LocalConfig(Component):

    def __init__(self,parent):
        self.setParentComponent(parent)

    def setParentComponent(self,parent):

        assert isinstance(parent,GlobalConfig), \
            "LocalConfig parent must be GlobalConfig"

        super(LocalConfig,self).setParentComponent(parent)
    

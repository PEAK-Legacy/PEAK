from peak.api import NOT_FOUND
from peak.binding.components import Component

__all__ = ['GlobalConfig', 'LocalConfig']


class GlobalConfig(Component):

    def acquireUtility(self, iface, forObj=None, localLookup=True):
        raise TypeError("Global config doesn't support 'acquireUtility'")

    def setParentComponent(self,parent):
        raise TypeError("Global config can't have a parent")



class LocalConfig(Component):

    def __init__(self,parent):
        self.setParentComponent(parent)


    def setParentComponent(self,parent):

        assert isinstance(parent,GlobalConfig), \
            "LocalConfig parent must be GlobalConfig"

        super(LocalConfig,self).setParentComponent(parent)













    def acquireUtility(self, iface, forObj=None, localLookup=True):

        if forObj is None:
            forObj=self

        if localLookup:
        
            provider = self.__instance_provides__.get(iface)
            
            if provider is not None:
                return provider(self,forObj)

            attr = self.__class_provides__.get(iface)

            if attr is not None:

                utility = getattr(self,attr)

                if utility is not NOT_FOUND:
                    return utility


        # use our global configuration's registry, but wrap anything
        # found around ourself, so that it has access to the local
        # configuration, and will be specific to this configuration
        # root.
        
        provider = self.getParentComponent().__instance_provides__.get(iface)
            
        if provider is not None:
            return provider(self,forObj)
        

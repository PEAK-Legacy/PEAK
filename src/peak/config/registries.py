from __future__ import generators
from peak.api import *
from interfaces import *
from peak.util.EigenData import EigenDict
from peak.util.imports import whenImported

__all__ = [ 'EigenRegistry' ]


class InterfaceAsConfigKey(protocols.Adapter):

    """Adapt interfaces to configuration keys"""

    protocols.advise(
        instancesProvide=[IConfigKey],
        asAdapterForTypes=[protocols.Interface.__class__],
    )

    def registrationKeys(self, depth=0):
        """Iterate over (key,depth) pairs to be used when registering"""
        yield self.subject, depth
        depth += 1
        for base in self.subject.getBases():
            for item in adapt(base,IConfigKey).registrationKeys(depth):
                yield item

    def lookupKeys(self):
        """Iterate over keys that should be used for lookup"""
        return self.subject,


whenImported('zope.interface',
    lambda interface: (
        protocols.declareAdapter(
            InterfaceAsConfigKey, provides=[IConfigKey],
            forTypes = [interface.Interface.__class__]
        )
    )
)


class EigenRegistry(EigenDict):

    """EigenDict that takes IConfigKey objects as keys, handling inheritance"""

    def __init__(self):
        self.depth = {}
        super(EigenRegistry,self).__init__()

    def lookup(self, configKey, failobj=None):
        sc = self._setCell
        for key in configKey.lookupKeys():
            cell = sc(key)
            if cell.exists():
                return cell.get()
        else:
            return failobj

    def register(self, configKey, item, depth=0):
        """Register 'item' under 'configKey'"""
        for key,depth in adapt(configKey,IConfigKey).registrationKeys():
            if self.depth.get(key,depth)>=depth:
                self[key]=item
                self.depth[key] = depth

    def update(self,other):
        """Conservatively merge in another EigenRegistry"""

        if not isinstance(other,EigenRegistry):
            raise TypeError("Not an EigenRegistry", other)

        mydepth = self.depth
        get = mydepth.get
        sc = self._setCell
        for iface, depth in other.depth.items():
            old = get(iface,depth)
            if old>=depth:
                sc(iface).set(other[iface])
                mydepth[iface] = depth



    def setdefault(self,key,failobj=None):
        raise NotImplementedError

    def __delitem__(self,key):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


































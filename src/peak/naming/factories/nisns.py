from __future__ import generators
from peak.api import *
from peak.naming.contexts import AbstractContext
from peak.naming.names import CompoundName
import nis


class nisURL(naming.ParsedURL):
    _defaultScheme = 'nis'
    
    _supportedSchemes = ('nis', )

    pattern = "((?P<mapname>[^/]+)(/(?P<key>.+)?)?)?"


class nisURLContext(AbstractContext):
    __implements__ = naming.IReadContext

    schemeParser = nisURL

    def __iter__(self):
        for map in nis.maps():
            yield nisURL(body=map)
            
    def _get(self, name, retrieve=1):
        if not name.body:
            return self, None

        mapname = getattr(name, 'mapname', 'passwd.byname')
        key = getattr(name, 'key', None)
        
        mapns = nisMapContext(mapname)
        if key:
            r = mapns.get(key, NOT_FOUND)
            if r:
                return r, None
            else:
                return NOT_FOUND
        else:
            return mapns, None

        
class nisMapContext(AbstractContext):
    __implements__ = naming.IReadContext

    nameClass = CompoundName
    
    def __init__(self, mapname):
        self.mapname = mapname

    def __iter__(self):
        return iter(nis.cat(self.mapname))

    def _get(self, name, retrieve=1):
        try:
            return nis.match(str(name), self.mapname), None
        except nis.error:
            return NOT_FOUND

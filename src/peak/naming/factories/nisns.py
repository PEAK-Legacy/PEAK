from __future__ import generators
from peak.api import *
import nis


class nisURL(naming.URL.Base):

    supportedSchemes = 'nis',
    nameAttr = 'body'


class nisURLContext(naming.NameContext):

    implements(naming.IReadContext)

    schemeParser = nisURL


    def __iter__(self):
        for map in nis.maps():
            yield self.compoundParser(map)


    def _get(self, name, retrieve=1):

        if not name:
            return self, None

        elif str(name) in nis.maps():
            return nisMapContext(
                namingAuthority = self.namingAuthority,
                nameInContext   = self.nameInContext + name,
            ), None

        else:
            return NOT_FOUND





class nisMapContext(naming.NameContext):

    implements(naming.IReadContext)

    mapname = binding.Once(lambda s,d,a: str(s.nameInContext))


    def __iter__(self):
        for key in nis.cat(self.mapname):
            yield self.compoundParser(key)


    def _get(self, name, retrieve=1):

        try:
            return nis.match(str(name), self.mapname), None

        except nis.error:
            return NOT_FOUND























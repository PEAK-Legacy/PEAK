from peak.naming.api import *
from peak.naming.contexts import AbstractContext
from peak.binding.imports import importString

from types import StringTypes


class importContext(AbstractContext):

    _supportedSchemes = ('import', )


    def _makeName(self, name):

        if isinstance(name,StringTypes):
            return OpaqueURL( ('import',name) )

        return name        


    def _get(self, name, default=None, retrieve=1):

        if retrieve:
            return (RefAddr('PEAK Import Specifier', name.body), None)

        else:
            return name


def importFactory(refInfo, name, context, environment, attrs=None):
    return importString(refInfo.content)

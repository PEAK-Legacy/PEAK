from peak.naming.api import *
from peak.naming.contexts import AbstractContext
from peak.binding.imports import importString

from types import StringTypes


class importURL(OpaqueURL):

    def _defaultObjectFactory(self, refInfo, name, context, environment, attrs=None):
        return importString(refInfo.body)

    def fromURL(klass, name):
        return OpaqueURL.__new__(klass, name)

    fromURL = classmethod(fromURL)

from peak.naming.api import *
from peak.naming.contexts import AbstractContext
from peak.util.imports import importString

from types import StringTypes


class importURL(ParsedURL):

    _supportedSchemes = 'import',

    def retrieve(self, refInfo, name, context, attrs=None):
        return importString(self.body)



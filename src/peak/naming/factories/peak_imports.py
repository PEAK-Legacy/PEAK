from peak.naming.api import *
from peak.util.imports import importString

from types import StringTypes


class importURL(ParsedURL):

    _defaultScheme = 'import'

    _supportedSchemes = 'import',

    def retrieve(self, refInfo, name, context, attrs=None):
        return importString(self.body)



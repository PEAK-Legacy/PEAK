from peak.naming.api import *
from peak.util.imports import importString


class importURL(URL.Base):

    supportedSchemes = 'import',

    def retrieve(self, refInfo, name, context, attrs=None):
        return importString(self.body)



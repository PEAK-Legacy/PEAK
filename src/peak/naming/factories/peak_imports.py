from peak.api import *
from peak.naming.api import *
from peak.util.imports import importString


class importURL(URL.Base):

    supportedSchemes = 'import',

    def retrieve(self, refInfo, name, context, attrs=None):
        return importString(self.body)


class importContext(naming.AddressContext):

    schemeParser = importURL

    def _get(self, name, retrieve=1):

        if not name:
            return self, None

        try:
            return importString(name.body), None
        except ImportError:
            return NOT_FOUND


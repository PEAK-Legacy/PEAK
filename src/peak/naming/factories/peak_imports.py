from peak.api import *
from peak.naming.api import *
from peak.util.imports import importString


class importURL(URL.Base):

    supportedSchemes = 'import',


class importContext(naming.AddressContext):

    schemeParser = importURL

    def _get(self, name, retrieve=1):

        try:
            return importString(name.body), None
        except ImportError:
            return NOT_FOUND


from peak.naming.api import *
from peak.util.uuid import UUID


class uuidURL(ParsedURL):
    """
    draft-kindel-uuid-uri-00 UUID urls
    
    Attributes provided:

    uuid            a peak.util.uuid object
    quals           a list of (key, value) pairs of qualifiers
                    note that the meaning, syntax, and use of
                    qualifiers is not well defined.
    """
    
    _supportedSchemes = ('uuid', )
    
    def _fromURL(self, url):
        l = self.body.split(';')
        
        try:
            self.uuid = UUID(l[0])
        except:
            raise InvalidNameException(url)

        self.quals = [tuple(x.split('=', 1)) for x in l[1:]]

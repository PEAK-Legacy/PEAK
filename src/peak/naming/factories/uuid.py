from peak.naming.api import *
from peak.util.uuid import UUID
from peak.api import exceptions

class uuidURL(ParsedURL):
    """
    draft-kindel-uuid-uri-00 UUID urls
    
    Attributes provided:

    uuid            a peak.util.uuid object
    quals           a tuple of (key, value) pairs of qualifiers
                    note that the meaning, syntax, and use of
                    qualifiers is not well defined.
    """

    _supportedSchemes = ('uuid', )

    def __init__(self, url=None,scheme=None,body=None,uuid=None,quals=None):
        self.setup(locals())
    
    def parse(self, scheme, body):

        l = body.split(';')
        
        try:
            uuid = UUID(l[0])
        except:
            raise exceptions.InvalidName(self.url)

        quals = tuple( [tuple(x.split('=', 1)) for x in l[1:]] )

        return locals()



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

    _defaultScheme = 'uuid'

    _supportedSchemes = ('uuid', )


    def __init__(self, url=None, uuid=None, quals=None):
        self.setup(locals())


    def parse(self, scheme, body):

        _l = body.split(';')
        
        uuid = UUID(_l[0])

        quals = tuple( [tuple(_x.split('=', 1)) for _x in _l[1:]] )

        return locals()



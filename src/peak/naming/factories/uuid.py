from peak.naming.api import *
from peak.util.uuid import UUID
from peak.api import model

class uuidURL(ParsedURL):
    """
    draft-kindel-uuid-uri-00 UUID urls

    Attributes provided:

    uuid            a peak.util.uuid object
    quals           a tuple of (key, value) pairs of qualifiers
                    note that the meaning, syntax, and use of
                    qualifiers is not well defined.
    """

    supportedSchemes = 'uuid',

    class quals(model.structField):
        upperBound = None
        defaultValue = ()
        referencedType = model.Any

    class uuid(model.structField):
        class referencedType(model.String):
            def mdl_normalize(klass,value):
                return UUID(value)


    def parse(self, scheme, body):
        _l = body.split(';')
        return {
            'uuid':  UUID(_l[0]),
            'quals': tuple([ tuple(v.split('=',1)) for v in _l[1:] ])
        }



from structural import PrimitiveType, Enumeration

__all__ = [
    'Integer','UnlimitedInteger','UNBOUNDED','Boolean','String','Name'
]


UNBOUNDED = -1


class UnlimitedInteger(PrimitiveType):

    def fromString(klass, value):
        if value=='*': return UNBOUNDED
        return int(value)

    fromString = classmethod(fromString)


class Integer(PrimitiveType):

    fromString = int


class Boolean(Enumeration):
    true = 1; false = 0


class String(PrimitiveType):
    pass


class Name(PrimitiveType):
    pass


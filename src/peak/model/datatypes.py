from structural import PrimitiveType
from enumerations import Enumeration, enum

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
    true = enum(True)
    false = enum(False)


class String(PrimitiveType):

    def fromString(klass,value):
        return value

    fromString = classmethod(fromString)


class Name(String):
    pass


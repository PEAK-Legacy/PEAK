from structural import PrimitiveType, DataType, structField
from enumerations import Enumeration, enum

__all__ = [
    'Integer','UnlimitedInteger','UNBOUNDED','Boolean','String','Name',
    'TCKind',
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

class SimpleTC(Enumeration):

    """Simple (i.e. atomic/unparameterized) CORBA typecode kinds"""
    
    tk_short = enum()
    tk_long  = enum()
    tk_ushort = enum()
    tk_ulong = enum()
    tk_float = enum()
    tk_double = enum()

    tk_boolean = enum()
    tk_char = enum()
    tk_wchar = enum()
    tk_octet = enum()

    tk_any   = enum()
    tk_TypeCode = enum()
    tk_Principal = enum()
    tk_null = enum()
    tk_void = enum()
    
    tk_longlong = enum()
    tk_ulonglong = enum()
    tk_longdouble = enum()
















class TCKind(SimpleTC):

    """The full set of CORBA TypeCode kinds"""

    tk_alias = enum()       # content_type

    tk_array = enum()       # length + content_type
    tk_sequence = enum()

    tk_string = enum()      # length
    tk_wstring = enum()

    tk_enum = enum()        # member names

    tk_struct = enum()      # member names + types
    tk_except = enum()

    tk_union = enum()       # member names + types + discriminator

    tk_fixed = enum()       # digits + scale

    tk_objref = enum()


    # J2SE also defines these...  presumably they come from a newer CORBA
    # spec than XMI 1.0 uses?  Or maybe they just aren't useful for XMI?
    #
    # tk_abstract_interface
    # tk_native
    # tk_value
    # tk_value_box










class _tcField(structField):

    """TypeCode field that only allows itself to be set when relevant"""

    allowedKinds = ()

    sortPosn = 1    # all fields must sort *after* 'kind'

    def _onLink(feature,element,item,posn):
        if element.kind not in feature.allowedKinds:
            raise TypeError(
                "%s may not be set for TypeCode of kind %r" %
                (feature.attrName, element.kind)
            )



























class TypeCode(DataType):

    # XXX name, id ???

    class kind(structField):
        referencedType = TCKind
        sortPosn = 0

    class length(_tcField):     # xmi.tcLength

        allowedKinds = (
            TCKind.tk_array, TCKind.tk_sequence, TCKind.tk_string,
            TCKind.tk_wstring,
        )

        referencedType = Integer


    class content_type(_tcField):
        allowedKinds = (
            TCKind.tk_array, TCKind.tk_sequence, TCKind.tk_alias,
        )
        referencedType = 'TypeCode'


    class member_names(_tcField):   # XMI.CorbaTcEnumLabel/XMI.CorbaTcField
        allowedKinds = (
            TCKind.tk_enum, TCKind.tk_struct, TCKind.tk_except, TCKind.tk_union
        )
        upperBound = None   # sequence
        referencedType = Name


    class member_types(_tcField):   # XMI.CorbaTcField
        allowedKinds = (
            TCKind.tk_struct, TCKind.tk_except, TCKind.tk_union
        )
        upperBound = None   # sequence
        referencedType = 'TypeCode'


    class discriminator_type(_tcField):
        allowedKinds = TCKind.tk_union,
        referencedType = 'TypeCode'

    class member_labels(_tcField):
        allowedKinds = TCKind.tk_union,
        referencedType = 'Any'

    class fixed_digits(_tcField):   # xmi.tcDigits
        allowedKinds = TCKind.tk_fixed,
        referencedType = Integer

    class fixed_scale(fixed_digits):    # xmi.tcScale
        pass





TypeCode.mdl_typeCode = TypeCode(kind=TCKind.tk_TypeCode)

Integer.mdl_typeCode  = TypeCode(kind=TCKind.tk_longlong)

Boolean.mdl_typeCode  = TypeCode(kind=TCKind.tk_boolean)

String.mdl_typeCode   = TypeCode(kind=TCKind.tk_string)

Name.mdl_typeCode     = TypeCode(kind=TCKind.tk_alias,
                                 content_type=String.mdl_typeCode)



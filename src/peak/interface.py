"""Trivial Interfaces and Adaptation"""

__all__ = [
    'IMPLEMENTATION_ERROR','NO_ADAPTER_NEEDED','DOES_NOT_SUPPORT',
    'adapt', 'Protocol', 'InterfaceClass', 'Interface', 'implyProtocols',
    'implements', 'doesNotImplement', 'classProvides', 'metamethod',
    'directlyProvides', 'moduleProvides', 'instancesProvide', 'Attribute',
]


# Intrinsic Adapters

def IMPLEMENTATION_ERROR(obj, protocol):
    """Raise 'NotImplementedError' when adapting 'obj' to 'protocol'"""
    raise NotImplementedError("Can't adapt", obj, protocol)

def NO_ADAPTER_NEEDED(obj, protocol):
    """Assume 'obj' implements 'protocol' directly"""
    return obj

def DOES_NOT_SUPPORT(obj, protocol):
    """Prevent 'obj' from supporting 'protocol'"""
    return None


# Other miscellaneous stuff we need

_marker = object()
from sys import _getframe, exc_info, modules

from types import ClassType
ClassTypes = ClassType, type

from peak.util.advice import addClassAdvisor

def metamethod(func):
    """Wrapper for metaclass method that might be confused w/instance method"""
    return property(lambda ob: func.__get__(ob,ob.__class__))



def adapt(obj, protocol, default=_marker, factory=IMPLEMENTATION_ERROR):

    """PEP 246-alike: Adapt 'obj' to 'protocol', return 'default'

    If 'default' is not supplied and no implementation is found,
    the result of 'factory(obj,protocol)' is returned.  If 'factory'
    is also not supplied, 'NotImplementedError' is then raised."""

    if isinstance(protocol,ClassTypes) and isinstance(obj,protocol):
        return obj

    try:
        _conform = obj.__conform__
    except AttributeError:
        pass
    else:
        try:
            result = _conform(protocol)
            if result is not None:
                return result
        except TypeError:
            if exc_info()[2].tb_frame is not _getframe():
                raise

    try:
        _adapt = protocol.__adapt__
    except AttributeError:
        pass
    else:
        try:
            result = _adapt(obj)
            if result is not None:
                return result
        except TypeError:
            if exc_info()[2].tb_frame is not _getframe():
                raise

    if default is _marker:
        return factory(obj, protocol)
    return default

# Trivial interface implementation

class Protocol:
    """Generic protocol w/type-based adapter registry"""

    def __init__(self):
        self.__adapters__ = {}

    def getImpliedProtocols(self):
        return self.__dict__.get('__implies__',())

    def addImpliedProtocol(self,proto):
        old = self.__dict__.get('__implies__',())
        self.__implies__ = old+(proto,)

    def registerImplementation(self, klass, adapter=NO_ADAPTER_NEEDED):
        self.__adapters__[klass] = adapter
        for proto in self.getImpliedProtocols():
            proto.registerImplementation(klass,adapter)

    def registerNonImplementation(self, klass):
        self.__adapters__[klass] = DOES_NOT_SUPPORT

    def __adapt__(self, obj):
        get = self.__adapters__.get
        try:
            typ = obj.__class__
        except AttributeError:
            typ = type(obj)

        for klass in typ.__mro__:
            factory=get(klass)
            if factory is not None:
                return factory(obj,self)
        # return None

    __adapt__ = metamethod(__adapt__)




class InterfaceClass(Protocol, type):

    def __init__(self, __name__, __bases__, __dict__):
        type.__init__(self, __name__, __bases__, __dict__)
        Protocol.__init__(self)

    def getImpliedProtocols(self):
        return [
            b for b in self.__bases__
                if isinstance(b,Protocol) and b is not Interface
        ] + list(super(InterfaceClass,self).getImpliedProtocols())

    getBases = getImpliedProtocols  # XXX

    def isImplementedBy(self,ob):   # XXX
        return adapt(ob,self,None) is not None

    def isImplementedByInstancesOf(self,klass): # XXX
        get = self.__adapters__.get
        for klass in klass.__mro__:
            factory=get(klass)
            if factory is None:
                continue
            elif factory is DOES_NOT_SUPPORT:
                return False
            elif factory is NO_ADAPTER_NEEDED:
                return True


class Interface(object):
    __metaclass__ = InterfaceClass










# Interface declaration

def implements(*protocols):

    def callback(klass):
        instancesProvide(klass, *protocols)
        return klass

    addClassAdvisor(callback)


def doesNotImplement(*protocols):

    def callback(klass):
        for p in protocols:
            adapt(p,Protocol).registerNonImplementation(klass)

        return klass

    addClassAdvisor(callback)


def classProvides(*protocols):

    def callback(klass):
        meta = klass.__class__
        for base in klass.__bases__:
            if isinstance(base, meta):
                raise TypeError(
                    "Class must have its own metaclass to use classProvides",
                    klass, meta
                )
        for p in protocols:
            adapt(p,Protocol).registerImplementation(meta)
        return klass

    addClassAdvisor(callback)




def implyProtocols(*protocols):

    def callback(klass):

        _klass = adapt(klass,Protocol)

        for p in protocols:
            _klass.addImpliedProtocol(adapt(p,Protocol))

        return klass

    addClassAdvisor(callback)


def directlyProvides(ob, *protocols):

    if hasattr(ob, '__conform__'):
        raise TypeError(
            "Only objects without '__conform__' can use 'directlyProvides'",
            ob, protocols
        )

    from weakref import ref
    try:
        r = ref(ob)
    except TypeError:
        def conform(proto):
            if proto in protocols:
                return ob
    else:
        def conform(proto):
            if proto in protocols:
                return r()

    ob.__conform__ = conform






def moduleProvides(*interfaces):
    directlyProvides(
        modules[_getframe(1).f_globals['__name__']],
        *interfaces
    )


def instancesProvide(klass, *protocols):
    for p in protocols:
        adapt(p,Protocol).registerImplementation(klass, NO_ADAPTER_NEEDED)


class Attribute(object):
    """Attribute declaration; should we get rid of this?"""

    def __init__(self,doc,name=None,value=None):
        self.__doc__ = doc
        self.name = name
        self.value = value

    def __get__(self,ob,typ=None):
        if ob is None:
            return self
        try:
            return ob.__dict__[self.name]
        except KeyError:
            return self.value

    def __set__(self,ob,val):
        ob.__dict__[self.name] = val

    def __delete__(self,ob):
        del ob.__dict__[self.name]

    def __repr__(self):
        return "Attribute: %s" % self.__doc__





# Adapter for Zope X3 Interfaces

class ZopeInterfaceAsProtocol(object):

    __slots__ = 'iface'

    def __init__(self, iface, proto):
        self.iface = iface

    def getImpliedProtocols(self):
        return self.iface.getBases()

    def addImpliedProtocol(self, proto):
        raise TypeError(
            "Zope interfaces can't add implied protocols",
            self.iface, proto
        )

    def __adapt__(self, obj):
        if self.iface.isImplementedBy(obj):
            return obj

    def registerImplementation(self, klass, adapter=NO_ADAPTER_NEEDED):
        if adapter is NO_ADAPTER_NEEDED:
            from zope.interface.implements import implements
            implements(klass, self.iface)
        else:
            raise TypeError(
                "Zope interfaces can only declare support, not adapters",
                self.iface, klass, adapter
            )

    def registerNonImplementation(self, klass):
        from zope.interface.implements import flattenInterfaces
        klass.__implements__ = tuple([
            iface for iface in flattenInterfaces(
                getattr(klass,'__implements__',())
            ) if not self.iface.isEqualOrExtendedBy(iface)
        ])


# Monkeypatch Zope X3 Interfaces

try:
    from zope.interface import Interface as ZopeInterface

except ImportError:
    pass

else:

    def __adapt__(self, obj):
        if self.isImplementedBy(obj):
            return obj

    def __conform__(self,proto):
        if proto is Protocol:
            return ZopeInterfaceAsProtocol(self,proto)

    ZopeInterface.__class__.__adapt__   = __adapt__
    ZopeInterface.__class__.__conform__ = __conform__

    del ZopeInterface, __adapt__, __conform__




















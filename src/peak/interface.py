"""Trivial Interfaces and Adaptation"""

__all__ = [
    'IMPLEMENTATION_ERROR','NO_ADAPTER_NEEDED','DOES_NOT_SUPPORT', 'adapt',
    'minimumAdapter', 'composeAdapters', 'Protocol', 'InterfaceClass',
    'Interface', 'implements', 'instancesProvide', 'doesNotImplement',
    'implyProtocols', 'adapterForTypes', 'adapterForProtocols',
    'classProvides', 'moduleProvides', 'directlyProvides', 'IDirectProvider',
    'Attribute',
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

from peak.util.advice import addClassAdvisor, metamethod






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
            if exc_info()[2].tb_next is not None:
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
            if exc_info()[2].tb_next is not None:
                raise

    if default is _marker:
        return factory(obj, protocol)
    return default

# Adapter "arithmetic"

def minimumAdapter(a1,a2):
    """Which is a "shorter route" to implementation, 'a1' or 'a2'?

    Assuming both a1 and a2 are interchangeable adapters, return the one
    which is preferable.  If there is no obvious choice, raise TypeError."""

    if a1 is a2:
        return a1   # don't care which

    if a2 is DOES_NOT_SUPPORT or a1 is NO_ADAPTER_NEEDED:
        return a1

    if a1 is DOES_NOT_SUPPORT or a2 is NO_ADAPTER_NEEDED:
        return a2

    # it's ambiguous
    raise TypeError("Ambiguous adapter choice", a1, a2)


def composeAdapters(baseAdapter, baseProtocol, extendingAdapter):
    """Return the composition of 'baseAdapter'+'extendingAdapter'"""

    if baseAdapter is DOES_NOT_SUPPORT or extendingAdapter is DOES_NOT_SUPPORT:
        # fuhgeddaboudit
        return DOES_NOT_SUPPORT

    if baseAdapter is NO_ADAPTER_NEEDED:
        return extendingAdapter

    if extendingAdapter is NO_ADAPTER_NEEDED:
        return baseAdapter

    def newAdapter(ob,proto):
        return extendingAdapter(baseAdapter(ob,baseProtocol),proto)

    return newAdapter



# Trivial interface implementation

class Protocol:

    """Generic protocol w/type-based adapter registry"""

    def __init__(self):
        self.__adapters__ = {}; self.__implies__ = {}

    def getImpliedProtocols(self):
        return self.__implies__.items()

    def addImpliedProtocol(self, proto, adapter=NO_ADAPTER_NEEDED):
        old = self.__implies__.get(proto,DOES_NOT_SUPPORT)
        new = minimumAdapter(old,adapter)

        if old is new:
            return

        self.__implies__[proto] = new
        for klass,baseAdapter in self.__adapters__.items():
            proto.registerImplementation(
                klass, composeAdapters(baseAdapter,self,new)
            )

    def registerImplementation(self, klass, adapter=NO_ADAPTER_NEEDED):

        old = self.__adapters__.get(klass)
        new = adapter

        if old is not None:
            new = minimumAdapter(old,adapter)
        if old is new:
            return

        self.__adapters__[klass] = new
        for proto,extender in self.getImpliedProtocols():
            proto.registerImplementation(
                klass, composeAdapters(new,self,extender)
            )

    def registerNonImplementation(self, klass):
        self.__adapters__[klass] = DOES_NOT_SUPPORT

    def __adapt__(self, obj):
        get = self.__adapters__.get
        try:
            typ = obj.__class__
        except AttributeError:
            typ = type(obj)

        try:
            mro = typ.__mro__
        except AttributeError:
            mro = type('tmp',(typ,),{}).__mro__

        for klass in mro:
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
            (b,NO_ADAPTER_NEEDED) for b in self.__bases__
                if isinstance(b,Protocol) and b is not Interface
        ] + super(InterfaceClass,self).getImpliedProtocols()

    def getBases(self):
        return [
            b for b in self.__bases__
                if isinstance(b,Protocol) and b is not Interface
        ]

    def isImplementedBy(self,ob):   # XXX
        return adapt(ob,self,self) is ob and ob is not self

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






# Interface and adapter declarations

def implements(*protocols):
    """Declare that this class' instances directly provide 'protocols'"""
    def callback(klass):
        instancesProvide(klass, *protocols)
        return klass
    addClassAdvisor(callback)

def instancesProvide(klass, *protocols):
    """Declare that instances of 'klass' directly provide 'protocols'"""
    for p in protocols:
        adapt(p,Protocol).registerImplementation(klass)

def doesNotImplement(*protocols):
    """Declare that this class' instances do not provide 'protocols'"""
    def callback(klass):
        for p in protocols:
            adapt(p,Protocol).registerNonImplementation(klass)
        return klass
    addClassAdvisor(callback)

def implyProtocols(*protocols):
    """Declare that this protocol implies 'protocols' as well as its bases"""
    def callback(klass):
        _klass = adapt(klass,Protocol)
        for p in protocols:
            _klass.addImpliedProtocol(adapt(p,Protocol))
        return klass
    addClassAdvisor(callback)

def adapterForTypes(protocol,types):
    """Declare that this class adapts 'types' to 'protocol'"""
    protocol = adapt(protocol, Protocol)
    def callback(klass):
        for typ in types:
            protocol.registerImplementation(typ, klass)
        return klass
    addClassAdvisor(callback)


def adapterForProtocols(protocol, protocols):
    """Declare that this class adapts 'protocols' to 'protocol'"""
    protocol = adapt(protocol, Protocol)
    def callback(klass):
        for proto in protocols:
            protocol.addImpliedProtocol(proto, klass)
        return klass
    addClassAdvisor(callback)


def classProvides(*protocols):
    """Declare that this class itself directly provides 'protocols'"""
    def callback(klass):
        directlyProvides(klass, *protocols)
        return klass
    addClassAdvisor(callback)


def moduleProvides(*protocols):
    """Declare that the enclosing module directly provides 'protocols'"""
    directlyProvides(
        modules[_getframe(1).f_globals['__name__']],
        protocols
    )


def directlyProvides(ob, *protocols):
    """Declare that 'ob' directly provides 'protocols'"""
    adapt(ob,IDirectProvider).declareSupportFor(*protocols)












# Interface and adapters for managing 'directlyProvides' declarations

class IDirectProvider(Interface):

    def declareSupportFor(*protocols):
        """Add 'protocols' to supported protocols for this object"""


class TypeAsDirectProvider(object):

    """'directlyProvides()' for a class w/a unique metaclass"""

    adapterForTypes(IDirectProvider, [type])

    def __init__(self,ob,proto):
        meta = ob.__class__
        for base in ob.__bases__:
            if isinstance(base, meta):
                raise TypeError(
                    "Class must have its own metaclass to use this adapter",
                    ob, meta
                )
        self.meta = meta

    def declareSupportFor(self, *protocols):
        for p in protocols:
            adapt(p,Protocol).registerImplementation(self.meta)


class conformsRegistry(dict):

    """Helper type for ArbitraryObjectAsDirectProvider"""

    def __call__(self, protocol):
        if protocol in self:
            return self.subject()





class ArbitraryObjectAsDirectProvider(object):

    """Poke a __conform__ registry into an arbitrary object"""

    adapterForTypes(IDirectProvider, [object])

    def __init__(self,ob,proto):

        reg = getattr(ob, '__conform__', None)

        if reg is not None and not isinstance(reg,conformsRegistry):
            raise TypeError(
                "Incompatible __conform__ on adapted object", ob, proto
            )

        if reg is None:
            reg = ob.__conform__ = conformsRegistry()
            from weakref import ref
            try:
                r = ref(ob)
            except TypeError:
                r = lambda: ob
            reg.subject = r

        self.ob = ob
        self.reg = reg

    def declareSupportFor(self, *protocols):
        for p in protocols:
            self.reg[p] = p











# Semi-backward compatible 'interface.Attribute'

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
        return [(b,NO_ADAPTER_NEEDED) for b in self.iface.getBases()]

    def addImpliedProtocol(self, proto, adapter=NO_ADAPTER_NEEDED):
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




















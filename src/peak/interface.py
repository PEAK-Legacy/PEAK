"""Trivial Interfaces and Adaptation"""

__all__ = [
    'IMPLEMENTATION_ERROR','NO_ADAPTER_NEEDED','DOES_NOT_SUPPORT', 'adapt',
    'minimumAdapter', 'composeAdapters', 'Protocol', 'InterfaceClass',
    'Interface', 'declareAdapterForType', 'declareAdapterForProtocol',
    'declareAdapterForObject', 'instancesProvide', 'instancesDoNotProvide',
    'protocolImplies', 'directlyProvides', 'implements', 'doesNotImplement',
    'implyProtocols', 'adapterForTypes', 'adapterForProtocols', 'classProvides',
    'moduleProvides', 'IAdapter', 'IProtocol', 'IProtocolProvider',
    'IProtocolImplementor', 'Attribute',
]

# Fundamental Adapters

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

from types import ClassType, FunctionType, ModuleType, InstanceType
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

    a1ct = getattr(a1,'__adapterCount__',1)
    a2ct = getattr(a2,'__adapterCount__',1)

    if a1ct<a2ct:
        return a1
    elif a2ct<a1ct:
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

    newAdapter.__adapterCount__ = (
        getattr(extendingAdapter,'__adapterCount__',1)+
        getattr(baseAdapter,'__adapterCount__',1)
    )

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
            return new

        self.__implies__[proto] = new

        # Always register implied protocol with classes, because they should
        # know if we break the implication link between two protocols

        for klass,baseAdapter in self.__adapters__.items():
            declareAdapterForType(
                proto, composeAdapters(baseAdapter,self,new), klass
            )

        return new

    def __conform__(self,protocol):
        # I implement IProtocol directly
        if protocol is IProtocol:
            return self




    def registerImplementation(self, klass, adapter=NO_ADAPTER_NEEDED):

        old = self.__adapters__.get(klass)
        new = adapter

        if old is not None:
            new = minimumAdapter(old,adapter)

        if old is new:
            return new

        self.__adapters__[klass] = new

        if new is DOES_NOT_SUPPORT:
            return new

        # register with implied protocols, only if not DOES_NOT_SUPPORT
        for proto, extender in self.getImpliedProtocols():
            declareAdapterForType(
                proto, composeAdapters(new,self,extender), klass
            )

        return new

    def registerObject(self, ob, adapter=NO_ADAPTER_NEEDED):

        # Just handle implied protocols

        for proto, extender in self.getImpliedProtocols():
            declareAdapterForObject(
                proto, composeAdapters(adapter,self,extender), ob
            )









    def __adapt__(self, obj):

        get = self.__adapters__.get

        try:
            typ = obj.__class__
        except AttributeError:
            typ = type(obj)

        factory=get(typ)
        if factory is not None:
            return factory(obj,self)

        try:
            mro = typ.__mro__
        except AttributeError:
            # XXX We should probably emulate the "classic" MRO here, but
            # XXX being able to use 'InstanceType' is important for adapting
            # XXX any classic class, and 'object' is important for universal
            # XXX adapters.
            mro = type('tmp',(typ,object),{}).__mro__[:-1]+(InstanceType,object)
            typ.__mro__ = mro   # mommy make it stop!

        for klass in mro[1:]:
            factory=get(klass)
            if factory is not None:
                # Cache successful lookup
                declareAdapterForType(self, factory, klass)
                return factory(obj,self)

        # Cache the failed lookup
        declareAdapterForType(self, DOES_NOT_SUPPORT, typ)

    # Wrapping this in metamethod should only be necessary if you use a
    # Protocol as a metaclass for another protocol.  Which is probably a
    # completely insane thing to do, but it could happen by accident, if
    # someone includes a protocol (or subclass of a protocol) in the bases
    # of a metaclass.  So we'll wrap it, just in case.

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





class Interface(object):
    __metaclass__ = InterfaceClass

















# Fundamental, explicit interface/adapter declaration API:
#   All declarations should pass through these three routines.

def declareAdapterForType(protocol, adapter, typ):
    """Declare that 'adapter' adapts instances of 'typ' to 'protocol'"""

    adapter = adapt(protocol, IProtocol).registerImplementation(typ, adapter)

    dci = adapt(typ, IProtocolImplementor, None)

    if dci is not None:
        dci.declareClassImplements(protocol,adapter)


def declareAdapterForProtocol(protocol, adapter, proto):
    """Declare that 'adapter' adapts 'proto' to 'protocol'"""
    adapt(proto, IProtocol).addImpliedProtocol(protocol, adapter)


def declareAdapterForObject(protocol, adapter, ob):
    """Declare that 'adapter' adapts 'ob' to 'protocol'"""
    ob = adapt(ob,IProtocolProvider)
    ob.declareProvides(protocol,adapter)
    adapt(protocol,IProtocol).registerObject(ob)

















# Interface and adapter declarations - convenience forms, explicit targets

def instancesProvide(klass, *protocols):
    """Declare that instances of 'klass' directly provide 'protocols'"""
    for p in protocols:
        declareAdapterForType(p, NO_ADAPTER_NEEDED, klass)


def instancesDoNotProvide(klass, *protocols):
    """Declare that instances of 'klass' do NOT provide 'protocols'"""
    for p in protocols:
        declareAdapterForType(p, DOES_NOT_SUPPORT, klass)


def protocolImplies(protocol, *protocols):
    """Declare that 'protocol' implies 'protocols' as well as its bases"""
    for p in protocols:
        declareAdapterForProtocol(protocol, NO_ADAPTER_NEEDED, p)


def directlyProvides(ob, *protocols):
    """Declare that 'ob' directly provides 'protocols'"""
    for p in protocols:
        declareAdapterForObject(p, NO_ADAPTER_NEEDED, ob)

















# Interface and adapter declarations - implicit declarations in classes

def implements(*protocols):
    """Declare that this class' instances directly provide 'protocols'"""
    def callback(klass):
        instancesProvide(klass, *protocols)
        return klass
    addClassAdvisor(callback)

def doesNotImplement(*protocols):
    """Declare that this class' instances do not provide 'protocols'"""
    def callback(klass):
        instancesDoNotProvide(klass, *protocols)
        return klass
    addClassAdvisor(callback)


def implyProtocols(*protocols):
    """Declare that this protocol implies 'protocols' as well as its bases"""
    def callback(klass):
        protocolImplies(klass, *protocols)
        return klass
    addClassAdvisor(callback)


def adapterForTypes(protocol, types):
    """Declare that this class adapts 'types' to 'protocol'"""
    def callback(klass):
        for t in types: declareAdapterForType(protocol, klass, t)
        instancesProvide(klass, protocol)
        return klass
    addClassAdvisor(callback)

def adapterForProtocols(protocol, protocols):
    """Declare that this class adapts 'protocols' to 'protocol'"""
    def callback(klass):
        for p in protocols: declareAdapterForProtocol(protocol, klass, p)
        instancesProvide(klass, protocol)
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
        *protocols
    )



























# Interfaces and adapters for managing declarations

class IAdapter(Interface):

    def __call__(ob, protocol):
        """Return an implementation of 'protocol' for 'ob'"""


class IProtocol(Interface):

    def addImpliedProtocol(proto, adapter=NO_ADAPTER_NEEDED):
        """'adapter' provides conversion from this protocol to 'proto'"""

    def registerImplementation(klass, adapter=NO_ADAPTER_NEEDED):
        """'adapter' provides protocol for instances of klass"""

    def registerObject(ob, adapter=NO_ADAPTER_NEEDED):
        """'adapter' provides protocol for 'ob' directly"""


class IProtocolProvider(Interface):

    def declareProvides(protocol, adapter=NO_ADAPTER_NEEDED):
        """Register 'adapter' as providing 'protocol' for this object"""


class IProtocolImplementor(Interface):

    def declareClassImplements(protocol, adapter=NO_ADAPTER_NEEDED):
        """Register 'adapter' as implementing 'protocol' for instances"""











class ClassicClassAsImplementor(object):

    adapterForTypes(IProtocolProvider, [ClassType])

    def __init__(self, ob, protocol):

        conf_func = getattr(ob,'__conform__',None)

        if conf_func is None:
            ob.__conform__ = Classic__conform__

        elif getattr(conf_func,'im_func',None) is not Classic__conform__:
            raise TypeError(
                "%r has a __conform__ method of its own" % ob
            )

        self.klass = ob

    def declareClassImplements(self,protocol, adapter=NO_ADAPTER_NEEDED):
        setattr(self.klass, `protocol`, protocol,adapter)





















def Classic__conform__(self, protocol):

    """__conform__ method that handles registration for classic classes"""

    proto, adapter = getattr(self.__class__,`protocol`,(None,None))
    if adapter is not None:
        return adapter(self,protocol)


class conformsRegistry(dict):

    """Helper type for objects and classes that need registration support"""

    def __call__(self, protocol):
        if protocol in self:
            return self[protocol](self.subject(),protocol)

        subject = self.subject()

        try:
            klass = subject.__class__
            conform = klass.__conform__

        except AttributeError:
            pass

        else:
            if getattr(conform,'im_class',None) is klass:
                return conform(subject,protocol)












class ArbitraryObjectAsProvider(object):

    """Poke a __conform__ registry into an arbitrary object"""

    adapterForTypes(IProtocolProvider, [FunctionType,ModuleType,InstanceType])

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


    def declareProvides(self, protocol, adapter=NO_ADAPTER_NEEDED):
        self.reg[protocol] = adapter











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
        elif adapter is DOES_NOT_SUPPORT:
            from zope.interface.implements import flattenInterfaces
            klass.__implements__ = tuple([
                iface for iface in flattenInterfaces(
                    getattr(klass,'__implements__',())
                ) if not self.iface.isEqualOrExtendedBy(iface)
            ])
        else:
            raise TypeError(
                "Zope interfaces can only declare support, not adapters",
                self.iface, klass, adapter
            )

    def registerObject(ob,adapter=NO_ADAPTER_NEEDED):
        pass    # Zope interfaces handle implied protocols directly



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
        if proto is IProtocol:
            return ZopeInterfaceAsProtocol(self,proto)

    ZopeInterface.__class__.__adapt__   = __adapt__
    ZopeInterface.__class__.__conform__ = __conform__

    del ZopeInterface, __adapt__, __conform__




















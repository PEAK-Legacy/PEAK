"""Trivial Interfaces and Adaptation"""

__all__ = [
    'IMPLEMENTATION_ERROR','NO_ADAPTER_NEEDED','DOES_NOT_SUPPORT', 'adapt',
    'minimumAdapter', 'composeAdapters', 'Protocol', 'InterfaceClass',
    'Interface', 'declareAdapterForType', 'declareAdapterForProtocol',
    'declareAdapterForObject', 'instancesProvide', 'instancesDoNotProvide',
    'protocolImplies', 'directlyProvides', 'implements', 'doesNotImplement',
    'implyProtocols', 'adapterForTypes', 'adapterForProtocols',
    'classProvides', 'moduleProvides', 'IAdapterFactory', 'IProtocol',
    'IAdaptingProtocol', 'IOpenProtocol', 'IOpenProvider',
    'IOpenImplementor', 'Attribute',
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

def minimumAdapter(a1,a2,d1=0,d2=0):

    """Shortest route to implementation, 'a1' @ depth 'd1', or 'a2' @ 'd2'?

    Assuming both a1 and a2 are interchangeable adapters (i.e. have the same
    source and destination protocols), return the one which is preferable; that
    is, the one with the shortest implication depth, or, if the depths are
    equal, then the adapter that is composed of the fewest chained adapters.
    If both are the same, then prefer 'NO_ADAPTER_NEEDED', followed by
    anything but 'DOES_NOT_SUPPORT', with 'DOES_NOT_SUPPORT' being least
    preferable.  If there is no unambiguous choice, and 'not a1 is a2',
    TypeError is raised.
    """

    if d1<d2:
        return a1
    elif d2<d1:
        return a2

    if a1 is a2:
        return a1   # don't care which

    a1ct = getattr(a1,'__adapterCount__',1)
    a2ct = getattr(a2,'__adapterCount__',1)

    if a1ct<a2ct:
        return a1
    elif a2ct<a1ct:
        return a2

    if a1 is NO_ADAPTER_NEEDED or a2 is DOES_NOT_SUPPORT:
        return a1

    if a1 is DOES_NOT_SUPPORT or a2 is NO_ADAPTER_NEEDED:
        return a2

    # it's ambiguous
    raise TypeError("Ambiguous adapter choice", a1, a2, d1, d2)

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


def updateAdapterRegistry(mapping, key, adapter, depth):

    """Replace 'mapping[key]' w/'adapter' @ 'depth', return true if changed"""

    new = adapter
    old = mapping.get(key)

    if old is not None:
        old, oldDepth = old
        new = minimumAdapter(old,adapter,oldDepth,depth)
        if old is new and depth>=oldDepth:
            return False

    mapping[key] = new, depth
    return True


# Trivial interface implementation

class Protocol:

    """Generic protocol w/type-based adapter registry"""

    def __init__(self):
        self.__adapters = {}
        self.__implies = {}
        self.__lock = allocate_lock()

    def getImpliedProtocols(self):
        return self.__implies.items()


    def addImpliedProtocol(self,proto,adapter=NO_ADAPTER_NEEDED,depth=1):

        self.__lock.acquire()
        try:
            if not updateAdapterRegistry(self.__implies,proto,adapter,depth):
                return self.__implies[proto][0]
        finally:
            self.__lock.release()

        # Always register implied protocol with classes, because they should
        # know if we break the implication link between two protocols

        for klass,(baseAdapter,d) in self.__adapters.items():
            declareAdapterForType(
                proto,composeAdapters(baseAdapter,self,adapter),klass,depth+d
            )

        return adapter

    addImpliedProtocol = metamethod(addImpliedProtocol)






    def registerImplementation(self,klass,adapter=NO_ADAPTER_NEEDED,depth=1):

        self.__lock.acquire()
        try:
            if not updateAdapterRegistry(self.__adapters,klass,adapter,depth):
                return self.__adapters[klass][0]
        finally:
            self.__lock.release()

        if adapter is DOES_NOT_SUPPORT:
            # Don't register non-support with implied protocols, because
            # "X implies Y" and "not X" doesn't imply "not Y".  In effect,
            # explicitly registering DOES_NOT_SUPPORT for a type is just a
            # way to "disinherit" a superclass' claim to support something.
            return adapter

        for proto, (extender,d) in self.getImpliedProtocols():
            declareAdapterForType(
                proto, composeAdapters(adapter,self,extender), klass, depth+d
            )

        return adapter

    registerImplementation = metamethod(registerImplementation)



    def registerObject(self, ob, adapter=NO_ADAPTER_NEEDED,depth=1):

        # Just handle implied protocols

        for proto, (extender,d) in self.getImpliedProtocols():
            declareAdapterForObject(
                proto, composeAdapters(adapter,self,extender), ob, depth+d
            )

    registerObject = metamethod(registerObject)




    def __adapt__(self, obj):

        get = self.__adapters.get

        try:
            typ = obj.__class__
        except AttributeError:
            typ = type(obj)

        factory=get(typ)
        if factory is not None:
            return factory[0](obj,self)

        try:
            mro = typ.__mro__
        except AttributeError:
            # XXX We should probably emulate the "classic" MRO here, but
            # XXX being able to use 'InstanceType' is important for adapting
            # XXX any classic class, and 'object' is important for universal
            # XXX adapters.
            mro = type('x',(typ,object),{}).__mro__[:-1]+(InstanceType,object)
            typ.__mro__ = mro   # mommy make it stop!

        for klass in mro[1:]:
            factory=get(klass)
            if factory is not None:
                # Cache successful lookup
                declareAdapterForType(self, factory[0], klass)
                return factory[0](obj,self)

        # Cache the failed lookup
        declareAdapterForType(self, DOES_NOT_SUPPORT, typ)

    # Wrapping this in metamethod should only be necessary if you use a
    # Protocol as a metaclass for another protocol.  Which is probably a
    # completely insane thing to do, but it could happen by accident, if
    # someone includes a protocol (or subclass of a protocol) in the bases
    # of a metaclass.  So we'll wrap it, just in case.

    __adapt__ = metamethod(__adapt__)

try:
    from thread import allocate_lock

except ImportError:
    try:
        from dummy_thread import allocate_lock

    except ImportError:
        class allocate_lock(object):
            __slots__ = ()
            def acquire(*args): pass
            def release(*args): pass



class InterfaceClass(Protocol, type):

    def __init__(self, __name__, __bases__, __dict__):
        type.__init__(self, __name__, __bases__, __dict__)
        Protocol.__init__(self)

    def getImpliedProtocols(self):
        return [
            (b,(NO_ADAPTER_NEEDED,1)) for b in self.__bases__
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
#   All declarations should end up passing through these three routines.

def declareAdapterForType(protocol, adapter, typ, depth=1):
    """Declare that 'adapter' adapts instances of 'typ' to 'protocol'"""

    adapter = adapt(protocol, IOpenProtocol).registerImplementation(
        typ, adapter, depth
    )

    oi = adapt(typ, IOpenImplementor, None)

    if oi is not None:
        oi.declareClassImplements(protocol,adapter,depth)


def declareAdapterForProtocol(protocol, adapter, proto, depth=1):
    """Declare that 'adapter' adapts 'proto' to 'protocol'"""
    adapt(proto, IOpenProtocol).addImpliedProtocol(protocol, adapter, depth)


def declareAdapterForObject(protocol, adapter, ob, depth=1):
    """Declare that 'adapter' adapts 'ob' to 'protocol'"""
    ob = adapt(ob,IOpenProvider)
    ob.declareProvides(protocol,adapter,depth)
    adapt(protocol,IOpenProtocol).registerObject(ob,adapter,depth)















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

class IAdapterFactory(Interface):

    """Callable that can adapt an object to a protocol"""

    def __call__(ob, protocol):
        """Return an implementation of 'protocol' for 'ob'"""


class IProtocol(Interface):

    """Object usable as a protocol by 'adapt()'"""

    def __hash__():
        """Protocols must be usable as dictionary keys"""

    def __eq__(other):
        """Protocols must be comparable with == and !="""

    def __ne__(other):
        """Protocols must be comparable with == and !="""


class IAdaptingProtocol(IProtocol):

    """A protocol that potentially knows how to adapt some object to itself"""

    def __adapt__(ob):
        """Return 'ob' adapted to protocol, or 'None'"""


class IConformingObject(Interface):

    """An object that potentially knows how to adapt to a protocol"""

    def __conform__(protocol):
        """Return an implementation of 'protocol' for self, or 'None'"""



class IOpenProvider(Interface):

    """An object that can be told how to adapt to protocols"""

    def declareProvides(protocol, adapter=NO_ADAPTER_NEEDED, depth=1):
        """Register 'adapter' as providing 'protocol' for this object"""


class IOpenImplementor(Interface):

    """Object/type that can be told how its instances adapt to protocols"""

    def declareClassImplements(protocol, adapter=NO_ADAPTER_NEEDED, depth=1):
        """Register 'adapter' as implementing 'protocol' for instances"""


class IOpenProtocol(IAdaptingProtocol):

    """A protocol that be told what it implies, and what supports it

    Note that these methods are for the use of the declaration APIs only,
    and you should NEVER call them directly."""

    def addImpliedProtocol(proto, adapter=NO_ADAPTER_NEEDED, depth=1):
        """'adapter' provides conversion from this protocol to 'proto'"""

    def registerImplementation(klass, adapter=NO_ADAPTER_NEEDED, depth=1):
        """'adapter' provides protocol for instances of klass"""

    def registerObject(ob, adapter=NO_ADAPTER_NEEDED, depth=1):
        """'adapter' provides protocol for 'ob' directly"""










# Bootstrap APIs to work with Protocol and InterfaceClass, without needing to
# give Protocol a '__conform__' method that's hardwired to IOpenProtocol.
# Note that InterfaceClass has to be registered first, so that when the
# registration propagates to IAdaptingProtocol and IProtocol, InterfaceClass
# will already be recognized as an IOpenProtocol, preventing infinite regress.

IOpenProtocol.registerImplementation(InterfaceClass)    # VERY BAD!!
IOpenProtocol.registerImplementation(Protocol)          # NEVER DO THIS!!

# From this line forward, the declaration APIs work.  Use them instead!



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








class MiscObjectsAsOpenProvider(object):

    """Supply __conform__ registry for funcs, modules, & classic instances"""

    adapterForTypes(IOpenProvider, [FunctionType,ModuleType,InstanceType])

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


    def declareProvides(self, protocol, adapter=NO_ADAPTER_NEEDED, depth=1):
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














# Monkeypatch Zope Interfaces

def __adapt__(self, obj):
    if self.isImplementedBy(obj):
        return obj


try:
    # Zope X3
    from zope.interface import Interface as ZopeInterface
    from zope.interface.implements import implements as ZopeImplements
    from zope.interface.implements import flattenInterfaces as ZopeFlatten

except ImportError:

    try:
        # Older Zopes
        from Interface import Interface as ZopeInterface
        from Interface.Implements import implements as ZopeImplements
        from Interface.implements import flattenInterfaces as ZopeFlatten

    except ImportError:
        ZopeInterface = None


if ZopeInterface is not None:

    ZopeInterface.__class__.__adapt__ = __adapt__
    ZopeInterface.__class__._doFlatten = staticmethod(ZopeFlatten)
    ZopeInterface.__class__._doSetImplements = staticmethod(ZopeImplements)
    ZopeInterfaceTypes = [ZopeInterface.__class__]

    instancesImplement(ZopeInterface.__class__, IAdaptingProtocol)

else:
    ZopeInterfaceTypes = []


del ZopeInterface, __adapt__


# Adapter for Zope X3 Interfaces

class ZopeInterfaceAsProtocol(object):

    __slots__ = 'iface'

    adapterForTypes(IOpenProtocol, ZopeInterfaceTypes)

    def __init__(self, iface, proto):
        self.iface = iface

    def addImpliedProtocol(self, proto, adapter=NO_ADAPTER_NEEDED,depth=1):
        raise TypeError(
            "Zope interfaces can't add implied protocols",
            self.iface, proto
        )

    def __adapt__(self, obj):
        if self.iface.isImplementedBy(obj):
            return obj

    def registerImplementation(self,klass,adapter=NO_ADAPTER_NEEDED,depth=1):
        if adapter is NO_ADAPTER_NEEDED:
            ZopeImplements(klass, self.iface)
        elif adapter is DOES_NOT_SUPPORT:
            klass.__implements__ = tuple([
                iface for iface in ZopeFlatten(
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




"""'Once' objects and classes"""

from __future__ import generators
from peak.api import NOT_FOUND, protocols, adapt
from peak.util.imports import importObject, importString
from interfaces import IAttachable, IActiveDescriptor
from _once import *
from protocols import IOpenProvider, IOpenImplementor, NO_ADAPTER_NEEDED
from peak.util.advice import metamethod
from warnings import warn
from types import ClassType

__all__ = [
    'Once', 'New', 'Copy', 'Activator', 'ActiveClass',
    'getInheritedRegistries', 'classAttr', 'Singleton', 'metamethod',
    'Attribute', 'ComponentSetupWarning', 'suggestParentComponent'
]

class ComponentSetupWarning(UserWarning):
    """Large iterator passed to suggestParentComponent"""


def supertype(supertype,subtype):

    """Workaround for 'super()' not handling metaclasses well

    Note that this will *skip* any classic classes in the MRO!
    """

    mro = iter(subtype.__mro__)

    for cls in mro:
        if cls is supertype:
            for cls in mro:
                if hasattr(cls,'__mro__'):
                    return cls
            break

    raise TypeError("Not sub/supertypes:", supertype, subtype)


class Descriptor(BaseDescriptor):

    def __init__(self,**kw):

        klass = self.__class__

        for k,v in kw.items():
            if hasattr(klass,k):
                setattr(self,k,v)
            else:
                raise TypeError("%r has no keyword argument %r" % (klass,k))



def getInheritedRegistries(klass, registryName):

    """Minimal set of 'registryName' registries in reverse MRO order"""

    bases = klass.__bases__

    if len(bases)==1:
        reg = getattr(bases[0],registryName,NOT_FOUND)
        if reg is not NOT_FOUND:
            yield reg

    else:
        mro = list(klass.__mro__)
        bases = [(-mro.index(b),b) for b in bases]
        bases.sort()
        for (b,b) in bases:
            reg = getattr(b,registryName,NOT_FOUND)
            if reg is not NOT_FOUND:
                yield reg








def suggestParentComponent(parent,name,child):

    """Suggest to 'child' that it has 'parent' and 'name'

    If 'child' does not support 'IAttachable' and is a container that derives
    from 'tuple' or 'list', all of its elements that support 'IAttachable'
    will be given a suggestion to use 'parent' and 'name' as well.  Note that
    this means it would not be a good idea to use this on, say, a 10,000
    element list (especially if the objects in it aren't components), because
    this function has to check all of them."""

    ob = adapt(child,IAttachable,None)

    if ob is not None:
        # Tell it directly
        ob.setParentComponent(parent,name,suggest=True)

    elif isinstance(child,(list,tuple)):

        ct = 0

        for ob in child:

            ob = adapt(ob,IAttachable,None)

            if ob is not None:
                ob.setParentComponent(parent,name,suggest=True)
            else:
                ct += 1
                if ct==100:
                    warn(
                        ("Large iterator for %s; if it will never"
                         " contain components, this is wasteful.  (You may"
                         " want to set 'suggestParent=False' on the attribute"
                         " binding or lookupComponent() call, if applicable.)"
                         % name),
                        ComponentSetupWarning, 3
                    )



def New(obtype, **kw):

    """One-time binding of a new instance of 'obtype'

    Usage::

        class someClass(binding.Component):

            myDictAttr = binding.New(dict)

            myListAttr = binding.New(list)

    The 'myDictAttr' and 'myListAttr' will become empty instance
    attributes on their first access attempt from an instance of
    'someClass'.

    This is basically syntactic sugar for 'Once' to create an empty
    instance of a type.  The same rules apply as for 'Once' about
    whether the 'name' parameter is required.  (That is, you need it if you're
    using this in a class whose metaclass doesn't support active descriptors,
    such as when you're not deriving from a standard PEAK base class.)
    """

    kw.setdefault('doc', 'New %s' % obtype)
    return Once( lambda s,d,a: importObject(obtype)(), **kw)
















def Copy(obj, **kw):

    """One-time binding of a copy of 'obj'

    Usage::

        class someClass(binding.Component):

            myDictAttr = binding.Copy( {'foo': 2} )

            myListAttr = binding.Copy( [1,2,'buckle your shoe'] )

    The 'myDictAttr' and 'myListAttr' will become per-instance copies of the
    supplied initial values on the first attempt to access them from an
    instance of 'someClass'.

    This is basically syntactic sugar for 'Once' to create copies using
    the Python 'copy.copy()' function.  The same rules apply as for
    'Once' about whether the 'name' parameter is required.  (That is, you need
    it if you're using this in a class whose metaclass doesn't support
    active descriptors, such as when you're not deriving from a standard PEAK
    base class.)
    """


    from copy import copy
    return Once(
        (lambda s,d,a: copy(obj)), **kw
    )












class AttributeClass(type):

    """Help attribute classes keep class docs separate from instance docs"""

    def __new__(meta, name, bases, cdict):
        classDoc = cdict.get('__doc__')
        cdict['__doc__'] = Descriptor(
            attrName = '__doc__',
            computeValue = lambda s,d,a: s.doc,
            ofClass = lambda a,k: classDoc
        )
        return supertype(AttributeClass,meta).__new__(meta,name,bases,cdict)





























class Attribute(Descriptor):

    __metaclass__ = AttributeClass

    protocols.advise(
        instancesProvide = [IActiveDescriptor]
    )

    offerAs = ()
    activateUponAssembly = False
    doc = None
    adaptTo = None
    suggestParent = True

    def activateInClass(self,klass,attrName):
        setattr(klass, attrName, self._copyWithName(attrName))
        return self

    def _copyWithName(self, attrName):
        return Descriptor(
            attrName     = attrName,
            computeValue = self.computeValue,
            ofClass      = self.ofClass,
            onSet        = self.onSet,
        )


    def __repr__(self):
        return "Binding: %s" % (self.__doc__ or '(undocumented)')


    def onSet(self, obj, attrName, value):

        if self.adaptTo is not None:
            value = adapt(value, self.adaptTo)

        if self.suggestParent:
            suggestParentComponent(obj, attrName, value)
        return value


    # The following methods only get called when an instance of this class is
    # used as a descriptor in a classic class or other class that doesn't
    # support active descriptors.  So, we will use the invocation of these
    # methods to bootstrap our activation.  Once activated, these methods won't
    # be called any more.

    def __get__(self, ob, typ=None):
        if ob is None:
            return self
        return self._installedDescr(ob.__class__).__get__(ob,typ)


    def __set__(self,ob,value):
        self._installedDescr(ob.__class__).__set__(ob,value)


    def __delete__(self,ob,value):
        self._installedDescr(ob.__class__).__delete__(ob)


    def _installedDescr(self, klass):
        # Return a newly installed descriptor proxy to use, or raise a usage
        # error if self doesn't know its own right name.

        from protocols.advice import getMRO
        name = self.attrName

        for cls in getMRO(klass):
            if name in cls.__dict__:
                if cls.__dict__[name] is self:
                    # Install a proxy, so we don't have to do this again!
                    descr = self._copyWithName(name)
                    setattr(cls, name, descr)
                    return descr
                else:
                    break

        # If we get here, we were not found under the name we were given
        self.usageError()


class Once(Attribute):
    """One-time Properties

        Usage ('Once(callable)')::

            class someClass(object):

                def anAttr(self, __dict__, attrName):
                    return self.foo * self.bar

                anAttr = Once(anAttr, attrName='anAttr')

        When 'anInstanceOfSomeClass.anAttr' is accessed for the first time,
        the 'anAttr' function will be called, and saved in the instance
        dictionary.  Subsequent access to the attribute will return the
        cached value.  Deleting the attribute will cause it to be computed
        again on the next access.

        The 'attrName' argument is optional.  If not supplied, it will default
        to the '__name__' of the supplied callable.  (So in the usage
        example above, it could have been omitted.)

        'Once' is an "active descriptor", so if you place an
        instance of it in a class which supports descriptor naming (i.e.,
        has a metaclass derived from 'binding.Activator'), it will
        automatically know the correct attribute name to use in the instance
        dictionary, even if it is different than the supplied name or name of
        the supplied callable.  However, if you place a 'Once' instance in a
        class which does *not* support descriptor naming, and you did not
        supply a valid name, attribute access will fail with a 'TypeError'."""

    def __init__(self, computeValue, **kw):
        self.computeValue = computeValue
        kw.setdefault('attrName',getattr(computeValue, '__name__', None))
        kw.setdefault('doc',
            getattr(computeValue,'__doc_',None) or kw['attrName']
        )
        super(Once,self).__init__(**kw)



class classAttr(object):

    """Class attribute binding

    This wrapper lets you create bindings which apply to a class, rather than
    to its instances.  This can be useful for creating bindings in a base
    class that will summarize metadata about subclasses.  Usage example::

        class SomeClass(binding.Component):

            CLASS_NAME = binding.classAttr(
                binding.Once(
                    lambda s,d,a: s.__name__.upper()
                )
            )

        class aSubclass(SomeClass):
            pass

        assert SomeClass.CLASS_NAME == "SOMECLASS"
        assert aSubclass.CLASS_NAME == "ASUBCLASS"

    Class attributes will only work in subclasses of classes like
    'binding.Component', whose metaclass derives from 'binding.Activator'.

    Implementation note: class attributes actually cause a new metaclass to
    be created on-the-fly to contain them.  The generated metaclass is named
    for the class that contained the class attributes, and has the same
    '__module__' attribute value.  So continuing the above example::

        assert SomeClass.__class__.__name__ == 'SomeClassClass'
        assert aSubClass.__class__.__name__ == 'SomeClassClass'

    Notice that the generated metaclass is reused for subsequent
    subclasses, as long as they don't define any new class attributes."""

    __slots__ = 'binding'

    def __init__(self, binding): self.binding = binding


class Activator(type):

    """Descriptor metadata management"""

    __name__ = 'Activator'    # trick to make instances' __name__ writable


    def __new__(meta, name, bases, cdict):

        classAttrs = [
            (k,v.binding) for (k, v) in cdict.items()
                if adapt(v,classAttr,not v) is v
        ]

        if classAttrs:

            cdict = cdict.copy(); d = {}
            d = dict(classAttrs)
            map(cdict.__delitem__, d.keys())

            d['__module__'] = cdict.get('__module__')

            meta = Activator( name+'Class', (meta,), d )

            # The new metaclass' __new__ will finish up for us...
            return meta(name,bases,cdict)

        klass = supertype(Activator,meta).__new__(meta, name, bases, cdict)
        klass.__name__ = name

        cd = klass.__class_descriptors__ = {}

        for k,v in cdict.items():
            v = adapt(v, IActiveDescriptor, None)
            if v is not None:
                cd[k]=v.activateInClass(klass,k)

        return klass



    def __all_descriptors__(klass,d,a):
        ad = {}
        map(ad.update, getInheritedRegistries(klass, '__all_descriptors__'))
        ad.update(klass.__class_descriptors__)
        return ad

    __all_descriptors__ = Once(__all_descriptors__, suggestParent=False)


































class ActiveClass(Activator):

    """Metaclass for classes that are themselves components"""

    def activateInClass(self,klass,attrName):

        if klass.__module__ == self.__module__:

            if '__parent__' not in self.__dict__ and attrName!='__metaclass__':
                # We use a tuple, so that if our parent is a descriptor,
                # it won't interfere when our instance tries to set *its*
                # parent!
                self.__parent__ = klass,

        return self


    def getParentComponent(self):
        return self.__parent__[0]

    getParentComponent = metamethod(getParentComponent)


    def getComponentName(self):
        return self.__cname__

    getComponentName = metamethod(getComponentName)


    def _getConfigData(self, forObj, configKey):
        return NOT_FOUND

    _getConfigData = metamethod(_getConfigData)








    def __parent__(self,d,a):

        parent = self.__module__
        name = self.__name__

        if '.' in name:
            name = '.'.join(name.split('.')[:-1])
            parent = '%s:%s' % (parent,name)

        return importString(parent),

    __parent__ = Once(__parent__, suggestParent=False)


    def __cname__(self,d,a):
        return self.__name__.split('.')[-1]

    __cname__ = Once(__cname__, suggestParent=False)























_ignoreNames = {'__name__':1, '__new__':1, '__module__':1, '__return__':1}

class SingletonClass(Activator):

    def __new__(meta, name, bases, cdict):
        for k in cdict.keys():
            if k not in _ignoreNames:
                cdict[k] = classAttr(cdict[k])

        return supertype(SingletonClass,meta).__new__(meta,name,bases,cdict)


class Singleton(object):

    """Class whose instances are itself, with all attributes at class level

    Subclass 'binding.Singleton' to create true (per-interpreter) singleton
    objects.  Any attribute bindings defined will apply to the class itself,
    rather than to its instances.  Any attempt to create an instance of a
    singleton class will simply return the class itself.  The 'self' of all
    methods will also be the class.

    This actually works by redefining all the singleton class' attributes
    as 'binding.classAttr()' objects, causing them to be placed in a new
    metaclass created specifically for the singleton class.  So, if you would
    otherwise find yourself using 'classmethod' or 'binding.classAttr()' on
    all the contents of a class, just subclass 'binding.Singleton' instead.

    Note that if you define special methods like '__new__()' or '__init__()',
    these will also be promoted to the metaclass.  This means, for example,
    that if you define an '__init__' method, it will be called with the
    singleton class object (or a subclass) when the class is created."""

    __metaclass__ = SingletonClass

    def __new__(klass):
        return klass

del _ignoreNames['__new__']     # we want this to be promoted, for subclasses



"""'Once' objects and classes"""

from __future__ import generators
from peak.api import NOT_FOUND
from peak.util.imports import importObject, importString
from interfaces import IComponentFactory
from _once import *


__all__ = [
    'Once', 'New', 'Copy', 'Activator', 'ActiveClass', 'ActiveClasses',
    'getInheritedRegistries', 'classAttr', 'Singleton', 'metamethod',
]


def metamethod(func):
    """Wrapper for metaclass method that might be confused w/instance method"""
    return property(lambda ob: func.__get__(ob))

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



def New(obtype, bindToOwner=None, name=None, provides=None, doc=None,
    activateUponAssembly=False):

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

    def mkNew(s,d,a):
        factory = importObject(obtype)

        if bindToOwner or (
            bindToOwner is None and IComponentFactory.isImplementedBy(factory)
        ):
            return factory(s,a)
        else:
            return factory()

    return Once( mkNew, name, provides, doc, activateUponAssembly)






def Copy(obj, name=None, provides=None, doc=None, activateUponAssembly=False):

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
        (lambda s,d,a: copy(obj)), name, provides, doc, activateUponAssembly
    )












class Once(OnceDescriptor):

    """One-time Properties

        Usage ('Once(callable,name)')::

            class someClass(object):

                def anAttr(self, __dict__, attrName):
                    return self.foo * self.bar

                anAttr = Once(anAttr, 'anAttr')

        When 'anInstanceOfSomeClass.anAttr' is accessed for the first time,
        the 'anAttr' function will be called, and saved in the instance
        dictionary.  Subsequent access to the attribute will return the
        cached value.  Deleting the attribute will cause it to be computed
        again on the next access.

        The 'name' argument is optional.  If not supplied, it will default
        to the '__name__' of the supplied callable.  (So in the usage
        example above, it could have been omitted.)

        'Once' is an "active descriptor", so if you place an
        instance of it in a class which supports descriptor naming (i.e.,
        has a metaclass derived from 'binding.Activator'), it will
        automatically know the correct attribute name to use in the instance
        dictionary, even if it is different than the supplied name or name of
        the supplied callable.  However, if you place a 'Once' instance in a
        class which does *not* support descriptor naming, and you did not
        supply a valid name, attribute access will fail with a 'TypeError'.
    """

    attrName = OnceDescriptor_attrName
    declareAsProviderOf = None
    activateUponAssembly = False





    def __init__(self,
        func, name=None, provides=None, doc=None, activateUponAssembly=False):

        self.computeValue = func
        self.attrName = self.__name__ = name or getattr(func,'__name__',None)
        self.declareAsProviderOf = provides
        self.__doc__ = doc or getattr(func,'__doc__','')
        if activateUponAssembly:
            self.activateUponAssembly = True


    def usageError(self):
        raise TypeError(
            "%s was used in a type which does not support active bindings,"
            " but a valid attribute name was not supplied"
            % self
        )


    def computeValue(self, obj, instanceDict, attrName):
        raise NotImplementedError


    def activate(self,klass,attrName):

        if attrName !=self.attrName:
            self = self._copyWithName(attrName)
            setattr(klass, attrName, self)

        return self


    def _copyWithName(self, attrName):

        from copy import copy
        newOb = copy(self)

        newOb.attrName = newOb.__name__ = attrName
        return newOb


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

    __class_descriptors__ = {}
    __all_descriptors__ = {}

    def __new__(meta, name, bases, cdict):

        class_attrs = []; addCA = class_attrs.append
        class_descr = []; addCD = class_descr.append

        for k, v in cdict.items():
            if isinstance(v,ActiveClasses):
                if isinstance(v,classAttr):
                    addCA(k)
                else:
                    addCD(k)

        if class_attrs:

            cdict = cdict.copy(); d = {}

            for k in class_attrs:
                d[k]=cdict[k].binding
                del cdict[k]

            d['__module__'] = cdict.get('__module__')

            meta = Activator( name+'Class', (meta,), d )

            # The new metaclass' __new__ will finish up for us...
            return meta(name,bases,cdict)

        klass = supertype(Activator,meta).__new__(meta, name, bases, cdict)
        klass.__name__ = name



        d = klass.__class_descriptors__ = {}

        for k in class_descr:
            v = cdict[k]
            d[k] = v.activate(klass,k)

        ad = {}
        map(ad.update, getInheritedRegistries(klass, '__all_descriptors__'))
        ad.update(klass.__class_descriptors__)
        klass.__all_descriptors__ = ad


        return klass




























class ActiveClass(Activator):

    """Metaclass for classes that are themselves components"""

    def activate(self,klass,attrName):

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

    __parent__ = Once(__parent__)


    def __cname__(self,d,a):
        return self.__name__.split('.')[-1]

    __cname__ = Once(__cname__)


ActiveClasses = (Once, ActiveClass, classAttr)


def supertype(supertype,subtype):

    mro = iter(subtype.__mro__)

    for cls in mro:
        if cls is supertype:
            return mro.next()
    else:
        raise TypeError("Not sub/supertypes:", supertype, subtype)









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



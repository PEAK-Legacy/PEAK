from interfaces import IActiveDescriptor
from protocols import adapt
from types import ClassType

__all__ = ['activateClass','classAttr','Activator']


def activateClass(klass):
    """Activate any 'IActiveDescriptor' or 'classAttr' objects in 'klass'

    Any 'IActiveDescriptor' objects found in the class dictionary will have
    their 'activateInClass()' method called with the target class and attribute
    name.  The return value is then placed in a '__class_descriptors__' mapping
    that maps from attribute names to return values.

    If the class dictionary contains any 'binding.classAttr' instances, these
    are attached to a new metaclass for the class, and the class is rebuilt
    as an instance of the new metaclass.

    'activateClass()' does nothing if the class already possesses a
    '__class_descriptors__' mapping, so it is safe to call it more than once on
    the same class.
    """

    d = klass.__dict__
    if '__class_descriptors__' in d:
        return klass

    meta, stdAttrs = _boostedMeta(type(klass),klass.__name__,d)
    if meta is not type(klass):
        klass = meta(klass.__name__,klass.__bases__,stdAttrs)
        d = stdAttrs

    klass.__class_descriptors__ = cd = {}
    for k,v in d.items():
        v = IActiveDescriptor(v,None)
        if v is not None:
            cd[k] = v.activateInClass(klass,k)
    return klass


class classAttr(object):

    """Class attribute binding

    This wrapper lets you create bindings which apply to a class, rather than
    to its instances.  This can be useful for creating bindings in a base
    class that will summarize metadata about subclasses.  Usage example::

        class SomeClass(binding.Component):

            CLASS_NAME = binding.classAttr(
                binding.Make(
                    lambda self: self.__name__.upper()
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

        meta, stdAttrs = _boostedMeta(meta,name,cdict)

        if stdAttrs is not None:
            cdict = stdAttrs
            return meta(name,bases,cdict)

        klass = supertype(Activator,meta).__new__(meta, name, bases, cdict)
        klass.__name__ = name
        return activateClass(klass)



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



def _boostedMeta(meta,name,cdict):

    classAttrs = dict([
        (k,v.binding) for (k, v) in cdict.items()
            if v is not None and adapt(v,classAttr,None) is v
    ])

    if not classAttrs:
        return meta,None

    stdAttrs = dict(cdict)
    map(stdAttrs.__delitem__, classAttrs)

    classAttrs['__module__'] = stdAttrs.get('__module__')

    if meta is ClassType:
        meta = type

    metameta = type(meta)
    if metameta is type:
        metameta = Activator    # Ensure that all subclasses are activated, too

    meta = metameta( name+'Class', (meta,), classAttrs )
    return meta, stdAttrs

















def activateClass(klass):
    """Activate any 'IActiveDescriptor' or 'classAttr' objects in 'klass'

    Any 'IActiveDescriptor' objects found in the class dictionary will have
    their 'activateInClass()' method called with the target class and attribute
    name.  The return value is then placed in a '__class_descriptors__' mapping
    that maps from attribute names to return values.

    'activateClass()' does nothing if the class already possesses a
    '__class_descriptors__' mapping, so it is safe to call it more than once on
    the same class.
    """

    d = klass.__dict__
    if '__class_descriptors__' in d:
        return klass

    meta, stdAttrs = _boostedMeta(type(klass),klass.__name__,d)

    if meta is not type(klass):
        klass = meta(klass.__name__,klass.__bases__,stdAttrs)
        d = stdAttrs

    klass.__class_descriptors__ = cd = {}

    for k,v in d.items():
        v = IActiveDescriptor(v,None)
        if v is not None:
            cd[k] = v.activateInClass(klass,k)
    return klass












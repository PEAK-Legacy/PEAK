"""Basic implementation of a domain metamodel"""

from peak.api import *
from peak.model.interfaces import *
from peak.model.interfaces import __all__ as allInterfaces

from Persistence import Persistent



__all__ = [
    'App','Service',
    'StructuralFeature', 'Field', 'Collection', 'Reference', 'Sequence',
    'Classifier','PrimitiveType','Enumeration','DataType','Element',
]


# We export the interfaces too, so people don't have to dig for them...

__all__ += allInterfaces





















class Service(binding.AutoCreated):

    """Well-known instances"""

    __implements__ = IService
    

class App(Service):

    """Application class"""

    def newElement(self,elementType,*args,**kw):
        element = apply(getattr(self,elementType),args,kw)  # XXX won't do dotted names
        element._fData = {}
        element.setParentComponent(self)
        return element

























class FeatureMC(binding.MethodExporter):

    """Method-exporting Property
    
        This metaclass adds property support to Meta.MethodExporter by adding
        '__get__', '__set__', and '__delete__' methods, which are delegated
        to the method templates for the 'get', 'set' and 'delattr' verbs.

        In other words, if you define a feature 'foo', following standard
        naming patterns for its 'set', 'get' and 'delattr' verbs, and 'bar' is
        an Element whose class includes the 'foo' feature, then 'bar.foo = 1'
        is equivalent to 'bar.setFoo(1)'.  Similarly, referencing 'bar.foo' by
        itself is equivalent to 'bar.getFoo()', and 'del bar.foo' is equivalent
        to 'bar.delattrFoo()'.

        (Note: this is true even if the Element class supplies its own 'setFoo'
        or 'getFoo' implementations, since the 'getMethod()' API is used.)

        Please see the 'TW.API.Meta.MethodExporter' class documentation for
        more detail on how method templates are defined, the use of naming
        conventions, verbs, template variants, etc."""

    def __get__(self, ob, typ=None):

        """Get the feature's value by delegating to 'ob.getX()'"""

        if ob is None: return self
        return self.getMethod(ob,'get')()

    def __set__(self, ob, val):

        """Set the feature's value by delegating to 'ob.setX()'"""

        return self.getMethod(ob,'set')(val)

    def __delete__(self, ob):

        """Delete the feature's value by delegating to 'ob.delattrX()'"""

        return self.getMethod(ob,'delattr')()

class StructuralFeature(binding.Component):

    __metaclasses__ = FeatureMC,

    isRequired    = 0
    lowerBound    = 0
    upperBound    = None    # None means unbounded upper end

    isOrdered     = 0
    isChangeable  = 1       # default is to be changeable

    referencedEnd = None    # and without an 'other end'
    referencedType = None
    defaultValue   = None

    newVerbs = Items(
        get     = 'get%(initCap)s',
        set     = 'set%(initCap)s',
        delattr = 'delattr%(initCap)s',
    )
    
    def get(feature, element):
        return element._getBinding(feature.attrName, feature.defaultValue)


    def set(feature, element, val):
        element._setBinding(feature.attrName,val)

    def delete(feature, element):
        element._delBinding(feature.attrName)

    config.setupObject(delete, verb='delattr')









class Field(StructuralFeature):

    __class_implements__ = IValue    

    upperBound = 1

    def _getList(feature, element):
        return [feature.get(element)]

































class Collection(StructuralFeature):

    __class_implements__ = ICollection

    newVerbs = Items(
        add     = 'add%(initCap)s',
        remove  = 'remove%(initCap)s',
        replace = 'replace%(initCap)s',
    )

    def _getList(feature, element):
        return element._getBinding(feature.attrName, ())
        
    def get(feature, element):
        return feature._getList(element)

    def set(feature, element, val):
        feature.__delete__(element)
        element._setBinding(feature.attrName, val)

    def add(feature, element, item):

        """Add the item to the collection/relationship"""      

        ub = feature.upperBound

        if not ub or len(feature._getList(element))<ub:
            feature._notifyLink(element,item)
            feature._link(element,item)
        else:
            raise ValueError("Too many items")


    def remove(feature, element, item):
        """Remove the item from the collection/relationship, if present"""
        feature._unlink(element,item)
        feature._notifyUnlink(element,item)




    def replace(feature, element, oldItem, newItem):

        d = feature._getList(element) or []
        p = d.index(oldItem)

        if p!=-1:
            d[p]=newItem
            feature._notifyUnlink(element,oldItem)
            feature._notifyLink(element,newItem)
            element._setBinding(feature.attrName, d)
        else:
            raise ValueError(oldItem,"not found")


    def delete(feature, element):
        """Unset the value of the feature (like __delattr__)"""

        referencedEnd = feature.referencedEnd

        d = feature._getList(element)

        if referencedEnd:
            
            for item in d:
                otherEnd = getattr(item.__class__,referencedEnd)
                otherEnd._unlink(item,element)

        element._delBinding(feature.attrName)


    config.setupObject(delete, verb='delattr')


    def _notifyLink(feature, element, item):

        referencedEnd = feature.referencedEnd

        if referencedEnd:
            otherEnd = getattr(item.__class__,referencedEnd)
            otherEnd._link(item,element)

    def _notifyUnlink(feature, element, item):

        referencedEnd = feature.referencedEnd

        if referencedEnd:
            otherEnd = getattr(item.__class__,referencedEnd)
            otherEnd._unlink(item,element)


    def _link(feature,element,item):
        d=feature._getList(element) or []
        d.append(item)
        element._setBinding(feature.attrName, d)
        

    def _unlink(feature,element,item):
        d=feature._getList(element) or []
        d.remove(item)
        element._setBinding(feature.attrName, d)






















class Reference(Collection):

    __class_implements__ = IReference

    upperBound = 1


    def get(feature, element):
        vals = feature._getList(element)
        if vals: return vals[0]


    def set(feature, element, val):
        feature.__delete__(element)
        feature.getMethod(element,'add')(val)


























class Sequence(Collection):

    __class_implements__ = ISequence

    isOrdered = 1

    newVerbs = Items(
        insertBefore = 'insert%(initCap)sBefore',
    )

    def insertBefore(feature, element, oldItem, newItem):

        d = feature._getList(element)
        
        ub = feature.upperBound
        if ub and len(d)>=ub:
            raise ValueError("Too many items")

        i = -1
        if d: i = d.index(oldItem)

        if i!=-1:
            d.insert(i,newItem)
            element._setBinding(feature.attrName, d)
            feature._notifyLink(element,newItem)
        else:
            raise ValueError(oldItem,"not found")














class Classifier(binding.Base):
    """Basis for all flavors"""

class PrimitiveType(Classifier):
    """A primitive type (e.g. Boolean, String, etc.)"""

class Enumeration(Classifier):
    """An enumerated type"""

class DataType(Classifier):
    """A complex datatype"""

class ElementMeta(DataType.__class__, Persistent.__class__):
    pass


class Element(DataType, Persistent):
    """A (potentially persistent) domain element"""

    __implements__ = IElement
    __metaclass__  = ElementMeta

    def _setBinding(self,attr,value):
        self._p_changed = True
        self.__dict__[attr]=value

    def _delBinding(self,attr):
        if attr in self.__dict__:
            self._p_changed = True
            del self.__dict__[attr]


config.setupModule()
























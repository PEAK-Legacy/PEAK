"""Basic implementation of a domain metamodel"""

from peak.api import *
from peak.model.interfaces import *
from peak.model.interfaces import __all__ as allInterfaces

from Persistence import Persistent
from Persistence.cPersistence import GHOST

from UserList import UserList
from peak.util.ListProxy import ListProxy

from peak.model.method_exporter import MethodExporter


__all__ = [
    'App','Service', 'MethodExporter', 'FeatureMC',
    'StructuralFeature', 'Field', 'Collection', 'Reference', 'Sequence',
    'Classifier','PrimitiveType','Enumeration','DataType','Element',
    'LazyLoader', 'PersistentQuery', 'QueryLink',
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
        return element



























class FeatureMC(MethodExporter):

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
        
class SFMC(binding.Component.__class__, FeatureMC):
    pass


class StructuralFeature(binding.Component):

    __metaclass__ = SFMC

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
        return element._getBinding(feature.attrName, [])
        
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

        d = feature._getList(element)
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
        d=feature._getList(element)
        d.append(item)
        element._setBinding(feature.attrName, d)
        

    def _unlink(feature,element,item):
        d=feature._getList(element)
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
        d = self.__dict__
        
        if d.get(attr) is not value or not isinstance(value,Persistent):
            self._p_changed = True
            d[attr]=value

    def _getBinding(self,attr,default=None):

        ob = self.__dict__.get(attr,default)

        if isinstance(ob,LazyLoader):
            del self.__dict__[attr]
            ob.load(self,attr)
            return self._getBinding(attr,default)

        return ob

    def _delBinding(self,attr):
        if attr in self.__dict__:
            self._p_changed = True
            del self.__dict__[attr]

    def setParentComponent(self, parentComponent, componentName=None):
        if parentComponent is not None:
            self._p_jar = parentComponent
        self._p_oid = componentName

    def getParentComponent(self):
        return self._p_jar

    def getComponentName(self):
        return self._p_oid

class PersistentQuery(Persistent,ListProxy):

    """An immutable, persistent ListProxy for query results"""

    __slots__ = 'data', '__weakref__'

    def __getstate__(self):
        return self.data

    def __setstate__(self,state):
        self.data = list(state)






























class QueryLink(ListProxy):

    """PersistentQuery proxy for use in Collection, Sequence, or Reference"""

    __cacheData = None
    __localData = None

    def __init__(self, query):
        self.__query = query


    def data(self):
        # Discard cached form of query data when underlying query reloaded
        if self.__cacheData is not self.__query.data:
            self.__cacheData = self.__query.data
            self.__localData = self.__cacheData[:]
            
        return self.__localData

    data = property(data)


    def __isActive(self):
        return self.__query._p_state <> GHOST


    def __setitem__(self, i, item):
        if self.__isActive():
            self.data[i]=item

    def __delitem__(self, i):
        if self.__isActive():
            del self.data[i]


    def __setslice__(self, i, j, other):
        if self.__isActive():
            i = max(i, 0); j = max(j, 0)
            self.data[i:j] = self._cast(other)


    def __delslice__(self, i, j):
        if self.__isActive():
            i = max(i, 0); j = max(j, 0)
            del self.data[i:j]
    

    def __iadd__(self, other):  # XXX
        if self.__isActive():
            self.data += self._cast(other)
        return self


    def __imul__(self, n):      # XXX
        if self.__isActive():
            self.data *= n
        return self


    def append(self, item):
        if self.__isActive():
            self.data.append(item)


    def insert(self, i, item):
        if self.__isActive():
            self.data.insert(i, item)


    def remove(self, item):
        if self.__isActive():
            self.data.remove(item)


    def extend(self, other):
        if self.__isActive():
            self.data.extend(self._cast(other))





class LazyLoader(object):

    """Abstract base for lazy loaders of persistent features"""

    def load(self, ob, attrName):
        """Load 'ob' at least with 'attrName'

        Note that a lazy loader is allowed to load all the attributes it
        knows how to, as long as it only overwrites *itself* in the object's
        dictionary.  That is, if an attribute to be read has already been
        written to, it should not reload that attribute.

        This method is not required to return a value, and it can ignore
        the 'attrName' parameter as long as it is certain that the 'attrName'
        attribute will be loaded.
        """
        raise NotImplementedError


config.setupModule()
























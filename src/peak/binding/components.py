"""Basic, in-memory implementation of the Service-Element-Feature pattern"""

from TW.API import *
from TW.SEF.Interfaces import *
from TW.SEF.Interfaces import __all__ as allInterfaces

from types import TupleType
from Interface import Standard


__all__ = [
    'Base','App','Service','TypeService','DynamicBinding','StaticBinding',
    'StructuralFeature', 'Field', 'Collection', 'Reference', 'Sequence',
    'Classifier','PrimitiveType','Enumeration','DataType','Element',
    'bindTo', 'requireBinding',
]


# We export the interfaces too, so people don't have to dig for them...

__all__ += allInterfaces



class DynamicBindingMC(Meta.AssertInterfaces):

    def __get__(self, obj, typ=None):
        if obj is None: return self        
        newOb = self()
        newOb._setSEFparent(obj)
        obj.__dict__[newOb._componentName] = newOb
        return newOb


class DynamicBinding(object):

    __metaclass__ = DynamicBindingMC




class bindTo(object):

    """Automatically look up and cache a relevant service

        Usage::

            class someClass(SEF.Service):

                thingINeed = SEF.bindTo("path.to.service")

        'someClass' can then refer to 'self.thingINeed' instead of
        calling 'self.getService("path.to.service")' repeatedly.
    """
    
    __implements__ = INamedDescriptor


    def __init__(self,targetName):
        self.targetName = targetName


    def copyWithName(self,newName):
        from copy import copy
        newOb = copy(self)
        newOb._componentName = newName
















    def __get__(self, obj, typ=None):

        if obj is None: return self

        d = obj.__dict__
        n = self._componentName
        t = self.targetName

        if not n:
            raise TypeError(
                "%s used in type which does not support NamedDescriptors"
                % self
            )
        d[n] = None

        newOb = obj.getSEFparent()
        if newOb is None: newOb = obj
        newOb = newOb.getService(t)

        if newOb is None:
            del d[n]
            raise NameError("%s not found binding %s" % (t, n))

        d[n] = newOb
        return newOb
















class requireBinding(bindTo):

    """Placeholder for a binding that should be (re)defined by a subclass"""

    def __init__(self,description=""):
        self.description = description
    
    def __get__(self, obj, typ=None):
    
        if obj is None: return self

        raise NameError("Class %s must define %s; %s"
            % (obj.__class__.__name__, self._componentName, self.description)
        )



























class Base(object):

    """Base for all S-E-F classes"""

    __metaclasses__  = Meta.AssertInterfaces, Meta.ClassInit
    __implements__ = ISEF
    _sefParent     = None

    def getService(self,name=None):

        if name:
            if not isinstance(name,TupleType):
                name = tuple(name.split('.'))
                
            if hasattr(self,name[0]):
                o = getattr(self,name[0])
                if len(name)==1:
                    return o
                else:
                    return o.getService(name[1:])
            else:    
                parent = self.getSEFparent()
                if parent is not None:
                    return parent.getService(name)
        else:                
            return self.getSEFparent()


    def _setSEFparent(self,parent):
        from weakref import ref
        self.getSEFparent = ref(parent)

    def getSEFparent(self):
        return None

    def _componentName(self):
        return self.__class__.__name__

    _componentName = property(_componentName)


    def __class_init__(thisClass, newClass, next):
        
        if __proceed__ is not None:
            __proceed__(thisClass, newClass, next)
        else:
            next().__class_init__(newClass,next)

        for k,v in newClass.__dict__.items():
            if hasattr(v,'copyWithName') and isNamedDescriptor(v):
                setattr(newClass, k, v.copyWithName(k))































class App(Base):

    """Application class"""

    def newElement(self,elementType,*args,**kw):
        element = apply(getattr(self,elementType),args,kw)  # XXX won't do dotted names
        element._fData = {}
        element._setSEFparent(self)
        return element


class Service(DynamicBinding, Base):

    """Instance (as opposed to class)"""

    __implements__ = IService
    

class TypeService(Service):

    """Service that supports a (possibly abstract) class"""

    __implements__ = ITypeService


class StaticBinding(object):
    pass














class StructuralFeature(DynamicBinding, Base):

    # XXX lowerBound = Eval("isRequired and 1 or 0")
    # XXX lowerBound.copyIntoSubclasses = 1

    isRequired    = 0  # XXX SubclassDefault(0)

    upperBound    = None    # None means unbounded upper end

    isOrdered     = 0
    isChangeable  = 1       # default is to be changeable

    referencedEnd = None    # and without an 'other end'
    referencedType = None

    def getElement(self):
        return self.getSEFparent()
        
    def getService(self,name=None):
        return self.getSEFparent().getService(name)

    def getReferencedType(self):
        return self.getService(self.referencedType)

    def _getData(self,default=()):
        return self.getSEFparent()._fData.get(self._componentName,default)

    def _setData(self,value):
        self.getSEFparent()._fData[self._componentName]=value

    def _delData(self):
        del self.getSEFparent()._fData[self._componentName]

    def _hasData(self):
        return self.getSEFparent()._fData.has_key(self._componentName)






class Field(StructuralFeature):

    __implements__ = IValue
    
    upperBound = 1

    def __call__(self):
        """Return the value of the feature"""
        return self._getData(None)

    def values(self):
        """Return the value(s) of the feature as a sequence, even if it's a single value"""
        v=self._getData(NOT_FOUND)
        if v is NOT_FOUND: return ()
        return v,

    def clear(self):
        """Unset the value of the feature (like __delattr__)"""
        if self._hasData():
            self._delData()

    def set(self,value):
        """Set the value of the feature to value"""
        if self.isChangeable:
            self._set(value)
        else:
            raise TypeError,("Read-only field %s" % self._componentName)

    def _set(self,value):
        self.clear()
        self._setData(value)










class Collection(StructuralFeature):

    __implements__ = ICollection


    def set(self,value):
        """Set the value of the feature to value"""
        self._set(value)


    def addItem(self,item):
        """Add the item to the collection/relationship, reject if multiplicity exceeded"""
        
        ub = self.upperBound
        
        if not ub or len(self)<ub:
            self._notifyLink(item)
            self._link(item)
        else:
            raise ValueError


    def removeItem(self,item):
        """Remove the item from the collection/relationship, if present"""
        self._unlink(item)
        self._notifyUnlink(item)


    def replaceItem(self,oldItem,newItem):
        d = self._getData([])
        p = d.index(oldItem)
        if p!=-1:
            d[p]=newItem
            self._setData(d)
            self._notifyUnlink(oldItem)
            self._notifyLink(newItem)
        else:
            raise ValueError    # XXX



    def __call__(self):
        """Return the value of the feature"""
        return self._getData()


    def values(self):
        """Return the value(s) of the feature as a sequence, even if it's a single value"""
        return self._getData()


    def clear(self):
        """Unset the value of the feature (like __delattr__)"""

        referencedEnd = self.referencedEnd

        d = self._getData()

        if referencedEnd:
            element = self.getElement()
            for item in d:
                otherEnd = getattr(item,referencedEnd)
                otherEnd._unlink(element)

        if d:
            self._delData()


    def __len__(self):
        return len(self._getData())

    def isEmpty(self):
        return len(self._getData())==0

    def isReferenced(self,item):
        return item in self._getData()






    def _notifyLink(self,item):
        referencedEnd = self.referencedEnd
        if referencedEnd:
            otherEnd = getattr(item,referencedEnd)
            otherEnd._link(self.getElement())

    def _notifyUnlink(self,item):
        referencedEnd = self.referencedEnd
        if referencedEnd:
            otherEnd = getattr(item,referencedEnd)
            otherEnd._unlink(self.getElement())


    def _set(self,value):
        self.clear()
        self._setData(value)


    def _link(self,element):
        d=self._getData([])
        d.append(element)
        self._setData(d)

    def _unlink(self,element):
        d=self._getData([])
        d.remove(element)
        self._setData(d)














class Reference(Collection):

    __implements__ = IReference

    upperBound = 1

    def __call__(self):
        """Return the value of the feature"""
        return self._getData(None)

    def _set(self,value):
        self.clear()
        self._setData([value])


class Sequence(Collection):

    __implements__ = ISequence

    isOrdered = 1

    def insertBefore(self,oldItem,newItem):

        d = self._getData([])
        
        ub = self.upperBound
        if ub and len(d)>=ub:
            raise ValueError    # XXX

        i = -1
        if d: i = d.index(element)

        if i!=-1:
            d.insert(i,newItem)
            self._setData(d)
            self._notifyLink(newItem)
        else:
            raise ValueError    # XXX
    


class Classifier(StaticBinding, Base):
    """Basis for all flavors"""
            
class PrimitiveType(Classifier):
    """A primitive type (e.g. Boolean, String, etc.)"""

class Enumeration(DynamicBinding, Classifier):
    """An enumerated type"""

class DataType(Classifier):
    """A complex datatype"""

class Element(DataType):
    """An element in its own right"""
    __implements__ = IElement


setupModule()
























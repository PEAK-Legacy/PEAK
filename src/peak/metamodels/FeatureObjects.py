"""SEF implementation variant that uses directly accessible feature objects

    This module exists primarily for backward compatibility with the XMI,
    UML, and Query frameworks.  Updating them to use 'setX()'-style methods
    isn't a high priority for me at present, and it's a rather involved task
    since many concepts need to be reworked, features may need renaming or
    other metadata, etc.
"""

from peak.api import *
from peak.model.interfaces import *

from Interface.Standard import Class as IClass

import peak.model.api

__bases__ = peak.model.api,
























class StructuralFeature(binding.AutoCreated):

    __metaclasses__ = ()    # prevents us from being a 'FeatureMC' instance

    # XXX lowerBound = Eval("isRequired and 1 or 0")
    # XXX lowerBound.copyIntoSubclasses = 1

    isRequired    = 0  # XXX SubclassDefault(0)

    upperBound    = None    # None means unbounded upper end

    isOrdered     = 0
    isChangeable  = 1       # default is to be changeable

    referencedEnd = None    # and without an 'other end'
    referencedType = None

    def getElement(self):
        return self.getParentComponent()
        
    def lookupComponent(self,name=None):
        return self.getParentComponent().lookupComponent(name)

    def getReferencedType(self):
        return self.lookupComponent(self.referencedType)

    def _getData(self,default=()):
        return self.getParentComponent()._fData.get(self._componentName,default)

    def _setData(self,value):
        self.getParentComponent()._fData[self._componentName]=value

    def _delData(self):
        del self.getParentComponent()._fData[self._componentName]

    def _hasData(self):
        return self.getParentComponent()._fData.has_key(self._componentName)




class Field(StructuralFeature):

    __class_implements__ = IClass
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

    __class_implements__ = IClass
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

    __class_implements__ = IClass
    __implements__ = IReference

    upperBound = 1

    def __call__(self):
        """Return the value of the feature"""
        return self._getData(None)

    def _set(self,value):
        self.clear()
        self._setData([value])

    set = Collection.set.im_func

























class Sequence(Collection):

    __class_implements__ = IClass
    __implements__ = ISequence

    isOrdered = 1

    def insertBefore(self,oldItem,newItem):

        d = self._getData([])
        
        ub = self.upperBound
        if ub and len(d)>=ub:
            raise ValueError    # XXX

        i = -1
        if d: i = d.index(oldItem)

        if i!=-1:
            d.insert(i,newItem)
            self._setData(d)
            self._notifyLink(newItem)
        else:
            raise ValueError    # XXX
    
binding.setupModule()

"""Persistent Elements"""

from peak.api import *

from structural import Type
from interfaces import *

from Persistence import Persistent
from Persistence.cPersistence import GHOST

from peak.storage.lazy_loader import LazyLoader


__all__ = [ 'Element' ]


class ElementClass(Type.__class__, Persistent.__class__):
    pass























class Element(Type, Persistent):

    """A persistent domain element"""

    __implements__ = binding.IBindingAPI
    __metaclass__  = ElementClass

    def setParentComponent(self, parentComponent, componentName=None):
        if parentComponent is not None:
            self._p_jar = parentComponent
        self._p_oid = componentName

    def getParentComponent(self):
        return self._p_jar

    def getComponentName(self):
        return self._p_oid


    def _bindingChanging(self, attr, value=NOT_FOUND, isSlot=False):

        old = self._getBinding(attr,NOT_FOUND,isSlot)

        if old is not value or not isinstance(value,Persistent):
            self._p_changed = True


    def _postGet(self,attr,value,isSlot=False):
    
        if isinstance(value,LazyLoader):

            if isSlot:
                getattr(self.__class__,attr).__delete__(self)
            else:
                del self.__dict__[attr]

            value.load(self,attr)   # XXX           
            return self._getBinding(attr,NOT_FOUND)

        return value





"""Persistent Elements"""

from peak.api import *

from structural import DataType
from interfaces import *

from Persistence import Persistent
from Persistence.cPersistence import GHOST

from peak.storage.lazy_loader import LazyLoader


__all__ = [ 'Element' ]


class ElementClass(DataType.__class__, Persistent.__class__):
    pass























class Element(DataType, Persistent):

    """A (potentially persistent) domain element"""

    __implements__ = IElement
    __metaclass__  = ElementClass
    __setattr__    = binding.Base.__setattr__

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

    def getParentComponent(self):   return self._p_jar
    def getComponentName(self):     return self._p_oid




























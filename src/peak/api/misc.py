from Meta import NamedDescriptor

__all__ = ['Once', 'OnceClass']


class Once(NamedDescriptor):    

    """Usage:: Once(function)"""
    
    def __init__(self, func):
        self.computeValue = func

    attrName = None

    def __get__(self, obj, typ=None):

        if obj is None: return self

        d = obj.__dict__
        n = self.attrName

        if not n:
            raise TypeError(
                "%s used in type which does not support NamedDescriptor"
                % self
            )
            
        d[n] = value = self.computeValue(obj, d, n)
        return value


    def computeValue(self, obj, instanceDict, attrName):
        raise NotImplementedError


    def copyWithName(self,newName):
        from copy import copy
        newOb = copy(self)
        newOb.attrName = newName
        return newOb

class OnceClass(Once, type):

    """Use this one as a metaclass..."""

    def __init__(klass, name, bases, dict):
        # bypass Once.__init__...  this is a bit of a hack...
        super(Once,klass).__init__(name,bases,dict)
        
    def computeValue(self, obj, instanceDict, attrName):
        return self(obj)

    def copyWithName(self,newName):
        newOb = self.__class__(
            self.__name__, self.__mro__, {'__module__':self.__module__}
        )
        newOb.attrName = newName
        return newOb


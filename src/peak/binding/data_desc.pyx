cdef extern from "Python.h":
    int PyType_Check(object o)

cdef extern from "py_obj.h":
    object GET_DICTIONARY(object o)

cdef extern from "object.h":
    pass


from peak.api import NOT_FOUND


class data_descr(object):

    """Data descriptor base class for 'Once' bindings"""
    
    def __set__(self, obj, value):
        d = GET_DICTIONARY(obj)
        d[self.attrName] = value


    def __delete__(self, obj):
        d = GET_DICTIONARY(obj)
        del d[self.attrName]















        
    def __get__(self, obj, typ=None):
    
        """Compute the attribute value and cache it

            Note: fails if attribute name not supplied or doesn't reference
            this descriptor!
        """

        if obj is None:
            return self

        n = self.attrName
        d = GET_DICTIONARY(obj)

        if n in d:
            return d[n]
            
        if not n or getattr(obj.__class__, n, None) is not self:
            self.usageError()

        d[n] = NOT_FOUND    # recursion guard

        try:
            value = self.computeValue(obj, obj.__dict__, n)
        except:
            del d[n]
            raise

        setattr(obj,n,value)
        return value



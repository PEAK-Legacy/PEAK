cdef extern from "Python.h":
    int PyType_Check(object o)
    object PyDict_New()
    void *PyDict_GetItem(object dict,object key)

cdef extern object GET_DICTIONARY(object o)

cdef void *_NOTFOUND

from peak.api import NOT_FOUND


cdef class OnceDescriptor:

    """Data descriptor base class for 'Once' bindings"""
    
    cdef object attrName

    def __set__(self, obj, void *value):

        d = GET_DICTIONARY(obj)

        if value:
            d[self.attrName] = <object>value

        else:
            del d[self.attrName]














    def __get__(self, void *obj, void *typ):
    
        # Compute the attribute value and cache it

        # Note: fails if attribute name not supplied or doesn't reference
        # this descriptor!

        if not obj:
            return self

        ob = <object> obj
        n = self.attrName
        d = GET_DICTIONARY(ob)

        obj = PyDict_GetItem(d, n)

        if obj:
            # XXX should check for a lock here instead, and acquire it

            if obj == _NOTFOUND:
                raise AttributeError, n

            return <object> obj
            
        if not n or getattr(ob.__class__, n, None) is not self:
            self.usageError()

        d[n] = <object> _NOTFOUND  # XXX recursion guard; should be a lock

        try:
            value = self.computeValue(ob, d, n)
        except:
            del d[n]
            raise

        d[n] = value

        return value





cdef class __attrName_Descriptor:

    """The attribute name this descriptor will handle."""


    def __get__(self, void *obj, void *typ):

        if not obj:
            return self

        return (<OnceDescriptor>obj).attrName
            

    def __set__(self, OnceDescriptor obj, void *value):
        if not value:
            obj.attrName = None
        else:
            obj.attrName = <object>value


OnceDescriptor_attrName = __attrName_Descriptor()

__all__ = ['OnceDescriptor_attrName', 'OnceDescriptor']

_NOTFOUND = <void *> NOT_FOUND

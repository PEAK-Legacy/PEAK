cdef extern from "Python.h":
    int PyType_Check(object o)
    object PyDict_New()
    void *PyDict_GetItem(object dict,object key)
    struct _object:
        void *ob_type

cdef extern object GET_DICTIONARY(object o)

cdef void *_NOTFOUND
cdef void *_lockType

from peak.api import NOT_FOUND
from peak.util.threads import get_ident


cdef class bindingLock:

    cdef int id

    def __new__(self):
        self.id = get_ident()


_NOTFOUND = <void *> NOT_FOUND
_lockType = <void *> bindingLock


cdef int isLock(void *obj):
    return (<_object *>obj).ob_type == _lockType

cdef int isOurs(void *obj):
    cdef int id
    cdef bindingLock lock
    id = get_ident()
    lock = <bindingLock> obj
    return lock.id == id




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

            if obj == _NOTFOUND:
                raise AttributeError, n

            elif (<_object *>obj).ob_type == _lockType:

                if isOurs(obj):
                    raise AttributeError(
                        "Recursive attempt to compute attribute", n
                    )

            else:
                return <object> obj

        else:
            # claim our spot
            d[n] = bindingLock()

        try:
            if not n or getattr(ob.__class__, n, None) is not self:
                self.usageError()

            value = self.computeValue(ob, d, n)

        except:

            # We can only remove the guard if it was put in
            # place by this thread, and another thread hasn't
            # already finished the computation

            obj = PyDict_GetItem(d, n)

            if obj and isLock(obj) and isOurs(obj):
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



"""'Once' objects and classes"""

from meta import ActiveDescriptor
from weakref import ref
from peak.api import NOT_FOUND

__all__ = ['Once', 'New', 'Copy', 'WeakBinding', 'OnceClass']


def New(obtype, name=None, provides=None):

    """One-time binding of a new instance of 'obtype'

    Usage::

        class someClass(binding.Component):

            myDictAttr = binding.New(dict)

            myListAttr = binding.New(list)

    The 'myDictAttr' and 'myListAttr' will become empty instance
    attributes on their first access attempt from an instance of
    'someClass'.
    
    This is basically syntactic sugar for 'Once' to create an empty
    instance of a type.  The same rules apply as for 'Once' about
    whether the 'name' parameter is required.  (That is, you need it if you're
    using this in a class whose metaclass doesn't support ActiveDescriptors,
    such as when you're not deriving from a standard PEAK base class.)
    """

    return Once( (lambda s,d,a: obtype()), name, provides)








def Copy(obj, name=None, provides=None):

    """One-time binding of a copy of 'obj'

    Usage::

        class someClass(binding.Component):

            myDictAttr = binding.Copy( {'foo': 2} )
            
            myListAttr = binding.Copy( [1,2,'buckle your shoe'] )

    The 'myDictAttr' and 'myListAttr' will become per-instance copies of the
    supplied initial values on the first attempt to access them from an
    instance of 'someClass'.

    This is basically syntactic sugar for 'Once' to create copies using
    the Python 'copy.copy()' function.  The same rules apply as for
    'Once' about whether the 'name' parameter is required.  (That is, you need
    it if you're using this in a class whose metaclass doesn't support
    ActiveDescriptors, such as when you're not deriving from a standard PEAK
    base class.)
    """
    

    from copy import copy
    return Once( (lambda s,d,a: copy(obj)), name, provides)














class Once(ActiveDescriptor):

    """One-time Properties
    
        Usage ('Once(callable,name)')::

            class someClass(object):

                def anAttr(self, __dict__, attrName):
                    return self.foo * self.bar

                anAttr = Once(anAttr, 'anAttr')

        When 'anInstanceOfSomeClass.anAttr' is accessed for the first time,
        the 'anAttr' function will be called, and saved in the instance
        dictionary.  Subsequent access to the attribute will return the
        cached value.  Deleting the attribute will cause it to be computed
        again on the next access.

        The 'name' argument is optional.  If not supplied, it will default
        to the '__name__' of the supplied callable.  (So in the usage
        example above, it could have been omitted.)

        'Once' is a 'binding.meta.ActiveDescriptor', so if you place an
        instance of it in a class which supports descriptor naming (i.e.,
        has a metaclass derived from 'binding.meta.ActiveDescriptors'), it will
        automatically know the correct attribute name to use in the instance
        dictionary, even if it is different than the supplied name or name of
        the supplied callable.  However, if you place a 'Once' instance in a
        class which does *not* support descriptor naming, and you did not
        supply a valid name, attribute access will fail with a 'TypeError'.
    """

    attrName = None
    provides = None
    
    def __init__(self, func, name=None, provides=None):
        self.computeValue = func
        self.attrName = name or getattr(func,'__name__',None)
        self._provides = provides

    def __get__(self, obj, typ=None):
    
        """Compute the attribute value and cache it

            Note: fails if attribute name not supplied or doesn't reference
            this descriptor!
        """
        if obj is None: return self

        d = obj.__dict__
        n = self.attrName

        if not n or getattr(obj.__class__,n) is not self:
            self.usageError()

        d[n] = NOT_FOUND    # recursion guard

        try:
            d[n] = value = self.computeValue(obj, d, n)
        except:
            del d[n]
            raise
            
        return value


    def usageError(self):            
        raise TypeError(
            "%s used in type which does not support ActiveDescriptors"
            "and a name was not supplied"
            % self
        )


    def computeValue(self, obj, instanceDict, attrName):
        raise NotImplementedError





    def activate(self,klass,attrName):

        if attrName !=self.attrName:

            from copy import copy
            newOb = copy(self)

            newOb.attrName = attrName
            setattr(klass, attrName, newOb)

        klass.__volatile_attrs__.add(attrName)
        
        if self._provides is not None:

            if not klass.__dict__.has_key('__class_provides__'):
                cp = EigenRegistry()
                for c in klass.__mro__:
                    if c.__dict__.has_key('__class_provides__'):
                        cp.update(c.__class_provides__)
                klass.__class_provides__ = cp

            klass.__class_provides__.register(self._provides,attrName)



















class WeakBinding(Once):

    """Like Once, but keeps a weak reference only
    
       This binding descriptor saves a weak reference to its target in
       the object's instance dictionary, and dereferences it on each access.
       It therefore supports '__set__' and '__delete__' as well as '__get__'
       methods, and retrieval is slower than for other 'Once' attributes.  But
       it can prevent the creation of circular reference garbage."""

    def __get__(self, obj, typ=None):
    
        if obj is None: return self

        d = obj.__dict__
        n = self.attrName

        if not n or getattr(obj.__class__,n) is not self:
            self.usageError()

        r = d.get(n)

        if r is None:
            d[n] = NOT_FOUND    # recursion guard
            try:
                d[n] = r = ref(self.computeValue(obj, d, n))
            except:
                del d[n]; raise

        return r()

    def __set__(self, obj, val):

        n = self.attrName

        if not n or getattr(obj.__class__,n) is not self:
            self.usageError()

        obj.__dict__[n] = ref(val)


    def __delete__(self, obj):

        n = self.attrName

        if not n or getattr(obj.__class__,n) is not self:
            self.usageError()

        del obj.__dict__[n]

































class OnceClass(Once, type):

    """A variation on Once that can be used as a metaclass

        Usage::

            class outer(object):

                class inner(object):
                    __metaclass__ = OnceClass

                    def __init__(self, obj, instDict, attrName):
                        ...

        When 'anOuterInstance.inner' is accessed, an instance of
        'inner' will be created and cached in the instance dictionary,
        as per 'Once'.  See 'Once' for more details on the mechanics.
        The class name will serve as a default attribute name.
    """

    def __init__(klass, name, bases, dict):
        # Hack to bypass Once.__init__, which is the wrong signature!
        super(Once,klass).__init__(name,bases,dict)
        klass.attrName = name

    def computeValue(self, *args):
        return self(*args)
    
    def activate(self,klass,attrName):

        if attrName !=self.attrName:
            setattr(klass, attrName, Once(self.computeValue, attrName))

        klass.__volatile_attrs__.add(attrName)

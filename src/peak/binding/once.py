"""'Once' objects and classes"""

from peak.api import NOT_FOUND
from peak.util.EigenData import EigenRegistry
from peak.util.imports import importObject
from interfaces import IBindingFactory

__all__ = [
    'Once', 'New', 'Copy', 'OnceClass', 'ActiveDescriptors',
    'ActiveDescriptor',
]


class ActiveDescriptors(type):

    """Type which gives its descriptors a chance to find out their names"""
    
    def __init__(klass, name, bases, dict):

        for k,v in dict.items():
            if isinstance(v,ActiveDescriptor):
                v.activate(klass,k)

        super(ActiveDescriptors,klass).__init__(name,bases,dict)


class ActiveDescriptor(object):

    """This is just a (simpler sort of) interface assertion class""" 

    def activate(self,klass,attrName):
        """Informs the descriptor that it is in 'klass' with name 'attrName'"""
        raise NotImplementedError








def New(obtype, bindToOwner=None, name=None, provides=None, doc=None):

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

    def mkNew(s,d,a):
        factory = importObject(obtype)

        if bindToOwner or (
            bindToOwner is None and IBindingFactory.isImplementedBy(factory)
        ):
            return factory(s,a)
        else:
            return factory()

    return Once( mkNew, name, provides, doc)







def Copy(obj, name=None, provides=None, doc=None):

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
    return Once( (lambda s,d,a: copy(obj)), name, provides, doc)














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
    _provides = None
    
    def __init__(self, func, name=None, provides=None, doc=None):
        self.computeValue = func
        self.attrName = self.__name__ = name or getattr(func,'__name__',None)
        self._provides = provides; self.__doc__ = doc or getattr(func,'__doc__','')

    def __get__(self, obj, typ=None):
    
        """Compute the attribute value and cache it

            Note: fails if attribute name not supplied or doesn't reference
            this descriptor!
        """
        if obj is None: return self

        d = obj.__dict__
        n = self.attrName

        if not n or getattr(obj.__class__,n,None) is not self:
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
            "%s was used in a type which does not support ActiveDescriptors,"
            " but a valid attribute name was not supplied"
            % self
        )


    def computeValue(self, obj, instanceDict, attrName):
        raise NotImplementedError





    def activate(self,klass,attrName):

        if attrName !=self.attrName:
            setattr(klass, attrName, self._copyWithName(attrName))

        if self._provides is not None:

            if not klass.__dict__.has_key('__class_provides__'):

                cp = EigenRegistry()

                for c in klass.__mro__:
                    if c.__dict__.has_key('__class_provides__'):
                        cp.update(c.__class_provides__)

                klass.__class_provides__ = cp

            klass.__class_provides__.register(self._provides,attrName)


    def _copyWithName(self, attrName):

        from copy import copy
        newOb = copy(self)

        newOb.attrName = attrName
        return newOb
        













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


    def _copyWithName(self,attrName):
        return Once(self.computeValue, attrName)



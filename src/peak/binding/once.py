"""Miscellaneous API functions, classes, etc."""

from Meta import NamedDescriptor

__all__ = ['Once', 'OnceClass']




































class Once(NamedDescriptor):

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

        'Once' is a 'Meta.NamedDescriptor', so if you place an instance of it
        in a class which supports descriptor naming (i.e., has a metaclass
        derived from 'Meta.NamedDescriptors'), it will automatically know the
        correct attribute name to use in the instance dictionary, even if it
        is different than the supplied name or name of the supplied callable.
        However, if you place a 'Once' instance in a class which does *not*
        support descriptor naming, and you did not supply a valid name,
        attribute access will fail with a 'TypeError'.
    """

    attrName = None

    def __init__(self, func, name=None):
        self.computeValue = func
        self.attrName = name or getattr(func,'__name__',None)



    def __get__(self, obj, typ=None):
    
        """Compute the attribute value and cache it

            Note: fails if attribute name not supplied or doesn't reference
            this descriptor!
        """
        if obj is None: return self

        d = obj.__dict__
        n = self.attrName

        if not n or getattr(obj.__class__,n) is not self:
            raise TypeError(
                "%s used in type which does not support NamedDescriptor"
                % self
            )
            
        d[n] = value = self.computeValue(obj, d, n)
        return value


    def computeValue(self, obj, instanceDict, attrName):
        raise NotImplementedError


    def copyWithName(self,newName):
    
        if newName==self.attrName:
            return self
            
        from copy import copy
        newOb = copy(self)
        newOb.attrName = newName
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
    
    def copyWithName(self, newName):
        if newName==self.attrName:
            return self
        return Once(self.computeValue, newName)


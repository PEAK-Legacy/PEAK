"""Miscellaneous API functions, classes, etc."""

from Meta import ActiveDescriptor

__all__ = ['Once', 'OnceClass']


def Items(mapping=None, **kwargs):

    """Convert 'mapping' and/or 'kwargs' into a list of '(key,val)' items

        Key/value item lists are often easier or more efficient to manipulate
        than mapping objects, so TransWarp API's tend to use such lists as
        a preferred parameter format.  Sometimes, however, the syntactic sugar
        of keyword items, possibly in combination with an existing mapping
        object, is desired.  In those cases, the 'Items()' function can be
        used .

        'Items()' takes an optional mapping and optional keyword arguments, and
        returns a key/value pair list that contains the items from both the
        mapping and keyword arguments, with the keyword arguments taking
        precedence over (i.e. being later in the list than) the mapping items.
    """

    if mapping:

        i = mapping.items()

        if kwargs:
            i.extend(kwargs.items())

        return i

    elif kwargs:
        return kwargs.items()

    else:
        return []



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

        'Once' is a 'Meta.ActiveDescriptor', so if you place an instance of it
        in a class which supports descriptor naming (i.e., has a metaclass
        derived from 'Meta.ActiveDescriptors'), it will automatically know the
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
                "%s used in type which does not support ActiveDescriptors"
                % self
            )
            
        d[n] = value = self.computeValue(obj, d, n)
        return value


    def computeValue(self, obj, instanceDict, attrName):
        raise NotImplementedError


    def activate(self,klass,attrName):

        if attrName !=self.attrName:

            from copy import copy
            newOb = copy(self)

            newOb.attrName = attrName
            setattr(klass, attrName, newOb)

        klass.__volatile_attrs__.add(attrName)




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

"""Metaclasses that are generally useful when working with TransWarp"""

from Modules import setupModule

class ClassInit(type):

    """Lets classes have a '__class_init__(thisClass,newClass,next)' method"""
    
    class _sentinel:
        def __class_init__(thisClass, newClass, next):
            pass

    sentinel = _sentinel()
    

    def __new__(meta, name, bases, dict):
        
        try:
            ci = dict['__class_init__']
        except KeyError:
            pass
        else:
            # Guido take note: a legitimate use for 'classmethod'!
            dict['__class_init__'] = classmethod(ci)

        return super(ClassInit, meta).__new__(meta,name,bases,dict)


    def __init__(newClass, name, bases, dict):

        super(ClassInit, newClass).__init__(name,bases,dict)

        initSupers = iter(
            [base for base in newClass.__mro__
                   if base.__dict__.has_key('__class_init__')
             ]+[ClassInit.sentinel]
        )

        next = initSupers.next
        next().__class_init__(newClass, next)

class AssertInterfaces(type):

    """Work around Zope Interface package's new-style class/metaclass bug
    
        Use this as a metaclass of any new-style class you'd like to have
        properly support '__implements__' and '__class_implements__', as
        current versions of the Zope 'Interface' package can't tell that
        a metaclass instance is really a class-like thing.

        Basically, this does two tricks.  First, it converts any
        '__implements__' value in the class dictionary to an
        'interfaceAssertion' attribute descriptor.  Second, it provides
        'instancesImplements' and 'instancesImplement' methods to its
        instances, so that when looking for 'isImplementedByInstancesOf',
        the 'Interface' package will get the right thing.  There are two
        spellings of the method because the Zope 2.x and Zope 3X versions
        of the package spell it differently.  :(
    """
    
    def __init__(klass, name, bases, dict):
    
        """Convert '__implements__' to a descriptor"""
        
        if dict.has_key('__implements__'):
            imp = dict['__implements__']
            if not isinstance(imp, klass.interfaceAssertion):
                klass.__implements__ = klass.interfaceAssertion(imp)

        super(AssertInterfaces, klass).__init__(name, bases, dict)
        

    def instancesImplements(klass):
        """Tell 'Interface' what our (non-metaclass) instances implement"""
        d = klass.__dict__
        if d.has_key('__implements__'):
            return d['__implements__'].implements

    instancesImplement = instancesImplements



    class interfaceAssertion(object):
    
        """Smart descriptor that returns the right '__implements__'"""
        
        def __init__(self, implements, *extra):
            self.implements = (implements,) + extra

        def __get__(self, ob, typ=None):
        
            """Return '__class_implements__' if retrieved from the class,
                or '__implements__' if retrieved from the instance."""
                
            if ob is None:
                from Interface.Standard import Class
                return getattr(typ,'__class_implements__',Class)

            return self.implements


setupModule()

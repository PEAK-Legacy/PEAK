"""Basic, in-memory implementation of the Service-Element-Feature pattern"""

from once import Once
import meta, modules


__all__ = [
    'Component','AutoCreated',
    'bindTo', 'requireBinding', 'bindToNames', 'bindToParent', 'bindToSelf',
]































class bindTo(Once):

    """Automatically look up and cache a relevant service

        Usage::

            class someClass(binding.AutoCreated):

                thingINeed = binding.bindTo("path.to.service")

        'someClass' can then refer to 'self.thingINeed' instead of
        calling 'self.lookupComponent("path.to.service")' repeatedly.
    """

    singleValue = 1

    def __init__(self,targetName):
        self.targetNames = (targetName,)

    def computeValue(self, obj, instanceDict, attrName):

        instanceDict[attrName] = None   # recursion guard

        parent = obj.getParentComponent()
        if parent is None: parent = obj

        obs = map(parent.lookupComponent, self.targetNames)

        for newOb in obs:
            if newOb is None:
                del instanceDict[attrName]
                raise NameError(
                    "%s not found binding %s" % (self.targetName, attrName)
                )
            elif self.singleValue:
                return newOb

        return tuple(obs)



class bindToNames(bindTo):

    """Automatically look up and cache a sequence of services by name

        Usage::

            class someClass(binding.AutoCreated):

                thingINeed = binding.bindToNames(
                    "path.to.service1", "another.path", ...
                )

        'someClass' can then refer to 'self.thingINeed' to get a tuple of
        services instead of calling 'self.lookupComponent()' on a series of
        names.
    """

    singleValue = 0

    def __init__(self,*targetNames):
        self.targetNames = targetNames




















class bindToParent(Once):

    """Look up and cache a reference to the nth-level parent service

        Usage::

            class someClass(binding.AutoCreated):

                grandPa = binding.bindToParent(2)

       'someClass' can then refer to 'self.grandPa' instead of calling
       'self.getParentComponent().getParentComponent()'.

       This binding descriptor saves a weak reference to its target in
       the object's instance dictionary, and dereferences it on each access.
       It therefore supports '__set__' and '__delete__' as well as '__get__'
       methods, and retrieval is slower than for other 'Once' attributes.  But
       it avoids creating circular reference garbage.
    """

    def __init__(self,level=1):
        self.level = level

    def __get__(self, obj, typ=None):
    
        if obj is None: return self

        d = obj.__dict__
        n = self.attrName

        if not n or getattr(obj.__class__,n) is not self:
            self.usageError()

        ref = d.get(n)

        if ref is None:
            d[n] = ref = self.computeValue(obj, d, n)

        return ref()


    def __set__(self, obj, val):

        n = self.attrName

        if not n or getattr(obj.__class__,n) is not self:
            self.usageError()

        from weakref import ref
        obj.__dict__[n] = ref(val)


    def __delete__(self, obj):

        n = self.attrName

        if not n or getattr(obj.__class__,n) is not self:
            self.usageError()

        del obj.__dict__[n]


    def computeValue(self, obj, instDict, attrName):

        for step in range(self.level):
            newObj = obj.getParentComponent()
            if newObj is None: break
            obj = newObj

        from weakref import ref
        return ref(obj)











def bindToSelf():

    """Weak reference to the 'self' object

    This is just a shortcut for 'bindToParent(0)', and does pretty much what
    you'd expect.  It's handy for objects that provide default support for
    various interfaces in the absence of an object to delegate to.  The object
    can refer to 'self.delegateForInterfaceX.someMethod()', and have
    'delegateForInterfaceX' be a 'bindToSelf()' by default.
    """

    return bindToParent(0)


class requireBinding(Once):

    """Placeholder for a binding that should be (re)defined by a subclass"""

    def __init__(self,description=""):
        self.description = description
    
    def computeValue(self, obj, instanceDict, attrName):
    
        raise NameError("Class %s must define %s; %s"
            % (obj.__class__.__name__, attrName, self.description)
        )















class Component(object):

    """Base for all S-E-F classes"""

    __metaclasses__  = (
        meta.AssertInterfaces, meta.ActiveDescriptors
    )

    def lookupComponent(self,name=None):

        if name:
            if not isinstance(name,tuple):
                name = tuple(name.split('.'))
                
            if hasattr(self,name[0]):
                o = getattr(self,name[0])
                if len(name)==1:
                    return o
                else:
                    return o.lookupComponent(name[1:])
            else:    
                parent = self.getParentComponent()
                if parent is not None:
                    return parent.lookupComponent(name)
        else:                
            return self.getParentComponent()


    def setParentComponent(self,parent):
        from weakref import ref
        self.getParentComponent = ref(parent)

    def getParentComponent(self):
        return None

    def _componentName(self, dict, name):
        return self.__class__.__name__.split('.')[-1]

    _componentName = Once(_componentName)


class AutoCreatable(type):

    """Metaclass for classes which auto-create"""

    def __get__(self, obj, typ=None):

        if obj is None:
            return self

        newOb = self(obj)
        
        obj.__dict__[newOb._componentName] = newOb
        return newOb


class AutoCreated(Component):

    """Class which auto-creates instances for instances of its containing class
    """

    __metaclasses__ = AutoCreatable,

    def __init__(self, parent=None):

        super(AutoCreated,self).__init__()

        if parent is not None:
            self.setParentComponent(parent)













modules.setupModule()
























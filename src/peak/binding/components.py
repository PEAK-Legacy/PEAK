"""Basic binding tools"""

from once import Once
import meta, modules

from weakref import ref
from peak.naming.names import toName, Syntax, CompoundName
from peak.naming.interfaces import NameNotFoundException

    


__all__ = [
    'Component','AutoCreated',
    'bindTo', 'requireBinding', 'bindToNames', 'bindToParent', 'bindToSelf',
    'getRootComponent', 'getParentComponent', 'lookupComponent',
    'acquireComponent', 'globalLookup'
]

_ACQUIRED = object()





















def getParentComponent(component):

    """Return parent of 'component', or 'None' if root or non-component"""

    try:
        gpc = component.getParentComponent
    except AttributeError:
        pass
    else:
        return gpc()


def getRootComponent(component):

    """Return the root component of the tree 'component' belongs to"""

    next = component

    while next is not None:
        component = next
        next = getParentComponent(component)

    return component


def globalLookup(name, component=None):

    """Lookup 'name' in global 'InitialContext', w/'component' in environ"""

    from peak.naming.api import InitialContext
    
    return InitialContext(RELATIVE_TO_COMPONENT=component).lookup(name)









def acquireComponent(component, name):

    """Acquire 'name' relative to 'component', w/fallback to globalLookup()"""

    target = component
    
    while target is not None:

        ob = getattr(target, name, _ACQUIRED)

        if ob is not _ACQUIRED:
            return ob

        target = getParentComponent(target)

    else:
        return globalLookup(name, component)
























ComponentNameSyntax = Syntax(
    direction = 1,
    separator = '/',
)


def ComponentName(nameStr):
    return CompoundName(nameStr, ComponentNameSyntax)


_getFirstPathComponent = dict( (
    ('',   getRootComponent),
    ('.',  lambda x:x),
    ('..', getParentComponent),
) ).get


_getNextPathComponent = dict( (
    ('',   lambda x:x),
    ('.',  lambda x:x),
    ('..', getParentComponent),
) ).get



















def lookupComponent(component, name):

    """Lookup 'name' relative to 'component'

    'name' can be any name acceptable to the 'peak.naming' package.  Strings
    and 'CompoundName' names will be interpreted as paths relative to the
    starting component.  An empty name will return the starting component.
    All other kinds of names, including URL strings and 'CompositeName'
    instances, will be looked up using 'binding.globalLookup()'.
    
    Regardless of how the lookup is processed, a 'naming.NameNotFoundException'
    will be raised if the name cannot be found.
   

    Component Path Syntax

        Paths are '/'-separated attribute names.  Path segments of '.' and
        '..' mean the same as they do in URLs.  A leading '/' (or a
        CompoundName beginning with an empty path segment), will be treated
        as an "absolute path" relative to the component's root component.

        Paths beginning with anything other than '/', './', or '../' are
        acquired, which means that the first path segment will be looked
        up using 'acquireComponent()' before processing the rest of the path.
        (See 'acquireComponent()' for more details.)  If you do not want
        a name to be acquired, simply prefix it with './' so it is relative
        to the starting object.

        All path segments after the first are interpreted as attribute names
        to be looked up, beginning at the component referenced by the first
        path segment.  '.' and '..' are interpreted the same as for the first
        path segment.   
    """

    parsedName = toName(name, ComponentName, 1)

    # URL's and composite names must be handled globally

    if not parsedName.isCompound:
        return globalLookup(name, component)

    if not parsedName:
        # empty name refers to self
        return component

    parts = iter(parsedName)

    attr = parts.next() # first part
    pc = _getFirstPathComponent(attr)

    if pc:
        ob = pc(component)
    else:
        ob = acquireComponent(component,attr)


    resolved = []
    append = resolved.append

    try:
        for attr in parts:
            pc = _getNextPathComponent(attr)
            if pc:
                ob = pc(ob)
            else:
                ob = getattr(ob,attr)
            append(attr)

    except AttributeError:

        raise NameNotFoundException(
            resolvedName = ComponentName(resolved),
            remainingName = ComponentName([attr] + [a for a in parts]),
            resolvedObj = ob
        )

    return ob





class bindTo(Once):

    """Automatically look up and cache a relevant component

        Usage::

            class someClass(binding.Component):

                thingINeed = binding.bindTo("path/to/service")

                getOtherThing = binding.bindTo("some/thing", weak=True)
                
        'someClass' can then refer to 'self.thingINeed' instead of
        calling 'self.lookupComponent("path/to/service")' repeatedly.
        It can also do 'self.getOtherThing()' to get '"some/thing"'.
        (The 'weak' argument, if true, means to bind to a weak reference.)
    """

    singleValue = True

    def __init__(self,targetName,weak=False):

        self.targetNames = (targetName,)
        self.weak = weak

















    def computeValue(self, obj, instanceDict, attrName):

        instanceDict[attrName] = _ACQUIRED   # recursion guard

        names = self.targetNames
        obs   = map(obj.lookupComponent, names)

        for name,newOb in zip(names, obs):

            if newOb is _ACQUIRED:
            
                del instanceDict[attrName]
                raise NameNotFoundError(attrName, resolvedName = name)

            if self.singleValue:
            
                if self.weak:
                    return ref(newOb)
                else:
                    return newOb

        if self.weak:
            obs = map(ref,obs)

        return tuple(obs)
















class bindToNames(bindTo):

    """Automatically look up and cache a sequence of services by name

        Usage::

            class someClass(binding.AutoCreated):

                thingINeed = binding.bindToNames(
                    "path/to/service", "another/path", ...
                )

        'someClass' can then refer to 'self.thingINeed' to get a tuple of
        services instead of calling 'self.lookupComponent()' on a series of
        names.  As with 'bindTo()', a 'weak' keyword argument can be set to
        indicate that the sequence should consist of weak references to the
        named objects.
    """

    singleValue = False

    def __init__(self, *targetNames, **kw):
        self.targetNames = targetNames
        self.weak = kw.get('weak')

















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

    """Thing that can be composed into a component tree, w/binding & lookups"""

    __metaclasses__  = (
        meta.AssertInterfaces, meta.ActiveDescriptors
    )

    # use the global lookupComponent function as a method

    lookupComponent = lookupComponent

    def setParentComponent(self,parent):
        from weakref import ref
        self.getParentComponent = ref(parent)

    def getParentComponent(self):
        return None

    def _componentName(self, dict, name):
        return self.__class__.__name__.split('.')[-1]

    _componentName = Once(_componentName)


















class AutoCreatable(type):

    """Metaclass for components which auto-create when used"""

    def __get__(self, obj, typ=None):

        if obj is None:
            return self

        newOb = self(obj)
        
        obj.__dict__[newOb._componentName] = newOb
        return newOb


class AutoCreated(Component):

    """Component that auto-creates itself in instances of its containing class
    """

    __metaclasses__ = AutoCreatable,

    def __init__(self, parent=None):

        super(AutoCreated,self).__init__()

        if parent is not None:
            self.setParentComponent(parent)













modules.setupModule()
























"""Basic binding tools"""

from __future__ import generators
from once import Once, New
import meta
from peak.config.modules import setupModule

from weakref import WeakValueDictionary

from peak.naming.names import toName, Syntax, CompoundName
from peak.naming.interfaces import NameNotFoundException
from peak.util.EigenData import EigenRegistry, EigenCell

from Interface import Interface
from peak.api import config, NOT_FOUND


__all__ = [
    'Base', 'Component','AutoCreated','Provider','CachingProvider',
    'bindTo', 'requireBinding', 'bindSequence', 'bindToParent', 'bindToSelf',
    'getRootComponent', 'getParentComponent', 'lookupComponent',
    'acquireComponent', 'globalLookup', 'findUtility', 'findUtilities',
    'bindToUtilities',
]


InterfaceClass = Interface.__class__














def Provider(callable):
    return lambda foundIn, forObj: callable(forObj)


def CachingProvider(callable, weak=False):

    def provider(foundIn, forObj):

        fid = id(foundIn)
        utility = provider.cache.get(fid)

        if utility is None:
            utility = provider.cache[fid] = callable(foundIn)

        return utility

    if weak:
        provider.cache = WeakValueDictionary()
    else:
        provider.cache = {}

    return provider



















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

    """Lookup 'name' in global 'InitialContext', relative to 'component'"""

    from peak.naming.api import InitialContext
    
    return InitialContext(component).lookup(name)







def acquireComponent(component, name):

    """Acquire 'name' relative to 'component', w/fallback to globalLookup()"""

    target = component
    
    while target is not None:

        ob = getattr(target, name, NOT_FOUND)

        if ob is not NOT_FOUND:
            return ob

        target = getParentComponent(target)

    else:
        return globalLookup(name, component)
























def findUtilities(component, iface, forObj=None):

    if forObj is None:
        forObj = component
        
    last = component
    
    while component is not None:

        utility = component._getUtility(iface, forObj)

        if utility is not None:
            yield utility

        last      = component
        component = component.getParentComponent()


    cfg = config.getLocal(last)

    if cfg is not None:
        for u in findUtilities(cfg, iface, forObj):
            yield u

    
def findUtility(component, iface, forObj=None):

    for u in findUtilities(component, iface, forObj):
        return u












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

    'name' can be any name acceptable to the 'peak.naming' package, or an
    Interface object.  Strings and 'CompoundName' names will be interpreted
    as paths relative to the starting component.  An empty name will return
    the starting component.  Interfaces will be looked up using
    'findUtility(component,...)'.  All other kinds of names, including URL
    strings and 'CompositeName' instances, will be looked up using
    'binding.globalLookup()'.
    
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
        path segment."""

    if isinstance(name, InterfaceClass):
        utility = findUtility(component, name)
        if utility is None:
            raise NameNotFoundException(name, resolvedObj = component)
        
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

        'someClass' can then refer to 'self.thingINeed' instead of
        calling 'self.lookupComponent("path/to/service")' repeatedly.
    """

    singleValue = True


    def __init__(self,targetName,provides=None,doc=None):

        self.targetNames = (targetName,)
        self._provides=provides
        self.__doc__ = doc or ("binding.bindTo(%r)" % targetName)

    def computeValue(self, obj, instanceDict, attrName):

        names = self.targetNames
        obs   = map(obj.lookupComponent, names)

        for name,newOb in zip(names, obs):

            if newOb is NOT_FOUND:
            
                del instanceDict[attrName]
                raise NameNotFoundError(attrName, resolvedName = name)

            if self.singleValue:            
                return newOb

        return tuple(obs)


class bindSequence(bindTo):

    """Automatically look up and cache a sequence of services by name

        Usage::

            class someClass(binding.AutoCreated):

                thingINeed = binding.bindSequence(
                    "path/to/service", "another/path", ...
                )

        'someClass' can then refer to 'self.thingINeed' to get a tuple of
        services instead of calling 'self.lookupComponent()' on a series of
        names.
    """

    singleValue = False

    def __init__(self, *targetNames, **kw):
        self.targetNames = targetNames
        self._provides = kw.get('provides')
        self.__doc__ = kw.get('doc',("binding.bindSequence%s" % `targetNames`))


















def bindToParent(level=1,provides=None,doc=None):

    """Look up and cache a reference to the nth-level parent component

        Usage::

            class someClass(binding.AutoCreated):

                grandPa = binding.bindToParent(2)

       'someClass' can then refer to 'self.grandPa' instead of calling
       'self.getParentComponent().getParentComponent()'.
    """

    def computeValue(obj, instDict, attrName):

        for step in range(level):
            newObj = obj.getParentComponent()
            if newObj is None: break
            obj = newObj

        return obj

    return Once(computeValue, provides=provides, doc=doc)


def bindToSelf(provides=None, doc=None):

    """Cached reference to the 'self' object

    This is just a shortcut for 'bindToParent(0)', and does pretty much what
    you'd expect.  It's handy for objects that provide default support for
    various interfaces in the absence of an object to delegate to.  The object
    can refer to 'self.delegateForInterfaceX.someMethod()', and have
    'delegateForInterfaceX' be a 'bindToSelf()' by default."""

    return bindToParent(0,provides,doc)




class requireBinding(Once):

    """Placeholder for a binding that should be (re)defined by a subclass"""

    def __init__(self,description="",provides=None,doc=None):
        self.description = description
        self._provides = provides
        self.__doc__ = doc or ("binding.requireBinding: %s" % description)

    def computeValue(self, obj, instanceDict, attrName):
    
        raise NameError("Class %s must define %s; %s"
            % (obj.__class__.__name__, attrName, self.description)
        )


def bindToUtilities(iface, provides=None, doc=None):
    return Once(lambda s,d,a: [u for u in findUtilities(s,iface,s)],
        provides=provides, doc=doc
    )





















class Base(object):

    """Thing that can be composed into a component tree, w/binding & lookups"""

    __metaclasses__  = (
        meta.AssertInterfaces, meta.ActiveDescriptors
    )


    # use the global lookupComponent + getParentComponent functions as methods
    
    lookupComponent = lookupComponent


    def setParentComponent(self,parent):
        self.__parentCell.set(parent)

    def getParentComponent(self):
        return self.__parentCell.get()


    def _getUtility(self, iface, forObj):
        pass


    def __parentCell(s,d,a):
        cell = EigenCell()
        cell.set(None)
        s.getParentComponent = cell.get
        return cell

    __parentCell = Once(__parentCell)


    def hasBinding(self,attr):
        return self.__dict__.has_key(attr)





class Component(Base):

    """An implementation (solution-domain) component"""

    def _componentName(self, dict, name):
        return self.__class__.__name__.split('.')[-1]

    _componentName = Once(_componentName)

    __instance_provides__ = New(EigenRegistry)

    __class_provides__ = EigenRegistry()
    

    def _getUtility(self, iface, forObj):
    
        provider = self.__instance_provides__.get(iface)
            
        if provider is not None:
            return provider(self,forObj)

        attr = self.__class_provides__.get(iface)

        if attr is not None:

            utility = getattr(self,attr)

            if utility is not NOT_FOUND:
                return utility
            

    def registerProvider(self, ifaces, provider):
        self.__instance_provides__.register(ifaces, provider)








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













setupModule()
























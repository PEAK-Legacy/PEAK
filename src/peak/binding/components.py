"""Basic binding tools"""

from __future__ import generators
from peak.api import *

from once import *
from interfaces import *
from weakref import WeakValueDictionary

from peak.naming.names import toName, Syntax, Name
from peak.util.EigenData import EigenRegistry, EigenCell
from peak.config.interfaces import IConfigKey, IPropertyMap
from peak.util.imports import importString


__all__ = [
    'Base', 'Component','AutoCreated', 'TraversableClass', 'AutoCreatable',
    'bindTo', 'requireBinding', 'bindSequence', 'bindToParent', 'bindToSelf',
    'getRootComponent', 'getParentComponent', 'lookupComponent',
    'acquireComponent', 'globalLookup', 'findUtility', 'findUtilities',
    'bindToUtilities', 'bindToProperty', 'iterParents', 'Constant',
    'getComponentName', 'getComponentPath', 'Acquire', 'ComponentName',
]


















def getComponentPath(component, relativeTo=None):

    """Get 'ComponentName' that would traverse from 'relativeTo' to 'component'

    If 'relativeTo' is 'None' or not supplied, the path returned is relative
    to the root component of 'component'.  Note that if supplied, 'relativeTo'
    must be an ancestor (parent, parent's parent, etc.) of 'component'."""

    path = []; root=None

    if relativeTo is None:
        root = getRootComponent(component)

    for c in iterParents(component):

        if c is root:
            path.append(''); break

        elif c is relativeTo:
            break

        path.append(getComponentName(c) or '*')

    path.reverse()
    return ComponentName(path)
















def Constant(provides, value, doc=None):
    """Supply a constant as a property or utility"""
    return Once(lambda s,d,a: value, provides=provides, doc=doc)


def getParentComponent(component):

    """Return parent of 'component', or 'None' if root or non-component"""

    try:
        gpc = component.__class__.getParentComponent
    except AttributeError:
        pass
    else:
        return gpc(component)


def getComponentName(component):

    """Return name of 'component', or 'None' if root or non-component"""

    try:
        gcn = component.__class__.getComponentName
    except AttributeError:
        pass
    else:
        return gcn(component)


def getRootComponent(component):

    """Return the root component of the tree 'component' belongs to"""

    next = component

    while next is not None:
        component = next
        next = getParentComponent(component)

    return component

def globalLookup(name, component=None, targetName=None):

    """Lookup 'name' in global 'InitialContext', relative to 'component'"""

    return naming.lookup(name, component,
        creationParent=component, creationName=targetName
    )







def acquireComponent(name, component=None, targetName=None):

    """Acquire 'name' relative to 'component', w/fallback to globalLookup()"""

    target = component
    
    while target is not None:

        ob = getattr(target, name, NOT_FOUND)

        if ob is not NOT_FOUND:
            return ob

        target = getParentComponent(target)

    else:
        return globalLookup(name, component, targetName)










def iterParents(component=None):

    """Return iterator for all parents of 'component', including config roots
    """

    last = component
        
    for part in "..":

        while component is not None:

            yield component

            last      = component
            component = getParentComponent(component)

        component = config.getLocal(last)


def findUtilities(iface, component=None):

    """Return iterator over all utilities providing 'iface' for 'component'"""

    forObj = component

    for component in iterParents(component):

        try:
            utility = component.__class__._getConfigData
        except AttributeError:
            continue

        utility = utility(component, iface, forObj)

        if utility is not NOT_FOUND:
            yield utility





def findUtility(iface, component=None, default=NOT_GIVEN):

    """Return first utility supporting 'iface' for 'component', or 'default'"""

    for u in findUtilities(iface, component):
        return u

    if default is NOT_GIVEN:
        raise exceptions.NameNotFound(iface, resolvedObj = component)

    return default






























class ComponentName(Name):

    """Path between components

    Component Path Syntax

        Paths are '"/"' separated attribute names.  Path segments of '"."' and
        '".."' mean the same as they do in URLs.  A leading '"/"' (or a
        compound name beginning with an empty path segment), will be treated
        as an "absolute path" relative to the component's root component.

        Paths beginning with anything other than '"/"', '"./"', or '"../"' are
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

    isCompound = 1

    syntax = Syntax(
        direction = 1,
        separator = '/',
    )











def lookupComponent(name, component=None):

    """Lookup 'name' relative to 'component'

    'name' can be any name acceptable to the 'peak.naming' package, or an
    Interface object.  Strings and compound names will be interpreted
    as paths relative to the starting component.  An empty name will return
    the starting component.  Interfaces and Properties will be looked up using
    'findUtility(name, component)'.  All other kinds of names, including URL
    strings and 'CompositeName' instances, will be looked up using
    'binding.globalLookup()'.
    
    Regardless of how the lookup is processed, an 'exceptions.NameNotFound'
    error will be raised if the name cannot be found."""

    return _lookupComponent(component, name)



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










def _lookupComponent(component, name, targetName=None):

    if IConfigKey.isImplementedBy(name):
        return findUtility(name, component)
        
    parsedName = toName(name, ComponentName, 1)

    if not parsedName.isCompound:
        # URL's and composite names must be handled globally
        return globalLookup(name, component, targetName)

    if not parsedName:  # empty name refers to self
        return component

    parts = iter(parsedName)
    attr = parts.next()                 # first part
    pc = _getFirstPathComponent(attr)

    if pc:  ob = pc(component)
    else:   ob = acquireComponent(attr, component, targetName)

    resolved = []
    append = resolved.append

    try:
        for attr in parts:
            pc = _getNextPathComponent(attr)
            if pc:  ob = pc(ob)
            else:   ob = getattr(ob,attr)
            append(attr)

    except AttributeError:

        raise exceptions.NameNotFound(
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
        obs   = [_lookupComponent(obj,n,attrName) for n in names]

        for name,newOb in zip(names, obs):

            if newOb is NOT_FOUND:
            
                del instanceDict[attrName]
                raise exceptions.NameNotFound(attrName, resolvedName = name)

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


def Acquire(key,doc=None):

    if not IConfigKey.isImplementedBy(key):
        raise exceptions.InvalidName("Not a configuration key:", key)

    return bindTo(key,key,doc)










def bindToParent(level=1, name=None, provides=None, doc=None):

    """Look up and cache a reference to the nth-level parent component

        Usage::

            class someClass(binding.AutoCreated):

                grandPa = binding.bindToParent(2)

       'someClass' can then refer to 'self.grandPa' instead of calling
       'self.getParentComponent().getParentComponent()'.
    """

    def computeValue(obj, instDict, attrName):

        for step in range(level):
            newObj = getParentComponent(obj)
            if newObj is None: break
            obj = newObj

        return obj

    return Once(computeValue, name=name, provides=provides, doc=doc)


def bindToSelf(name=None, provides=None, doc=None):

    """Cached reference to the 'self' object

    This is just a shortcut for 'bindToParent(0)', and does pretty much what
    you'd expect.  It's handy for objects that provide default support for
    various interfaces in the absence of an object to delegate to.  The object
    can refer to 'self.delegateForInterfaceX.someMethod()', and have
    'delegateForInterfaceX' be a 'bindToSelf()' by default."""

    return bindToParent(0,name,provides,doc)




class requireBinding(Once):

    """Placeholder for a binding that should be (re)defined by a subclass"""

    def __init__(self,description="",name=None,provides=None,doc=None):
        self.description = description
        self._provides = provides
        self.__doc__ = doc or ("binding.requireBinding: %s" % description)
        self.attrName = self.__name__ = name

    def computeValue(self, obj, instanceDict, attrName):
    
        raise NameError("Class %s must define %s; %s"
            % (obj.__class__.__name__, attrName, self.description)
        )


def bindToUtilities(iface, provides=None, doc=None):

    """Binding to a list of all 'iface' utilities above the component"""

    return Once(lambda s,d,a: list(findUtilities(iface,s)),
        provides=provides, doc=doc
    )


def bindToProperty(propName, default=NOT_GIVEN, provides=None, doc=None):

    """Binding to property 'propName', defaulting to 'default' if not found

        If 'default' is not supplied, failure to locate the named property
        will result in a 'config.PropertyNotFound' exception.
    """

    propName = PropertyName(propName)

    return Once(lambda s,d,a: config.getProperty(propName,s,default),
        provides=provides, doc=doc
    )


class Base(object):

    """Thing that can be composed into a component tree, w/binding & lookups"""

    __class_implements__ = IBindingFactory
    __implements__       = IBindingAPI
    __metaclass__        = ActiveDescriptors

    def __init__(self, parentComponent=None, componentName=None, **kw):
        self.setParentComponent(parentComponent,componentName)
        if kw:
            self.__dict__.update(kw)

    lookupComponent = _lookupComponent

    def setParentComponent(self, parentComponent, componentName=None):
        self.__parentCell.set(parentComponent)
        self.__componentName = componentName

    __componentName = None
    
    def getParentComponent(self):
        return self.__parentCell.get()

    def getComponentName(self):
        return self.__componentName

    def __parentCell(s,d,a):
        cell = EigenCell()
        cell.set(None)
        s.getParentComponent = cell.get
        return cell

    __parentCell = Once(__parentCell)

    def _getConfigData(self, configKey, forObj):
        return NOT_FOUND

    def _hasBinding(self,attr):
        return attr in self.__dict__

    def _getBinding(self,attr,default=None):
        return self.__dict__.get(attr,default)

    def _setBinding(self,attr,value):
        self.__dict__[attr]=value

    def _delBinding(self,attr):
        if attr in self.__dict__:
            del self.__dict__[attr]
































class Component(Base):

    """An configurable implementation (i.e., solution-domain) component"""

    __implements__ = IComponent

    def __instance_provides__(self,d,a):
        from peak.config.config_components import PropertyMap
        pm=PropertyMap()
        pm.setParentComponent(self)
        return pm

    __instance_provides__ = Once(__instance_provides__, provides=IPropertyMap)
    __class_provides__    = EigenRegistry()
    

    def _getConfigData(self, configKey, forObj):
    
        attr = self._getBinding('__instance_provides__')

        if attr:
            value = attr.getValueFor(configKey, forObj)
            
            if value is not NOT_FOUND:
                return value

        attr = self.__class_provides__.get(configKey)

        if attr:
            return getattr(self, attr, NOT_FOUND)

        return NOT_FOUND


    def registerProvider(self, configKeys, provider):
        self.__instance_provides__.registerProvider(configKeys, provider)





class AutoCreatable(OnceClass, ActiveDescriptors):

    """Metaclass for components which auto-create when used"""

    def computeValue(self,owner,_d,_a):
        return self(owner,_a)



class AutoCreated(Component):

    """Component that auto-creates itself in instances of its containing class
    """

    __metaclass__ = AutoCreatable


























class TraversableClass(ActiveDescriptors):

    """Metaclass for classes that can be their own component hierarchy"""

    __class_implements__ = IBindingSPI

    def __parent__(self,d,a):

        parent = self.__module__
        name = self.__name__

        if '.' in name:
            name = '.'.join(name.split('.')[:-1])
            parent = '%s:%s' % (parent,name)

        return importString(parent)
        
    __parent__ = Once(__parent__)


    def __cname__(self,d,a):
        return self.__name__.split('.')[-1]
        
    __cname__ = Once(__cname__)


    def getParentComponent(self):
        return self.__parent__

    def getComponentName(self):
        return self.__cname__        

    def _getConfigData(self, configKey, forObj):
        return NOT_FOUND



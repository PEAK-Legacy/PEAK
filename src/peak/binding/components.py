"""Basic binding tools"""

from __future__ import generators
from once import Once, New, OnceClass
from interfaces import *

import meta

from weakref import WeakValueDictionary

from peak.naming.names import toName, Syntax, CompoundName, PropertyName
from peak.util.EigenData import EigenRegistry, EigenCell

from peak.api import config, NOT_FOUND, NOT_GIVEN, exceptions

from peak.config.interfaces import IConfigKey, IPropertyMap


__all__ = [
    'Base', 'Component','AutoCreated','Provider','CachingProvider',
    'bindTo', 'requireBinding', 'bindSequence', 'bindToParent', 'bindToSelf',
    'getRootComponent', 'getParentComponent', 'lookupComponent',
    'acquireComponent', 'globalLookup', 'findUtility', 'findUtilities',
    'bindToUtilities', 'bindToProperty', 'iterParents', 'Constant',
]
















def Provider(callable):
    return lambda foundIn, configKey, forObj: callable(forObj)


def CachingProvider(callable, weak=False, local=False):

    def provider(foundIn, configKey, forObj):

        if local:

            foundIn = config.getLocal(forObj)

            if foundIn is None:
                foundIn = config.getGlobal()

        else:
            # get the owner of the property map
            foundIn = foundIn.getParentComponent()

        utility = provider.cache.get(foundIn)

        if utility is None:
            utility = provider.cache[foundIn] = callable(foundIn)

        return utility

    if weak:
        provider.cache = WeakValueDictionary()
    else:
        provider.cache = {}

    return provider


def Constant(provides, value, doc=None):
    """Supply a constant as a property or utility"""
    return Once(lambda s,d,a: value, provides=provides, doc=doc)
    



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
    
    return InitialContext(component, creationParent=component).lookup(name)







def acquireComponent(name, component=None):

    """Acquire 'name' relative to 'component', w/fallback to globalLookup()"""

    target = component
    
    while target is not None:

        ob = getattr(target, name, NOT_FOUND)

        if ob is not NOT_FOUND:
            return ob

        target = getParentComponent(target)

    else:
        return globalLookup(name, component)
























def iterParents(component=None):

    last = component
        
    for part in "..":

        while component is not None:

            yield component

            last      = component
            component = component.getParentComponent()

        component = config.getLocal(last)


def findUtilities(iface, component=None):

    forObj = component

    for component in iterParents(component):

        utility = component._getConfigData(iface, forObj)

        if utility is not NOT_FOUND:
            yield utility

    
def findUtility(iface, component=None, default=NOT_GIVEN):

    for u in findUtilities(iface, component):
        return u

    if default is NOT_GIVEN:
        raise exceptions.NameNotFound(iface, resolvedObj = component)

    return default




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



















def lookupComponent(name, component=None):

    """Lookup 'name' relative to 'component'

    'name' can be any name acceptable to the 'peak.naming' package, or an
    Interface object.  Strings and 'CompoundName' names will be interpreted
    as paths relative to the starting component.  An empty name will return
    the starting component.  Interfaces and Properties will be looked up using
    'findUtility(name, component)'.  All other kinds of names, including URL
    strings and 'CompositeName' instances, will be looked up using
    'binding.globalLookup()'.
    
    Regardless of how the lookup is processed, an 'exceptions.NameNotFound'
    error will be raised if the name cannot be found.

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

    return _lookupComponent(component, name)






def _lookupComponent(component, name):

    if IConfigKey.isImplementedBy(name):
        return findUtility(name, component)
        
    parsedName = toName(name, ComponentName, 1)

    if not parsedName.isCompound:
        # URL's and composite names must be handled globally
        return globalLookup(name, component)

    if not parsedName:  # empty name refers to self
        return component

    parts = iter(parsedName)
    attr = parts.next()                 # first part
    pc = _getFirstPathComponent(attr)

    if pc:  ob = pc(component)
    else:   ob = acquireComponent(attr,component)

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
        obs   = map(obj.lookupComponent, names)

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

    """Binding to a list of all 'iface' utilities above the component"""

    return Once(lambda s,d,a: [u for u in findUtilities(iface,s)],
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

    __implements__ = IBindingAPI
    __metaclass__  = meta.ActiveDescriptors

    def __init__(self, parent=None, **kw):
        if kw:
            self.__dict__.update(kw)
        if parent is not None:
            self.setParentComponent(parent)

    lookupComponent = _lookupComponent

    def setParentComponent(self,parent):
        self.__parentCell.set(parent)

    def getParentComponent(self):
        return self.__parentCell.get()


    def _getConfigData(self, configKey, forObj):
        return NOT_FOUND

    def __parentCell(s,d,a):
        cell = EigenCell()
        cell.set(None)
        s.getParentComponent = cell.get
        return cell

    __parentCell = Once(__parentCell)









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

    """An implementation (solution-domain) component"""

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


    def registerProvider(self, ifaces, provider):
        self.__instance_provides__.registerProvider(ifaces, provider)







class AutoCreatable(OnceClass, meta.ActiveDescriptors):

    """Metaclass for components which auto-create when used"""

    def computeValue(self,owner,_d,_a):
        return self(owner)



class AutoCreated(Component):

    """Component that auto-creates itself in instances of its containing class
    """

    __metaclass__ = AutoCreatable



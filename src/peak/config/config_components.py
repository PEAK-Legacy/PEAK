from __future__ import generators

from peak.api import *
from peak.util.imports import importString, importObject, whenImported
from peak.binding.components import Component, Make, getParentComponent
from peak.binding.interfaces import IAttachable, IRecipe
from peak.util.EigenData import EigenCell,AlreadyRead
from peak.util.FileParsing import AbstractConfigParser

from interfaces import *
from protocols.advice import getMRO, determineMetaclass

__all__ = [
    'PropertyMap', 'LazyRule', 'PropertySet', 'fileNearModule',
    'iterParents','findUtilities','findUtility', 'ProviderOf', 'FactoryFor',
    'provideInstance', 'instancePerComponent', 'Namespace',
    'CreateViaFactory'
]


def _setCellInDict(d,key,value):

    cell = d.get(key)

    if cell is None:
        cell = d[key] = EigenCell()

    cell.set(value)

_emptyRuleCell = EigenCell()
_emptyRuleCell.set(lambda *args: NOT_FOUND)
_emptyRuleCell.exists()


def fileNearModule(moduleName,filename):
    filebase = importString(moduleName+':__file__')
    import os; return os.path.join(os.path.dirname(filebase), filename)




def iterParents(component):

    """Iterate over all parents of 'component'"""

    last = component

    while component is not None:

        yield component

        component = getParentComponent(component)


def findUtilities(component, iface):

    """Return iterator over all utilities providing 'iface' for 'component'"""

    forObj = component
    iface = adapt(iface,IConfigKey)

    for component in iterParents(component):

        try:
            utility = component._getConfigData
        except AttributeError:
            continue

        utility = utility(forObj, iface)

        if utility is not NOT_FOUND:
            yield utility

    adapt(
        component,IConfigurationRoot,NullConfigRoot
    ).noMoreUtilities(component, iface, forObj)






def findUtility(component, iface, default=NOT_GIVEN):

    """Return first utility supporting 'iface' for 'component', or 'default'"""

    for u in findUtilities(component, iface):
        return u

    if default is NOT_GIVEN:
        raise exceptions.NameNotFound(iface, resolvedObj = component)

    return default






























class ProviderOf(object):

    """Configuration key based on interface+class(es)"""

    protocols.advise(
        instancesProvide=[IConfigKey]
    )

    __slots__ = 'keys', 'mro'

    def __init__(self, iface, klass, *others):
        bases = (klass,)+others
        if others:
            meta = determineMetaclass(bases)
            klass = meta("Dummy",bases,{})
            mro = list(getMRO(klass))[1:]
        else:
            mro = getMRO(klass)

        iface = adapt(iface,IConfigKey)

        self.keys = tuple(
            [((i,base),d)
                for base in bases
                    for (i,d) in iface.registrationKeys()
            ]
        )

        self.mro  = tuple(
            [(i,klass) for klass in mro for i in iface.lookupKeys()]
        )

    def registrationKeys(self,depth=0):
        return self.keys

    def lookupKeys(self):
        return self.mro




class FactoryFor(ProviderOf):

    """Config key for an 'IComponentFactory' that returns 'iface' objects"""

    __slots__ = ()


    def __init__(self, iface):

        iface = adapt(iface,IConfigKey)

        self.keys = tuple(
            [((FactoryFor,i),d) for (i,d) in iface.registrationKeys()]
        )

        self.mro  = tuple(
            [(FactoryFor,i) for i in iface.lookupKeys()]
        )























class CreateViaFactory(object):

    """'IRule' for one-time creation of target interface using FactoryFor()"""

    protocols.advise(
        classProvides=[IRule]
    )

    __slots__ = 'iface','instance'


    def __init__(self,iface):
        self.iface = iface


    def __call__(self, propertyMap, configKey, targetObj):

        try:
            return self.instance

        except AttributeError:

            factory = findUtility(targetObj, FactoryFor(self.iface))

            if factory is NOT_FOUND:
                self.instance = factory
            else:
                self.instance = factory()
                binding.suggestParentComponent(
                    binding.getParentComponent(propertyMap),None,self.instance
                )

            return self.instance








class PropertyMap(Component):

    rules = Make(dict)
    depth = Make(dict)

    protocols.advise(
        instancesProvide=[IPropertyMap]
    )

    def setRule(self, propName, ruleObj):
        _setCellInDict(self.rules, PropertyName(propName), ruleObj)

    def setDefault(self, propName, defaultRule):
        _setCellInDict(self.rules, PropertyName(propName+'?'), defaultRule)

    def setValue(self, propName, value):
        _setCellInDict(self.rules, PropertyName(propName), lambda *args: value)


    def registerProvider(self, configKey, provider):

        """Register 'provider' under 'configKey'"""

        for key,depth in adapt(configKey, IConfigKey).registrationKeys():

            if self.depth.get(key,depth)>=depth:
                # The new provider is at least as good as the one we have
                _setCellInDict(self.rules, key, provider)
                self.depth[key]=depth












    def getValueFor(self, forObj, configKey):

        rules      = self._getBinding('rules')
        value      = NOT_FOUND

        if not rules:
            return value

        xRules     = []

        for name in configKey.lookupKeys():

            rule = rules.get(name)

            if rule is None:
                xRules.append(name)     # track unspecified rules

            elif rule is not _emptyRuleCell:

                value = rule.get()(self, configKey, forObj)

                if value is not NOT_FOUND:
                    break

        # ensure that unspecified rules stay that way, if they
        # haven't been replaced in the meanwhile by a higher-level
        # wildcard rule

        for name in xRules:
            rules.setdefault(name,_emptyRuleCell)

        return value

    _getConfigData = getValueFor







class LazyRule(object):

    loadNeeded = True

    def __init__(self, loadFunc, prefix='*', **kw):
        self.load = loadFunc
        self.prefix = prefix
        self.__dict__.update(kw)


    def __call__(self, propertyMap, propName, targetObj):

        if self.loadNeeded:

            try:
                self.loadNeeded = False
                return self.load(propertyMap, self.prefix, propName)

            except:
                del self.loadNeeded
                raise

        return NOT_FOUND


















from peak.naming.interfaces import IState

class NamingStateAsSmartProperty(protocols.Adapter):

    protocols.advise(
        instancesProvide = [ISmartProperty],
        asAdapterForProtocols = [IState],
    )

    def computeProperty(self, propertyMap, name, prefix, suffix, targetObject):

        from peak.naming.factories.config_ctx import PropertyPath
        from peak.naming.factories.config_ctx import PropertyContext

        ctx = PropertyContext(targetObject,
            creationParent = targetObject,
            nameInContext = PropertyPath(prefix[:-1]), # strip any trailing '.'
        )

        result = self.subject.restore(ctx, PropertyPath(suffix))

        rule = adapt(result, ISmartProperty, None)
        if rule is not None:
            result = rule.computeProperty(
                propertyMap, name, prefix, suffix, targetObject
            )

        return result













class ConfigurationRoot(Component):
    """Default implementation for a configuration root.

    If you think you want to subclass this, you're probably wrong.  Note that
    you can have whatever setup code you want, called automatically from .ini
    files loaded by this class.  We recommend you try that approach first."""

    protocols.advise(instancesProvide=[IConfigurationRoot])

    def __instance_offers__(self,d,a):
        pm = d[a] = PropertyMap(self)
        self.setupDefaults(pm)
        return pm

    __instance_offers__ = Make(__instance_offers__,
        offerAs=[IPropertyMap], uponAssembly = True
    )

    iniFiles = ( ('peak','peak.ini'), )

    def setupDefaults(self, propertyMap):
        """Set up 'propertyMap' with default contents loaded from 'iniFiles'"""

        for file in self.iniFiles:
            if isinstance(file,tuple):
                file = fileNearModule(*file)
            config.loadConfigFile(propertyMap, file)

    def propertyNotFound(self,root,propertyName,forObj,default=NOT_GIVEN):
        if default is NOT_GIVEN:
            raise exceptions.PropertyNotFound(propertyName, forObj)
        return default

    def noMoreUtilities(self,root,configKey,forObj): pass

    def nameNotFound(self,root,name,forObj):
        return naming.lookup(forObj, name, creationParent=forObj)




class Namespace(object):
    """Traverse to another property namespace

    Use this in .ini files (e.g. '__main__.* = config.Namespace("environ.*")')
    to create a rule that looks up undefined properties in another property
    namespace.

    Or, use this as a way to treat a property namespace as a mapping object::

        myNS = config.Namespace("some.prefix", aComponent)
        myNS['spam.bayes']              # property 'some.prefix.spam.bayes'
        myNS.get('something',default)   # property 'some.prefix.something'

    Or use this in a component class to allow traversing to a property space::

        class MyClass(binding.Component):

            appConfig = binding.Make(
                config.Namespace('MyClass.conf')
            )

            something = binding.Obtain('appConfig/foo.bar.baz')

    In the example above, 'something' will be the component's value for the
    property 'MyClass.conf.foo.bar.baz'.  Note that you may not traverse to
    names beginning with an '_', and traversing to the name 'get' will give you
    the namespace's 'get' method, not the 'get' property in the namespace.  To
    obtain the 'get' property, or properties beginning with '_', you must use
    the mapping style of access, as shown above."""

    def __init__(self, prefix, target=NOT_GIVEN, cacheAttrs=True):
        self._prefix = PropertyName(prefix).asPrefix()
        self._target = target
        self._cache = cacheAttrs

    def __call__(self, suffix):
        """Return a sub-namespace for 'suffix'"""
        return self.__class__(
            PropertyName.fromString(self._prefix+suffix),self._target
        )

    def __getattr__(self, attr):
        if not attr.startswith('_'):
            ob = self.get(attr, NOT_FOUND)
            if ob is not NOT_FOUND:
                if self._cache:
                    setattr(self,attr,ob)   # Cache for future use
                return ob
        raise AttributeError,attr

    def __getitem__(self, key):
        """Return the value of property 'key' within this namespace"""
        ob = self.get(key,NOT_FOUND)
        if ob is not NOT_FOUND:
            return ob
        raise KeyError,key

    def get(self,key,default=None):
        """Return property 'key' within this namespace, or 'default'"""
        if self._target is not NOT_GIVEN:
            return config.getProperty(
                self._target,PropertyName.fromString(self._prefix+key),default
            )
        return default

    def __repr__(self):
        return "config.Namespace(%r,%r)" % (self._prefix,self._target)















class __NamespaceExtensions(protocols.Adapter):

    protocols.advise(
        instancesProvide = [ISmartProperty, IAttachable, IRecipe],
        asAdapterForTypes = [Namespace]
    )

    def computeProperty(self, propertyMap, name, prefix, suffix, targetObject):
        return config.getProperty(
            propertyMap, self.subject._prefix+suffix, default=NOT_FOUND
        )

    def setParentComponent(self, parentComponent, componentName=None,
        suggest=False
    ):

        pc = self.subject._target

        if pc is NOT_GIVEN:
            self.subject._target = parentComponent
            return

        elif suggest:
            return

        raise AlreadyRead(
            "%r already has target %r; tried to set %r"
                % (self.subject,pc,parentComponent)
        )


    def __call__(self,client,instDict,attrName):
        subject = self.subject
        return subject.__class__(subject._prefix[:-1], client, subject._cache)







class PropertySet(object):

    """DEPRECATED"""

    def __init__(self, targetObj, prefix):
        self.prefix = PropertyName(prefix).asPrefix()
        self.target = targetObj

    def __getitem__(self, key, default=NOT_GIVEN):
        return config.getProperty(self.target,self.prefix+key,default)

    def get(self, key, default=None):
        return config.getProperty(self.target,self.prefix+key,default)

    def __getattr__(self,attr):
        return self.__class__(self.target, self.prefix+attr)

    def of(self, target):
        return self.__class__(target, self.prefix[:-1])

    def __call__(self, default=None, forObj=NOT_GIVEN):

        if forObj is NOT_GIVEN:
            forObj = self.target

        return config.getProperty(forObj, self.prefix[:-1], default)















def instancePerComponent(factorySpec):
    """Use this to provide a utility instance for each component"""
    return lambda foundIn, configKey, forObj: importObject(factorySpec)(forObj)


def provideInstance(factorySpec):
    """DEPRECATED, use 'CreateViaFactory(key)' instead"""
    _ob = []
    def rule(foundIn, configKey, forObj):
        if not _ob:
            _ob.append(importObject(factorySpec)(
                binding.getParentComponent(foundIn))
            )
        return _ob[0]
    return rule



























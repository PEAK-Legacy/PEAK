from __future__ import generators

from peak.api import *
from peak.util.imports import importString, importObject
from peak.binding.components import Component, New, Once, getParentComponent

from peak.util.EigenData import EigenCell
from peak.util.FileParsing import AbstractConfigParser

from interfaces import *
from protocols import Interface


__all__ = [
    'PropertyMap', 'LazyRule', 'ConfigReader', 'loadConfigFiles',
    'loadConfigFile', 'loadMapping', 'PropertySet', 'fileNearModule',
    'iterParents','findUtilities','findUtility',
    'provideInstance', 'instancePerComponent',
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






























class PropertyMap(Component):

    rules = New(dict)
    depth = New(dict)

    protocols.advise(
        instancesProvide=[IPropertyMap]
    )

    def setRule(self, propName, ruleObj):
        _setCellInDict(self.rules, PropertyName(propName), ruleObj)

    def setDefault(self, propName, defaultRule):
        _setCellInDict(self.rules, PropertyName(propName+'?'), defaultRule)

    def setValue(self, propName, value):
        _setCellInDict(self.rules, PropertyName(propName), lambda *args: value)


    def registerProvider(self, configKey, provider, depth=0):
        """Register 'provider' under 'configKey'"""

        if self.depth.get(configKey,depth)>=depth:
            # The registered provider is at least as good as the one we have
            _setCellInDict(self.rules, configKey, provider)
            self.depth[configKey]=depth
            for i in configKey.getBases():
                self.registerProvider(i, provider, depth+1)













    def getValueFor(self, forObj, configKey):

        rules      = self._getBinding('rules')
        value      = NOT_FOUND

        if not rules:
            return value

        xRules     = []

        if isinstance(configKey,PropertyName):
            lookups = configKey.matchPatterns()
        else:
            lookups = configKey,


        for name in lookups:

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


















def _value(v):
    return lambda *x: v


def loadMapping(pMap, mapping, prefix='*', includedFrom=None):

    prefix = PropertyName(prefix).asPrefix()

    for k,v in mapping.items():
        pMap.registerProvider(PropertyName(prefix+k), _value(v))

protocols.adviseObject(loadMapping, provides=[ISettingLoader])


def loadConfigFile(pMap, filename, prefix='*', includedFrom=None):

    if filename:
        ConfigReader(pMap,prefix).readFile(filename)

protocols.adviseObject(loadConfigFile, provides=[ISettingLoader])


def loadConfigFiles(pMap, filenames, prefix='*', includedFrom=None):

    if not filenames:
        return

    import os.path

    for filename in filenames:
        if filename and os.path.exists(filename):
            ConfigReader(pMap,prefix).readFile(filename)

protocols.adviseObject(loadConfigFiles, provides=[ISettingLoader])







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













class ConfigReader(AbstractConfigParser):

    def __init__(self, propertyMap, prefix='*'):
        self.pMap = propertyMap
        self.prefix = PropertyName(prefix).asPrefix()


    def add_setting(self, section, name, value, lineInfo):

        _ruleName = PropertyName(section+name)
        _rulePrefix = _ruleName.asPrefix()
        _lrp = len(_rulePrefix)

        def f(propertyMap, propertyName, targetObj):
            ruleName = _ruleName
            rulePrefix = _rulePrefix
            ruleSuffix = propertyName[_lrp:]
            result = eval(value)
            rule = adapt(result,ISmartProperty,None)
            if rule is not None:
                result = rule.computeProperty(
                    propertyMap, propertyName, rulePrefix, ruleSuffix,
                    targetObj
                )
            return result

        self.pMap.registerProvider(_ruleName,f)


    def do_include(self, section, name, value, lineInfo):
        from api_impl import getProperty
        propertyMap = self.pMap
        loader = getProperty(propertyMap, "peak.config.loaders."+name)
        loader = importObject(loader)
        eval("loader(propertyMap,%s,includedFrom=self)" % value)


    def provide_utility(self, section, name, value, lineInfo):
        self.pMap.registerProvider(importString(name), eval(value))


    def on_demand(self, section, name, value, lineInfo):
        self.pMap.registerProvider(
            PropertyName(name),
            LazyRule(
                lambda propertyMap, ruleName, propertyName: eval(value),
                prefix = name
            )
        )


    section_handlers = {
        'load settings from': 'do_include',
        'provide utilities':  'provide_utility',
        'load on demand':     'on_demand',
    }


    def add_section(self, section, lines, lineInfo):

        if section is None:
            section='*'

        s = ' '.join(section.strip().lower().split())

        if ' ' in s:
            handler = self.section_handlers.get(s)

            if handler:
                handler = getattr(self,handler)
            else:
                raise SyntaxError("Invalid section type", section, lineInfo)

        else:
            section = self.prefix + PropertyName(section).asPrefix()
            handler = self.add_setting

        self.process_settings(section, lines, handler)




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

    __instance_offers__ = Once(__instance_offers__,
        offerAs=[IPropertyMap], activateUponAssembly = True
    )

    iniFiles = ( ('peak','peak.ini'), )

    def setupDefaults(self, propertyMap):
        """Set up 'propertyMap' with default contents loaded from 'iniFiles'"""

        for file in self.iniFiles:
            if isinstance(file,tuple):
                file = fileNearModule(*file)
            loadConfigFile(propertyMap, file)

    def propertyNotFound(self,root,propertyName,forObj,default=NOT_GIVEN):
        if default is NOT_GIVEN:
            raise exceptions.PropertyNotFound(propertyName, forObj)
        return default

    def noMoreUtilities(self,root,configKey,forObj): pass

    def nameNotFound(self,root,name,forObj):
        return naming.lookup(forObj, name, creationParent=forObj)




class PropertySet(object):

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
    """Use this to provide a single utility instance for all components"""
    _ob = []
    def rule(foundIn, configKey, forObj):
        if not _ob:
            _ob.append(importObject(factorySpec)(
                binding.getParentComponent(foundIn))
            )
        return _ob[0]
    return rule



























from peak.api import *
from peak.util.imports import importString, importObject, whenImported
from peak.util.FileParsing import AbstractConfigParser
from interfaces import *
from config_components import FactoryFor, CreateViaFactory, LazyRule

__all__ = [
    'ConfigReader', 'loadConfigFiles', 'loadConfigFile', 'loadMapping',
    'ruleForExpr',
]


SECTION_PARSERS = PropertyName('peak.config.iniFile.sectionParsers')
CONFIG_LOADERS  = PropertyName('peak.config.loaders')


def ruleForExpr(name,expr,globalDict):
    """Return 'config.IRule' for property 'name' based on 'expr' string"""

    _ruleName = PropertyName(name)
    _rulePrefix = _ruleName.asPrefix()
    _lrp = len(_rulePrefix)

    def f(propertyMap, configKey, targetObj):
        ruleName = _ruleName
        rulePrefix = _rulePrefix
        if isinstance(configKey,PropertyName):
            propertyName = configKey
            ruleSuffix = propertyName[_lrp:]
        result = eval(expr,globalDict,locals())
        rule = adapt(result,ISmartProperty,None)
        if rule is not None:
            result = rule.computeProperty(
                propertyMap, propertyName, rulePrefix, ruleSuffix,
                targetObj
            )
        return result

    protocols.adviseObject(f,provides=[IRule])
    return f

def loadMapping(pMap, mapping, prefix='*', includedFrom=None):

    prefix = PropertyName(prefix).asPrefix()

    for k,v in mapping.items():
        pMap.setValue(PropertyName.fromString(prefix+k), v)

protocols.adviseObject(loadMapping, provides=[ISettingLoader])


def loadConfigFile(pMap, filename, prefix='*', includedFrom=None):
    globalDict = getattr(includedFrom,'gloablDict',None)
    if filename:
        ConfigReader(pMap,prefix,globalDict).readFile(filename)

protocols.adviseObject(loadConfigFile, provides=[ISettingLoader])


def loadConfigFiles(pMap, filenames, prefix='*', includedFrom=None):

    if not filenames:
        return

    import os.path

    globalDict = getattr(includedFrom,'gloablDict',None)

    for filename in filenames:
        if filename and os.path.exists(filename):
            ConfigReader(pMap,prefix,globalDict).readFile(filename)

protocols.adviseObject(loadConfigFiles, provides=[ISettingLoader])









class ConfigReader(AbstractConfigParser):

    protocols.advise(
        instancesProvide=[IIniParser]
    )

    def __init__(self, propertyMap, prefix='*', globalDict=None):
        self.pMap = propertyMap
        self.prefix = PropertyName(prefix).asPrefix()
        if globalDict is None:
            globalDict = globals()
        self.globalDict = globalDict.copy()

    def add_setting(self, section, name, value, lineInfo):
        _ruleName = PropertyName(section+name)

        self.pMap.registerProvider(
            _ruleName,
            ruleForExpr(_ruleName,value,self.globalDict)
        )

    def add_section(self, section, lines, lineInfo):

        if section is None:
            section='*'

        section = section.strip()
        s = ' '.join(section.lower().split())

        if ' ' in s:
            pn = PropertyName.fromString(s.replace(' ','.'))
            func = importObject(SECTION_PARSERS.of(self.pMap).get(pn))
            if func is None:
                raise SyntaxError(("Invalid section type", section, lineInfo))
            handler = lambda *args: func(self, *args)
        else:
            section = self.prefix + PropertyName(section).asPrefix()
            handler = self.add_setting

        self.process_settings(section, lines, handler)

def do_include(parser, section, name, value, lineInfo):
    propertyMap = parser.pMap
    loader = importObject(CONFIG_LOADERS.of(propertyMap)[name])
    eval("loader(propertyMap,%s,includedFrom=parser)" % value,parser.globalDict,locals())

def provide_utility(parser, section, name, value, lineInfo):    # DEPRECATED!
    module = '.'.join(name.replace(':','.').split('.')[:-1])
    pMap = parser.pMap
    globalDict = parser.globalDict
    whenImported(
        module,
        lambda x: pMap.registerProvider(
            importString(name), eval(value,globalDict,locals())
        )
    )

def register_factory(parser, section, name, value, lineInfo):
    module = '.'.join(name.replace(':','.').split('.')[:-1])
    pMap = parser.pMap
    globalDict = parser.globalDict
    def onImport(module):
        iface = importString(name)
        pMap.registerProvider(
            FactoryFor(iface),
            ruleForExpr(name,"importObject(%s)" % value, globalDict)
        )
        pMap.registerProvider(iface, CreateViaFactory(iface))

    whenImported(module, onImport)

def on_demand(parser, section, name, value, lineInfo):
    globalDict = parser.globalDict
    parser.pMap.registerProvider(
        PropertyName(name),
        LazyRule(
            lambda propertyMap, ruleName, propertyName: eval(value,globalDict,locals()),
            prefix = name
        )
    )



"""The PEAK API

 Your first step to using PEAK in a module will almost always be::

    from peak.api import *

 This will put you only one or two attribute accesses away from most of the
 functions, classes, and constants you need to use PEAK.

 At the present time, this will import the 'api' submodules of the 'binding',
 'naming', 'config', 'storage', 'model', and 'running' packages, each under
 the corresponding name, using a lazy import.  Thus, 'from peak.api import
 binding' will get you a lazyImport of the 'peak.binding.api' module.  This
 allows you to get quick, easy access to most of the PEAK API, without complex
 import patterns, but also without a lot of namespace pollution.  In addition
 to the 'api' modules, the 'peak.running.logs' module is also available as
 'logs', and 'peak.exceptions' is available as 'exceptions'.

 In addition to the lazily-imported modules, 'peak.api' also exports
 the following objects for convenience in interacting with PEAK's APIs:
 
    'NOT_GIVEN' and 'NOT_FOUND' -- Singleton values used for convenience
        in dealing with non-existent parameters or dictionary/cache entries

    'Items()' -- a convenience function that produces a 'dict.items()'-style
        list from a mapping and/or keyword arguments.

    'LOG_*()' -- shortcut functions to call logs.LogEvent().publish() with a
        preset priority, e.g. 'LOG_NOTICE("message",component)'
"""

from __future__ import generators

__all__ = [
    'NOT_GIVEN', 'NOT_FOUND', 'Items', 'PropertyName',
    'binding', 'naming', 'model', 'config', 'running', 'logs', 'storage',
    'exceptions',
    'LOG_CRITICAL', 'LOG_ERROR', 'LOG_WARNING', 'LOG_NOTICE', 'LOG_INFO',
    'LOG_DEBUG', 'LOG',
]

from peak.util.imports import lazyModule

binding     = lazyModule('peak.binding.api')
config      = lazyModule('peak.config.api')
exceptions  = lazyModule('peak.exceptions')
model       = lazyModule('peak.model.api')
naming      = lazyModule('peak.naming.api')
running     = lazyModule('peak.running.api')
storage     = lazyModule('peak.storage.api')
logs        = lazyModule('peak.running.logs')


# Logging shortcuts

def LOG_CRITICAL(message, parent=None, **info):
    logs.Event(message,parent,priority=logs.PRI_CRITICAL,**info).publish()

def LOG_ERROR(message, parent=None, **info):
    logs.Event(message,parent,priority=logs.PRI_ERROR,**info).publish()

def LOG_WARNING(message, parent=None, **info):
    logs.Event(message,parent,priority=logs.PRI_WARNING,**info).publish()

def LOG_NOTICE(message, parent=None, **info):
    logs.Event(message,parent,priority=logs.PRI_NOTICE,**info).publish()

def LOG_INFO(message, parent=None, **info):
    logs.Event(message,parent,priority=logs.PRI_INFO,**info).publish()

def LOG_DEBUG(message, parent=None, **info):
    logs.Event(message,parent,priority=logs.PRI_DEBUG,**info).publish()

def LOG(message, parent=None, **info):
    logs.Event(message,parent,**info).publish()







# Convenience features

class _Symbol(object):

    """Symbolic global constant"""

    __slots__ = ['_name', '_module']
    __name__   = property(lambda s: s._name)
    __module__ = property(lambda s: s._module)

    def __init__(self, symbol, moduleName):
        self.__class__._name.__set__(self,symbol)
        self.__class__._module.__set__(self,moduleName)

    def __reduce__(self):
        return self._name

    def __setattr__(self,attr,val):
        raise TypeError("Symbols are immutable")

    def __repr__(self):
        return self.__name__

    __str__ = __repr__


# XXX we need to wrap these in security proxies if zope.security present

NOT_GIVEN = _Symbol("NOT_GIVEN", __name__)
NOT_FOUND = _Symbol("NOT_FOUND", __name__)











def Items(mapping=None, **kwargs):

    """Convert 'mapping' and/or 'kwargs' into a list of '(key,val)' items

        Key/value item lists are often easier or more efficient to manipulate
        than mapping objects, so PEAK API's will often use such lists as
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










import re
pnameValidChars = re.compile( r"([-+*?!:._a-z0-9]+)", re.I ).match

class PropertyName(str):

    """Name of a configuration property, usable as a configuration key"""

    def __new__(klass, *args):

        self = super(PropertyName,klass).__new__(klass,*args)

        valid = pnameValidChars(self)

        if not valid or valid.end()<len(self):
            raise exceptions.InvalidName(
                "Invalid characters in property name", self
            )

        parts = self.split('.')

        if '' in parts or not parts:
            raise exceptions.InvalidName(
                "Empty part in property name", self
            )

        if '*' in self:
            if '*' not in parts or parts.index('*') < (len(parts)-1):
                raise exceptions.InvalidName(
                    "'*' must be last part of wildcard property name", self
                )
            
        if '?' in self:
            if '?' in parts or self.index('?') < (len(self)-1):
                    raise exceptions.InvalidName(
                        "'?' must be at end of a non-empty part", self
                    )

        return self



    def isWildcard(self):
        return self.endswith('*')

    def isDefault(self):
        return self.endswith('?')

    def isPlain(self):
        return self[-1:] not in '?*'


    def matchPatterns(self):

        if self.isWildcard():
            raise exceptions.InvalidName(
                "Can't match patterns against wildcard names", self
            )

        yield self

        if self.isDefault():
            return

        name = self
        
        while '.' in name:
            name = name[:name.rindex('.')]
            yield name+'.*'

        yield '*'
        yield self
        yield self+'?'


    def getBases(self):
        return ()


    def extends(self, other, strict=1):
        return not strict and self==other


    def asPrefix(self):

        p = self

        if not self.isPlain():
            p=p[:-1]

        if p and not p.endswith('.'):
            p=p+'.'

        return p


    def __call__(self, forObj=None, default=NOT_GIVEN):
        from peak.config.api import getProperty
        return getProperty(forObj, self, default)


    def of(self, forObj):
        from peak.config.config_components import PropertySet
        return PropertySet(forObj, self)






















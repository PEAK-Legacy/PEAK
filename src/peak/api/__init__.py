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
 
    'NOT_GIVEN' and 'NOT_FOUND' -- Singleton false values used for convenience
        in dealing with non-existent parameters or dictionary/cache entries

    'Items()' -- a convenience function that produces a 'dict.items()'-style
        list from a mapping and/or keyword arguments.

    'LOG_*()' -- shortcut functions to call logs.LogEvent().publish() with a
        preset priority, e.g. 'LOG_NOTICE("message",component)'
"""

__all__ = [
    'NOT_GIVEN', 'NOT_FOUND', 'Items',
    'binding', 'naming', 'model', 'config', 'running', 'logs', 'storage',
    'exceptions',
    'LOG_CRITICAL', 'LOG_ERROR', 'LOG_WARNING', 'LOG_NOTICE', 'LOG_INFO',
    'LOG_DEBUG', 'LOG',
]



from peak.util.imports import lazyImport

binding = lazyImport('peak.binding.api')
naming  = lazyImport('peak.naming.api')
model   = lazyImport('peak.model.api')
config  = lazyImport('peak.config.api')
running = lazyImport('peak.running.api')
storage = lazyImport('peak.storage.api')
exceptions = lazyImport('peak.exceptions')
logs    = lazyImport('peak.running.logs')


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

NOT_GIVEN = object()
NOT_FOUND = object()


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






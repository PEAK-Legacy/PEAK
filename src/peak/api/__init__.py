"""The PEAK API

 Your first step to using PEAK in a module will almost always be::

    from peak.api import *

 This will put you only one or two attribute accesses away from most of the
 functions, classes, and constants you need to use PEAK.

 At the present time, this will import the following API modules:

    'binding' -- a lazy import of the 'peak.binding.api' module

    'naming' -- a lazy import of the 'peak.naming.api' module

    'model' -- a lazy import of the 'peak.model.api' module

    'config' -- a lazy import of the 'peak.running.config.api' module

 and the following objects for convenience in interacting with PEAK:
 
    'NOT_GIVEN' and 'NOT_FOUND' -- Singleton false values used for convenience
        in dealing with non-existent parameters or dictionary/cache entries

    'Items()' -- a convenience function that produces a 'dict.items()'-style
        list from a mapping and/or keyword arguments.
"""

__all__ = [
    'NOT_GIVEN', 'NOT_FOUND', 'Items',
    'binding', 'naming', 'model', 'config', 'running',
]

from peak.binding.imports import lazyImport

binding = lazyImport('peak.binding.api')
naming  = lazyImport('peak.naming.api')
model   = lazyImport('peak.model.api')
config  = lazyImport('peak.running.config.api')
running = lazyImport('peak.running.api')

# Convenience features

NOT_GIVEN = []
NOT_FOUND = []


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






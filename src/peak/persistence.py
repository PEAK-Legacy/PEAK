__all__ = [
    'Persistent', 'PersistentMetaClass', 'isGhost'
]

# Ugh; this is the one place where relative imports are annoying:
# when you can't turn them off!

from peak.util.imports import importString

import __main__
md = __main__.__dict__

Persistent             = importString('persistence:Persistent', md)
PersistentMetaClass    = importString('persistence:PersistentMetaClass', md)
GHOST                  = importString('persistence._persistence:GHOST', md)
IPersistentDataManager = importString('persistence.interfaces:IPersistentDataManager', md)

def isGhost(obj):
    return obj._p_state == GHOST


# XX It's not clear that we should be using GHOST
# XXX do we need simple_new()?  What is it for, anyway?




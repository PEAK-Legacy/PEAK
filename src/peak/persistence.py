from Persistence import Persistent, PersistentMetaClass
from Persistence.cPersistence import GHOST  # UPTODATE, CHANGED, STICKY,
from Persistence.IPersistentDataManager import IPersistentDataManager

__all__ = [
    'Persistent', 'PersistentMetaClass', 'isGhost'
]


def isGhost(obj):
    return obj._p_state == GHOST


# XX It's not clear that we should be using GHOST
# XXX do we need simple_new()?  What is it for, anyway?




##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""Python implementation of persistent container type

$Id: PersistentDict.py,v 1.1 2002/08/05 20:11:56 pje Exp $
"""

import Persistence
from UserDict import UserDict

__metaclass__ = type

class PersistentDict(Persistence.Persistent, UserDict):
    """A persistent wrapper for mapping objects.

    This class allows wrapping of mapping objects so that object
    changes are registered.  As a side effect, mapping objects may be
    subclassed.
    """

    # UserDict provides all of the mapping behavior.  The
    # PersistentDict class is responsible marking the persistent
    # state as changed when a method actually changes the state.  At
    # the mapping API evolves, we may need to add more methods here.

    __super_delitem = UserDict.__delitem__
    __super_setitem = UserDict.__setitem__
    __super_clear = UserDict.clear
    __super_update = UserDict.update
    __super_setdefault = UserDict.setdefault
    __super_popitem = UserDict.popitem

    __super_p_init = Persistence.Persistent.__init__
    __super_init = UserDict.__init__

    def __init__(self, dict=None):
        self.__super_init(dict)
        self.__super_p_init()

    def __delitem__(self, key):
        self.__super_delitem(key)
        self._p_changed = True

    def __setitem__(self, key, v):
        self.__super_setitem(key, v)
        self._p_changed = True

    def clear(self):
        self.__super_clear()
        self._p_changed = True

    def update(self, b):
        self.__super_update(b)
        self._p_changed = True

    def setdefault(self, key, failobj=None):
        # We could inline all of UserDict's implementation into the
        # method here, but I'd rather not depend at all on the
        # implementation in UserDict (simple as it is).
        if not self.has_key(key):
            self._p_changed = True
        return self.__super_setdefault(key, failobj)

    def popitem(self):
        self._p_changed = True
        return self.__super_popitem()

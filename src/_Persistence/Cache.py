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
from time import time
from sys import getrefcount
from weakref import ref

class Cache(object):

    __iter=None

    def __init__(self, size=500, inactive=300):
        self.__ghosts = {}
        self.__gget = self.__ghosts.get
        self.__active = {}
        self.__aget = self.__active.get
        self._size = size
        self._inactive = 300

    def __getitem__(self, oid):
        o = self.__gget(oid, self)
        if o is self:
            o = self.__active[oid]
        o=o()
        if o is None:
            raise KeyError, oid
        else:
            return o

    def get(self, oid, default=None):
        o = self.__gget(oid, self)
        if o is self:
            o = self.__active.get(oid, self)
            if o is self: return default
        o=o()
        if o is None:
            return default
        else:
            return o

    def __setitem__(self, oid, object):
        if object._p_changed is None:
            # ghost
            self.__ghosts[oid] = ref(object, _dictdel(oid, self.__ghosts))
        else:
            self.__active[oid] = ref(object, _dictdel(oid, self.__active))

    def __delitem__(self, oid):
        # XXX is there any way to know which dict the key is in?
        try:
            del self.__ghosts[oid]
        except KeyError:
            pass
        try:
            del self.__active[oid]
        except KeyError:
            pass

    def __len__(self):
        return len(self.__ghosts)+len(self.__active)

    def setstate(self, oid, object):
        try:
            del self.__ghosts[oid]
        except KeyError:
            pass
        self.__active[oid] = ref(object, _dictdel(oid, self.__active))

    def incrgc(self, multiple=1):
        na=len(self.__active)
        if na < 1: return

        # how many objects do we scan?
        n=min(multiple * max((na-self._size)/10, 3), na)
        
        # how long can objects be inactive?
        inactive = self._inactive * (
            0.2 + 0.1 * (min(100, 8 * self._size/na))
            )

        active=self.__active
        aget=active.get
        ghosts=self.__ghosts
        doomed=[]

        now=int(time()%86400)

        i=self.__iter
        if i is None:
            i=iter(self.__active)

        while n:
            n-=1
            try: oid = i.next()
            except StopIteration:
                del self.__iter
                return

            ob=aget(oid, self)
            if ob is self: continue
            ob=ob()
            state = ob._p_changed
            
            if state==0 and abs(ob._p_atime-now) > inactive:
                doomed.append(oid)
                continue
            if state is None:
                doomed.append(oid)

        for oid in doomed:
            ob=aget(oid, self)
            if ob is self: continue
            ob=ob()
            ob._p_deactivate()
            state = ob._p_changed
            if state is None:
                del active[oid]
                ghosts[oid] = ref(ob, _dictdel(oid, ghosts))

    def full_sweep(self):
        now=int(time()%86400)
        active=self.__active
        ghosts=self.__ghosts
        na=len(active)
        
        # how long can objects be inactive?
        inactive = self._inactive * (
            0.2 + 0.1 * (min(100, 8 * self._size/na))
            )

        doomed=[]

        for oid in active:
            ob=active[oid]
            ob=ob()
            state = ob._p_changed
            if state==0 and abs(ob._p_atime-now) > inactive:
                doomed.append(oid)
                continue
            if state is None:
                doomed.append(oid)

        for oid in doomed:
            ob._p_deactivate()
            state = ob._p_changed
            if state is None:
                del active[oid]
                ghosts[oid] = ref(ob, _dictdel(oid, ghosts))

    def minimize(self):
        active=self.__active
        aget=active.get
        ghosts=self.__ghosts

        # Grump: I cant use an iterator because the size will change
        # during iteration. :(
        for oid in active.keys():
            ob=aget(oid, self)
            if ob is self: continue
            ob=ob()
            ob._p_deactivate()
            if ob._p_changed is None:
                del active[oid]
                ghosts[oid] = ref(ob, _dictdel(oid, ghosts))
        self.__iter=None

    def invalidate(self, oid):
        ob = self.__aget(oid)
        if ob is None:
            return
        ob = ob()
        del ob._p_changed
        del self.__active[oid]
        self.__ghosts[oid] = ref(ob, _dictdel(oid, self.__ghosts))

    def invalidateMany(self, oids):
        if oids is None:
            oids = self.__active.keys()
        for oid in oids:
            self.invalidate(oid)

    def clear(self):
        for oid in self.__active.keys():
            self.invalidate(oid)

    def statistics(self):
        return {
            'ghosts': len(self.__ghosts),
            'active': len(self.__active),
            }
        
class _dictdel(object):

    __slots__ = 'oid', 'dict'

    def __init__(self, oid, dict):
        self.oid, self.dict = oid, dict
        
    def __call__(self, *args):
        del self.dict[self.oid]

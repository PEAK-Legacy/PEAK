##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Persistent Classes."""

from Persistence import Persistent, PersistentMetaClass
from Persistence.cPersistence import UPTODATE, CHANGED, STICKY, GHOST
from Persistence.IPersistent import IPersistent
from Persistence.Function import PersistentFunction

import new
from types import FunctionType as function
import time

# XXX There is a lot of magic here to give classes and instances
# separate sets of attributes.  This code should be documented, as it
# it quite delicate, and it should be move to a separate module.

class ExtClassDescr(object):
    """Maintains seperate class and instance descriptors for an attribute.

    This allows a class to provide methods and attributes without
    intefering with normal use of instances.  The class and its
    instances can each have methods with the same name.

    This does interfere with introspection on the class.
    """

    def __init__(self, name, instdescr):
        self.name = name
        self.instdescr = instdescr

    def __get__(self, obj, cls):
        if obj is None:
            return self.clsget(cls)
        else:
            return self.instdescr.__get__(obj, cls)

    def __set__(self, obj, val):
        if obj is None:
            self.clsset(val)
        else:
            if self.instdescr is None:
                raise AttributeError, self.name
            return self.instdescr.__set__(obj, val)

    def __delete__(self, obj):
        if self.instdescr is None:
            raise AttributeError, self.name
        return self.instdescr.__delete__(obj)

    # subclass should override

    def clsget(self, cls):
        pass

    def clsset(self, val):
        pass

    def clsdelete(self):
        pass

class MethodMixin(object):

    def __init__(self, name, descr, func):
        super(MethodMixin, self).__init__(name, descr)
        self.func = func

    def clsget(self, cls):
        def f(*args, **kwargs):
            try:
                return self.func(cls, *args, **kwargs)
            except TypeError:
                print `self.func`, `cls`, `args`, `kwargs`
                raise
        return f

class DataMixin(object):

    def __init__(self, name, descr, val):
        super(DataMixin, self).__init__(name, descr)
        self.val = val

    def clsget(self, cls):
        return self.val

    def clsset(self, val):
        self.val = val

    def clsdelete(self):
        del self.val

class ExtClassObject(object):

    _missing = object()
    
    def __init__(self, name, instdescr):
        self.name = name
        self.instdescr = instdescr

    def __get__(self, obj, cls):
        if obj is None:
            return self.clsget(cls)
        else:
            return self.instdescr.__get__(obj, cls)

    def __set__(self, obj, cls):
        if obj is None:
            return self.clsset(cls)
        else:
            if self.instdescr is None:
                raise AttributeError, self.name
            return self.instdescr.__set__(obj, cls)

    def __delete__(self, obj, cls):
        if obj is None:
            return self.clsdelete(cls)
        else:
            if self.instdescr is None:
                raise AttributeError, self.name
            return self.instdescr.__delete__(obj, cls)

class ExtClassMethodDescr(MethodMixin, ExtClassDescr):
    pass

class ExtClassDataDescr(DataMixin, ExtClassDescr):
    pass

# XXX is missing necessary for findattr?
# None might be sufficient
_missing = object()

def findattr(cls, attr, default):
    """Walk the mro of cls to find attr."""
    for c in cls.__mro__:
        o = c.__dict__.get(attr, _missing)
        if o is not _missing:
            return o
    return default

class PersistentClassMetaClass(PersistentMetaClass):

    # an attempt to make persistent classes look just like other
    # persistent objects by providing class attributes and methods
    # that behave like the persistence machinery.

    # the chief limitation of this approach is that class.attr won't
    # always behave the way it does for normal classes

    __implements__ = IPersistent
    
    _pc_init = 0

    def __new__(meta, name, bases, dict):
        cls = super(PersistentClassMetaClass, meta).__new__(meta, name, bases, dict)
        # helper functions
        def extend_attr(attr, v):
            prev = findattr(cls, attr, None)
            setattr(cls, attr, ExtClassDataDescr(attr, prev, v))

        def extend_meth(attr, m):
            prev = findattr(cls, attr, None)
            setattr(cls, attr, ExtClassMethodDescr(attr, prev, m))

        extend_attr("_p_oid", None)
        extend_attr("_p_jar", None)
        extend_meth("_p_activate", meta._p_activate)
        extend_meth("_p_deactivate", meta._p_activate)
        extend_meth("__getstate__", meta.__getstate__)
        extend_meth("__setstate__", meta.__setstate__)
        extend_attr("__implements__", meta.__implements__)
        
        cls._pc_init = 1
        return cls

    def fixup(cls, mod):
        for k, v in cls.__dict__.items():
            if isinstance(v, function):
                setattr(cls, k, PersistentFunction(v, mod))

    def __getattribute__(cls, name):
        if (name[0] == "_" and
            not (name.startswith("_p_") or name.startswith("_pc_") or
                 name == "__dict__")):
            if cls._p_state is None:
                cls._p_activate()
                cls._p_atime = int(time.time() % 86400)
        return super(PersistentClassMetaClass, cls).__getattribute__(name)

    def __setattr__(cls, attr, val):
        if not attr.startswith("_pc_") and cls._pc_init:
            descr = cls.__dict__.get(attr)
            if descr is not None:
                set = getattr(descr, "__set__", None)
                if set is not None:
                    set(None, val)
                    return
        super(PersistentClassMetaClass, cls).__setattr__(attr, val)

    def __delattr__(cls, attr):
        if attr.startswith('_p_'):
            if attr == "_p_changed":
                # this means something special
                pass
            else:
                return
        super(PersistentClassMetaClass, cls).__delattr__(attr)
    
    def __getstate__(cls):
        dict = {}
        for k, v in cls.__dict__.items():
            if hasattr(v, '_p_oid'):
                dict[k] = v
        return dict

    def __setstate__(cls, dict):
        for k, v in dict.items():
            setattr(cls, k, v)

    def _p_deactivate(cls):
        # do nothing but mark the state change for now
        cls._p_state = GHOST

    def _p_activate(cls):
        if cls._p_state is None:
            dm = cls._p_jar
            if dm is not None:
                # reactivate
                cls._p_state = UPTODATE

    # Methods below here are not wrapped to be class-only attributes.
    # They are available as methods of classes using this metaclass.

    def __getnewargs__(cls):
        return cls.__name__, cls.__bases__, {}

class PersistentBaseClass(Persistent):

    __metaclass__ = PersistentClassMetaClass

def _test():
    global PC, P

    class PC(Persistent):

        __metaclass__ = PersistentClassMetaClass

        def __init__(self):
            self.x = 1

        def inc(self):
            self.x += 1

        def __int__(self):
            return self.x

    class P(PersistentBaseClass):

        def __init__(self):
            self.x = 1

        def inc(self):
            self.x += 1

        def __int__(self):
            return self.x

if __name__ == "__main__":
    _test()


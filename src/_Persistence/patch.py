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
"""Patch references to auto-persistent objects in a module.

Implementation notes:

What semantics do we want for update-in-place in the presence of aliases?

Semantics based on per-namespace updates don't work in the presence of
aliases.  If an update changes an alias, then the old binding will be
updated with the state of the new binding.

Semantics based on containing namespaces seem to work.  The outermost
namespace that contains a name is updated in place.  Aliases are
simple rebinding operations that do not update in place.

The containment approach seems to have a problem with bound methods,
where an instance can stash a copy of a bound method created via an
alias.  When the class is updated, the alias changes, but the bound
method isn't.  Then the bound method can invoke an old method on a new
object, which may not be legal.  It might sufficient to outlaw this case.
"""

__metaclass__ = type

from cStringIO import StringIO
import pickle
from types import *

from Persistence.Class import PersistentClassMetaClass

class FunctionWrapper:

    def __init__(self, func, module):
        self._func = func
        self._module = module
        self._p_oid = id(func)

    def __call__(self, defaults, dict):
        self._func.func_defaults = defaults
        self._func.func_dict.update(dict)
        return PersistentFunction(self._func, self._module)

class TypeWrapper:

    def __init__(self, atype, module):
        self._type = atype
        self._module = module

    def __call__(self, bases, dict):
        return PersistentClassMetaClass(self._type.__name__, bases, dict)

class Pickler(pickle.Pickler):

    dispatch = {}
    dispatch.update(pickle.Pickler.dispatch)

    def __init__(self, file, module, memo):
        pickle.Pickler.__init__(self, file, bin=True)
        self._pmemo = memo
        self._module = module

    def persistent_id(self, object):
        if hasattr(object, "_p_oid"):
            oid = id(object)
            self._pmemo[oid] = object
            return oid
        else:
            return None

    def save_type(self, atype):
        self.save_reduce(TypeWrapper(atype, self._module),
                         (atype.__bases__, atype.__dict__))
    
    dispatch[TypeType] = save_type

    def save_function(self, func):
        self.save_reduce(FunctionWrapper(func, self._module),
                         (func.func_defaults, func.func_dict))

    dispatch[FunctionType] = save_function

class Unpickler(pickle.Unpickler):

    def __init__(self, file, pmemo):
        pickle.Unpickler.__init__(self, file)
        self._pmemo = pmemo

    def persistent_load(self, oid):
        return self._pmemo[oid]

def fixup(new, old):
    pass

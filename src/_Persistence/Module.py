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
"""Persistent Module."""

__metaclass__ = type

import __builtin__
# in 2.3, this will be spelled new.function
from types import FunctionType as function
import sys

from Persistence import Persistent
from Persistence.cPersistence import GHOST
from Persistence.Class import PersistentClassMetaClass
from Persistence.Function import PersistentFunction
from Persistence.IPersistentModuleManager import IPersistentModuleManager
from Persistence.IPersistentModuleRegistry \
     import IPersistentModuleImportRegistry, IPersistentModuleUpdateRegistry 

from Transaction import get_transaction

# builtins are explicitly assigned when a module is unpickled
import __builtin__

# Modules aren't picklable by default, but we'd like them to be
# pickled just like classes (by name).
import copy_reg

def _pickle_module(mod):
    return mod.__name__

def _unpickle_module(modname):
    mod = __import__(modname)
    if "." in modname:
        parts = modname.split(".")[1:]
        for part in parts:
            mod = getattr(mod, part)
    return mod

copy_reg.pickle(type(copy_reg), _pickle_module, _unpickle_module)

# XXX Is this comment still relevant?
#
# There seems to be something seriously wrong with a module pickle
# that contains objects pickled via save_global().  These objects are
# pickled using references to the module.  It appears that unpickling the
# object in the module causes the persistence machinery to fail.
#
# My suspicion is that the assignment to po_state before trying to
# load the state confuses things.  The first call to setstate attempts
# to reference an attribute of the module.  That getattr() fails because
# the module is not a ghost, but does have any empty dict.  Since
# that getattr() fails, its state can't be unpickled.
#
# Not sure what to do about this.

class PersistentModule(Persistent):

    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.__name__)

    # XXX need getattr &c. hooks to update _p_changed?
    # XXX what about code that modifies __dict__ directly?
    # XXX one example is a function that rebinds a global

    def __getstate__(self):
        d = self.__dict__.copy()
        try:
            del d["__builtins__"]
        except KeyError:
            pass
        return d

    def __setstate__(self, state):
        state["__builtins__"] = __builtin__
        self.__dict__.update(state)

class PersistentPackage(PersistentModule):
    # XXX Is it okay that these packages don't have __path__?

    # A PersistentPackage can exist in a registry without a manager.
    # It only gets a manager if someone creates an __init__ module for
    # the package.

    def __init__(self, name):
        self.__name__ = name

__persistent_module_registry__ = "__persistent_module_registry__"

class PersistentModuleManager(Persistent):

    __implements__ = IPersistentModuleManager

    def __init__(self, registry):
        self._registry = registry
        self._module = None
        self.name = None
        self.source = None

    def new(self, name, source):
        if self._module is not None:
            raise ValueError, "module already exists"
        if "." in name:
            parent = self._new_package(name)
        else:
            parent = None
            self._module = PersistentModule(name)
        try:
            self._registry.setModule(name, self._module)
        except ValueError, err:
            self._module = None
            raise
        self.name = name
        self.update(source)
        if parent is not None:
            modname = name.split(".")[-1]
            setattr(parent, modname, self._module)

    def update(self, source):
        self._module._p_changed = True
        moddict = self._module.__dict__
        copy = moddict.copy()
        moddict[__persistent_module_registry__] = self._registry
        exec source in moddict
        del moddict[__persistent_module_registry__]
        self._fixup(moddict, copy, self._module)
        self.source = source

    def remove(self, source):
        self._registry.delModule(self._module.__name__)
        self._module = None
    
    def _fixup(self, new, old, module):
        # Update persistent objects in place, and
        # convert new functions to persistent functions
        # XXX should convert classes, too

        for k, v in new.items():
            if isinstance(v, function):
                v = new[k] = PersistentFunction(v, module)
            elif isinstance(v.__class__, PersistentClassMetaClass):
                v.__class__.fixup(module)
            # XXX need to check for classes that are not persistent!

            old_v = old.get(k)
            if old_v is not None:
                # XXX the type test below works for functions, but may
                # not work for classes or other objects
                if (isinstance(old_v, Persistent)
                    and type(old_v) == type(v)):
                    state = v.__getstate__()
                    old_v.__setstate__(state)
                    new[k] = old_v

    def _new_package(self, name):
        parent = self._get_parent(name)
        modname = name.split(".")[-1]
        if modname == "__init__":
            self._module = parent
            return None
        else:
            self._module = PersistentModule(name)
            return parent

    def _get_parent(self, name):
        # If a module is being created in a package, automatically
        # create parent packages that do no already exist.
        parts = name.split(".")[:-1]
        parent = None
        for i in range(len(parts)):
            if parts[i] == "__init__":
                raise ValueError, "__init__ can not be a package"
            pname = ".".join(parts[:i+1])
            package = self._registry.findModule(pname)
            if package is None:
                package = PersistentPackage(pname)
                self._registry.setModule(pname, package)
                if parent is not None:
                    setattr(parent, parts[i], package)
            elif not isinstance(package, PersistentPackage):
                raise ValueError, "%s is module" % pname
            parent = package
        return parent

class PersistentModuleImporter:
    """An import hook that loads persistent modules.

    The importer cooperates with other objects to make sure imports of
    persistent modules work correctly.  The default importer depends
    on finding a persistent module registry in the globals passed to
    __import__().  It looks for the name __persistent_module_registry__.
    A PersistentModuleManager places its registry in the globals used
    to exec module source.

    It is important that the registry be activated before it is used
    to handle imports.  If a ghost registry is used for importing, a
    circular import occurs.  The second import occurs when the
    machinery searches for the class of the registry.  It will re-use
    the registry and fail, because the registry will be marked as
    changed but not yet have its stated loaded.  XXX There ought to be
    a way to deal with this.
    """

    def __init__(self):
        self._saved_import = None

    def install(self):
        self._saved_import = __builtin__.__import__
        __builtin__.__import__ = self.__import__

    def uninstall(self):
        __builtin__.__import__ = self._saved_import

    def _import(self, registry, name, parent, fromlist):
        mod = None
        if parent is not None:
            fullname = "%s.%s" % (parent, name)
            mod = registry.findModule(fullname)
            if mod is None:
                parent = None
        if mod is None: # no parent or didn't find in parent
            mod = registry.findModule(name)
        if mod is None:
            return None
        if fromlist:
            if isinstance(mod, PersistentPackage):
                self._import_fromlist(registry, mod, fromlist)
            return mod
        else:
            i = name.find(".")
            if i == -1:
                return mod
            name = name[:i]
            if parent:
                name = "%s.%s" % (parent, name)
            top = registry.findModule(name)
            assert top is not None, "No package for module %s" % name
            return top

    def _import_fromlist(self, registry, mod, fromlist):
        for name in fromlist:
            if not hasattr(mod, name):
                fullname = "%s.%s" % (mod.__name__, name)
                self._import(registry, fullname, None, [])

    def __import__(self, name, globals={}, locals={}, fromlist=[]):
        registry = globals.get(__persistent_module_registry__)
        if registry is not None:
            mod = self._import(registry, name, self._get_parent(globals),
                               fromlist)
            if mod is not None:
                return mod
        return self._saved_import(name, globals, locals, fromlist)

    def _get_parent(self, globals):
        name = globals.get("__name__")
        if name is None or "." not in name:
            return None
        i = name.rfind(".")
        return name[:i]

class PersistentModuleRegistry(Persistent):

    __implements__ = (IPersistentModuleImportRegistry,
                      IPersistentModuleUpdateRegistry)

    def __init__(self):
        self.__modules = {}

    def findModule(self, name):
        assert self._p_state != GHOST
        return self.__modules.get(name)
    
    def setModule(self, name, module):
        if name in self.__modules:
            raise ValueError, name
        self._p_changed = True
        self.__modules[name] = module

    def delModule(self, name):
        self._p_changed = True
        del self.__modules[name]

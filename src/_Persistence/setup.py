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
from distutils.core import setup, Extension

# A hack to determine if Extension objects support the depends keyword arg.
if not "depends" in Extension.__init__.func_code.co_varnames:
    # If it doesn't, create a local replacement that removes depends
    # from the kwargs before calling the regular constructor.
    _Extension = Extension
    class Extension(_Extension):
        def __init__(self, name, sources, **kwargs):
            if "depends" in kwargs:
                del kwargs["depends"]
            _Extension.__init__(self, name, sources, **kwargs)

base_btrees_depends = [
    "setup.py",
    "BTrees/BTreeItemsTemplate.c",
    "BTrees/BTreeModuleTemplate.c",
    "BTrees/BTreeTemplate.c",
    "BTrees/BucketTemplate.c",
    "BTrees/MergeTemplate.c",
    "BTrees/SetOpTemplate.c",
    "BTrees/SetTemplate.c",
    "BTrees/TreeSetTemplate.c",
    "BTrees/sorters.c",
    ]

oob = Extension(name = "BTrees._OOBTree",
                include_dirs = ["."],
                sources = ['BTrees/_OOBTree.c'],
                depends = (base_btrees_depends +
                           ["BTrees/objectkeymacros.h",
                            "BTrees/objectvaluemacros.h"])
                )

oib = Extension(name = "BTrees._OIBTree",
                include_dirs = ["."],
                sources = ['BTrees/_OIBTree.c'],
                depends = (base_btrees_depends +
                           ["BTrees/objectkeymacros.h",
                            "BTrees/intvaluemacros.h"])
                )

iib = Extension(name = "BTrees._IIBTree",
                include_dirs = ["."],
                sources = ['BTrees/_IIBTree.c'],
                define_macros = [('EXCLUDE_INTSET_SUPPORT', None)],
                depends = (base_btrees_depends +
                           ["BTrees/intkeymacros.h",
                            "BTrees/intvaluemacros.h"])
                )

iob = Extension(name = "BTrees._IOBTree",
                include_dirs = ["."],
                sources = ['BTrees/_IOBTree.c'],
                define_macros = [('EXCLUDE_INTSET_SUPPORT', None)],
                depends = (base_btrees_depends +
                           ["BTrees/intkeymacros.h",
                            "BTrees/objectvaluemacros.h"])
                )

fsb = Extension(name = "BTrees._fsBTree",
                include_dirs = ["."],
                sources = ['BTrees/_fsBTree.c'],
                define_macros = [('EXCLUDE_INTSET_SUPPORT', None)],
                depends = base_btrees_depends
                )

setup(
    name="Persistence",
    version="XXX",
    ext_modules=[Extension("cPersistence", ["cPersistence.c"]),
                 oob, oib, iib, iob, fsb]
    )

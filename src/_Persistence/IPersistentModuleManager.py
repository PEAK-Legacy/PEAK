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
try:
    from Interface import Interface
    from Interface.Attribute import Attribute
except ImportError:
    class Interface:
        pass
    def Attribute(x):
        return x

class IPersistentModuleManager(Interface):

    def new(name, source):
        """Create and register a new named module from source."""

    def update(src):
        """Update the source of the existing module."""

    def remove():
        """Unregister the module and forget about it."""

    name = Attribute("Absolute module name")
    source = Attribute("Module source string")

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
except ImportError:
    class Interface:
        pass

class IPersistentModuleImportRegistry(Interface):

    def findModule(name):
        """Return module registered under name or None."""

class IPersistentModuleUpdateRegistry(IPersistentModuleImportRegistry):

    def setModule(name, module):
        """Register module under name.

        Raises ValueError if module is already registered.
        """

    def delModule(name):
        """Unregister module registered under name.

        Raises KeyError in module is not registered.
        """


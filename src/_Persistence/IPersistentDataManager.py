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
try:
    from Interface import Interface
except ImportError:
    class Interface: pass

class IPersistentDataManager(Interface):
    """Provide services for managing persistent state.

    This interface is provided by ZODB Connections.

    This interface is used by persistent objects.
    """

    def setstate(object):
        """Load the state for the given object.

        The object should be in the deactivated (ghost) state.
        The object's state will be set and the object will end up
        in the up-to-date state.

        The object must implement the IPersistent interface.
        """

    def register(object):
        """Register a IPersistent with the current transaction.

        This method provides some insulation of the persistent object
        from details of transaction management. For example, it allows
        the use of per-database-connection rather than per-thread
        transaction managers.
        """

    def mtime(object):
        """Return the modification time of the object.

        The modification time may not be known, in which case None
        is returned.
        """

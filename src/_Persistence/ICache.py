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

class ICache(Interface):
    """In-memory object cache

    Cache objects are used by data managers to implement in-memory
    object caches with automatic object deactivation and removal of
    unreferenced objects.

    Cache objects depend heavily on the Persistent object C API.
    """

    def __getitem__(key):
        """Get a cached object
        """

    def __setitem__(key, value):
        """Add an object to the cache
        """

    def __len__():
        """Return the number of objects in the cache
        """

    def get(oid, default=None):
        """Get a cached object
        """

    def incrgc(multiple=1):
        """Perform incremental garbage collection

        An positive integer argument can be provided to speify a
        number of incremental steps to take.
        """

    def full_sweep():
        """Perform a full sweep of the cache
        """

    def minimize():
        """Remove as many objects as possible from the cache
        """

    def invalidate(oids):
        """Invalidate the object for the given object ids
        """

    def invalidateMany(oids):
        """Invalidate the objects for the given colection of object ids

        If oids is None, all of the objets in the cache are
        invalidated.

        The collection must be iterable as if it was a sequence of oids.
        """

class ICachePolicy(Interface):

    def maximum_quiet(cache_size):
        """Return a number of seconds

        Objects that haven't been accessed in the last number seconds
        should be deactivated.
        """

    def incremental_check_count(cache_size):
        """Return the number of objects that should be checked in an
        incremental garbage collection.
        """

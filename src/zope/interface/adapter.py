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
"""Adapter-style interface registry

See Adapter class.

$Id: adapter.py,v 1.1 2003/01/20 20:02:52 pje Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.interface._flatten import _flatten
from zope.interface.interfaces import IAdapterRegistry

class AdapterRegistry:
    """Adapter-style interface registry
    """

    __implements__ = IAdapterRegistry

    # The implementation uses a mapping:
    #
    #  { (required_interface, provided_interface) ->
    #                             (registered_provides, component) }
    #
    # Where the registered provides is what was registered and
    # provided may be some base interface

    def __init__(self, data=None):
        if data is None:
            data = {}
        self._reg = data

    def _registerAllProvided(self, require, primary_provide, object, provide):
        # Registers a component using (require, provide) as a key.
        # Also registers superinterfaces of the provided interface,
        # stopping when the registry already has a component
        # that provides a more general interface or when the Base is Interface.

        reg = self._reg
        reg[(require, provide)] = (primary_provide, object)
        bases = getattr(provide, '__bases__', ())
        for base in bases:
            if base is Interface:
                # Never register the say-nothing Interface.
                continue
            existing = reg.get((require, base), None)
            if existing is not None:
                existing_provide = existing[0]
                if existing_provide is not primary_provide:
                    if not existing_provide.extends(primary_provide):
                        continue
                    # else we are registering a general component
                    # after a more specific component.
            self._registerAllProvided(require, primary_provide, object, base)


    def register(self, require, provide, object):
        if require is not None and not IInterface.isImplementedBy(require):
            raise TypeError(
                "The require argument must be an interface (or None)")
        if not IInterface.isImplementedBy(provide):
            raise TypeError(
                "The provide argument must be an interface (or None)")

        # Invalidate our cache
        self._v_cache = {}

        self._registerAllProvided(require, provide, object, provide)

    def get(self, ob_interface_provide, default=None, filter=None):
        """
        Finds a registered component that provides the given interface.
        Returns None if not found.
        """

        if filter is None:
            cache = getattr(self, '_v_cache', self)
            if cache is self:
                cache = self._v_cache = {}
            key = `ob_interface_provide`
            cached = cache.get(key, self)
            if cached is self:
                cached = self._uncached_get(ob_interface_provide,
                                            default, filter)
                cache[key] = cached
            return cached

        return self._uncached_get(ob_interface_provide,
                                  default, filter)

    def _uncached_get(self, (ob_interface, provide), default, filter):
        
        for interface in _flatten(ob_interface, 1):
            c = self._reg.get((interface, provide))
            if c:
                c = c[1]
                if filter is None:
                    return c
                if filter(c):
                    return c

        return default

    def getForObject(self, object, interface, filter=None):
        return self.get((getattr(object, '__implements__', None), interface),
                        filter=filter)

    def getRegistered(self, require, provide):
        data = self._reg.get((require, provide))
        if data:
            registered_provide, object = data
            if registered_provide == provide:
                return object
        return None

    def getRegisteredMatching(self,
                              required_interfaces=None,
                              provided_interfaces=None):


        if IInterface.isImplementedBy(required_interfaces):
            required_interfaces = (required_interfaces, )

        if provided_interfaces:

            if IInterface.isImplementedBy(provided_interfaces):
                provided_interfaces = (provided_interfaces, )

            r = {}

            if required_interfaces:
                # Both specified
                for required in _flatten(required_interfaces, 1):
                    for provided in provided_interfaces:
                        v = self._reg.get((required, provided))
                        if v:
                            rprovided, o = v
                            r[required, rprovided] = o


            else:
                # Only provided specified
                for (required, provided), (rprovided, o) in self._reg.items():
                    for p in provided_interfaces:
                        if provided.extends(p, 0):
                            r[required, rprovided] = o
                            break

            return [(required, provided, o)
                    for ((required, provided), o) in r.items()]


        elif required_interfaces:
            # Just required specified
            required_interfaces = _flatten(required_interfaces, 1)
            return [(required, provided, o)
                    for (required, provided), (rprovided, o)
                    in self._reg.items()
                    if ((required in required_interfaces)
                        and
                        provided == rprovided
                        )
                   ]

        else:
            # Nothing specified
            return [(required, provided, o)
                    for (required, provided), (rprovided, o)
                    in self._reg.items()
                    if provided == rprovided
                   ]

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

$Id: _flatten.py,v 1.1 2003/02/03 15:54:25 pje Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.interface import Interface

def _flatten(implements, include_None=0):
    """Flatten an implements spec to a list of interfaces

    The list includes all base interfaces of the interface(s) in
    implements. Each interface is listed only once and more
    specific interfaces are listed before less specific
    interfaces. This is similar to Python 2.2's MRO.
    """
    interfaces = []
    _flatten_recurse(implements, interfaces)
    interfaces.reverse()
    seen = {}
    flattened = []
    for interface in interfaces:
        if interface not in seen:
            seen[interface] = 1
            flattened.append(interface)
    flattened.reverse()

    if include_None and None not in flattened:
        flattened.append(None)

    return flattened

def _flatten_recurse(implements, list):
    if implements.__class__ == tuple:
        for i in implements:
            _flatten_recurse(i, list)
    else:
        _flatten_recurse_interface(implements, list)

def _flatten_recurse_interface(interface, list):
    list.append(interface)
    if interface is None:
        return
    for i in interface.__bases__:
        _flatten_recurse_interface(i, list)

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
"""Implemantation assertion facilities.

Revision information:
$Id: implements.py,v 1.1 2003/04/10 15:43:16 pje Exp $
"""

from zope.interface import exceptions
from zope.interface.verify import verifyClass
from zope.interface.interface import InterfaceClass
from types import TupleType, ClassType, StringType

# Special value indicating the object supports
# what its class supports.
CLASS_INTERFACES = 1

ClassTypes = ClassType, type

_typeImplements = {}

def getImplements(object):
    # Decide whether or not the object is a class.  If it is a class,
    # return it's __class_implements__ rather than its __implements__.
    if isinstance(object, ClassTypes):
        ci = getattr(object, '__class_implements__', None)
        if ci is not None:
            return ci
    else:
        impl = getattr(object, '__implements__', None)
        if impl is not None:
            return impl

    return _typeImplements.get(type(object))


def getImplementsOfInstances(klass):
    if isinstance(klass, ClassTypes):
        return getattr(klass, '__implements__', None)
    else:
        return _typeImplements.get(klass)


def visitImplements(implements, object, visitor, getInterface=None):
    """Call visitor for each interace.

    Visits the interfaces described by an __implements__ attribute,
    invoking the visitor for each interface object.
    If the visitor returns anything true, the loop stops.
    This does not, and should not, visit superinterfaces.
    """
    # this allows us to work with proxy wrappers in Python 2.2,
    # yet remain compatible with earlier versions of python.
    implements_class = getattr(implements, '__class__', None)

    if InterfaceClass in implements_class.__mro__:
        return visitor(implements)
    elif implements == CLASS_INTERFACES:
        klass = getattr(object, '__class__', None)
        if klass is not None:
            i = getImplementsOfInstances(klass)
            if i:
                return visitImplements(i, object, visitor, getInterface)
    elif implements_class == StringType or type(implements) is StringType:
        if getInterface is not None:
            # Look up a named interface.
            i = getInterface(object, implements)
            if i is not None:
                return visitImplements(i, object, visitor, getInterface)
    elif implements_class == TupleType or type(implements) is TupleType:
        for i in implements:
            r = visitImplements(i, object, visitor, getInterface)
            if r:
                # If the visitor returns anything true, stop.
                return r
    else:
        if implements_class is not None and \
           type(implements) != implements_class:
            raise exceptions.BadImplements(
                """__implements__ should be an interface or tuple,
                not a %s pretending to be a %s"""
                % (type(implements).__name__, implements_class.__name__)
                )
        raise exceptions.BadImplements(
            """__implements__ should be an interface or tuple,
            not a %s""" % type(implements).__name__)
    return None


def assertTypeImplements(type, interfaces):
    """Assign a set of interfaces to a Python type such as int, str, tuple,
       list and dict.
    """
    _typeImplements[type] = interfaces

def objectImplements(object, getInterface=None):
    r = []
    implements = getImplements(object)
    if not implements:
        return r
    visitImplements(implements, object, r.append, getInterface)
    return r

def instancesOfObjectImplements(klass, getInterface=None):
    r = []
    implements = getImplementsOfInstances(klass)
    if not implements:
        return r
    visitImplements(implements, klass, r.append, getInterface)
    return r

def _flatten(i, append):
    if isinstance(i, (list, tuple)):
        for iface in i:
            _flatten(iface, append)
    else:
        append(i)
        bases = i.getBases()
        if bases:
            for b in bases:
                _flatten(b, append)

def flattenInterfaces(interfaces, remove_duplicates=1):
    res = []
    _flatten(interfaces, res.append)
    if remove_duplicates:
        # Remove duplicates in reverse.
        # Similar to Python 2.2's method resolution order.
        seen = {}
        index = len(res) - 1
        while index >= 0:
            i = res[index]
            if i in seen:
                del res[index]
            else:
                seen[i] = 1
            index = index - 1
    return res

def implements(klass, interface, check=1):
    if check:
        verifyClass(interface, klass, tentative=1)

    old = getattr(klass, '__implements__', None)
    if old is None:
        klass.__implements__ = interface
    else:
        klass.__implements__ = old, interface

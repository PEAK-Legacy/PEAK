"""Encapsulate use of Zope's 'Interface' package"""

from zope.interface import Interface, Attribute
from zope.interface.implements import implements as addDeclarationToType

__all__ = [
    'Interface', 'Attribute', 'adapt', 'implements', 'classProvides'
]

# We don't want to export 'addDeclarationToType' by default; we only use it
# in 'peak.config.interfaces' right now, and that should go away eventually.


# Monkeypatch 'Interface' to support the '__adapt__' side of the protocol
# This is slower than just having the object check, but more
# backward-compatible.

def __adapt__(self, obj):
    if self.isImplementedBy(obj):
        return obj

Interface.__class__.__adapt__ = __adapt__


_marker = object()
from sys import _getframe, exc_info

from types import ClassType
ClassTypes = ClassType, type

from peak.util.advice import addClassAdvisor










def adapt(obj, protocol, default=_marker):

    """PEP 246-alike: Adapt 'obj' to 'protocol', return 'default'

    If 'default' is not supplied and no implementation is found,
    raises 'TypeError'."""

    if isinstance(protocol,ClassTypes) and isinstance(obj,protocol):
        return obj
        
    try:
        _conform = obj.__conform__
    except AttributeError:
        pass
    else:
        try:
            result = _conform(protocol)
            if result is not None:
                return result
        except TypeError:
            if exc_info()[2].tb_frame is not _getframe():
                raise

    try:
        _adapt = protocol.__adapt__
    except AttributeError:
        pass
    else:
        try:
            result = _adapt(obj)
            if result is not None:
                return result   
        except TypeError:
            if exc_info()[2].tb_frame is not _getframe():
                raise
            
    if default is _marker:
        raise NotImplementedError("Can't adapt", obj, protocol)

    return default

def implements(*interfaces):

    def callback(klass):
        klass.__implements__ = interfaces
        return klass

    addClassAdvisor(callback)


def classProvides(*interfaces):

    def callback(klass):
        klass.__class_implements__ = interfaces
        return klass

    addClassAdvisor(callback)

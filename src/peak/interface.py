"""Encapsulate use of Zope's 'Interface' package"""

from zope.interface import Interface, Attribute
from zope.interface.implements import implements as addDeclarationToType

__all__ = [
    'Interface', 'Attribute', 
]

# We don't want to export 'addDeclarationToType' by default; we only use it
# in 'peak.config.interfaces' right now, and that should go away eventually.


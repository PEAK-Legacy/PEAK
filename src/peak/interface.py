"""Encapsulate use of Zope's 'Interface' package"""

from Interface import Interface
from Interface.Attribute import Attribute
from Interface.Implements import implements as addDeclarationToType

__all__ = [
    'Interface', 'Attribute', 
]

# We don't want to export 'addDeclarationToType' by default; we only use it
# in 'peak.config.interfaces' right now, and that should go away eventually.


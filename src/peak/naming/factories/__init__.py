"""Factories for objects, states, and URL scheme contexts"""

from peak.naming.interfaces import IObjectFactory, IAddress
from peak.naming.references import NNS_Reference
from peak.naming.properties import SCHEMES_PREFIX

__implements__ = IObjectFactory


def getObjectInstance(refInfo, name, context, attrs=None):

    if IAddress.isImplementedBy(refInfo):
        return refInfo.retrieve(refInfo, name, context, attrs)

    elif isinstance(refInfo, NNS_Reference):
        # default is to treat the object as its own NNS
        return refInfo.relativeTo




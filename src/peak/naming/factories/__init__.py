"""Factories for objects, states, and URL scheme contexts"""

from peak.naming.interfaces import IObjectFactory, IAddress
from peak.naming.references import NNS_Reference
from peak.naming.properties import SCHEMES_PREFIX

__implements__ = IObjectFactory


schemeParsers = {
    'import':       'peak_imports:importURL',
    'ldap':         'ldap:ldapURL',
    'smtp':         'smtp:smtpURL',
    'uuid':         'uuid:uuidURL',
    'lockfile':     'lockfiles:lockfileURL',
    'nulllockfile': 'lockfiles:lockfileURL',
    'shlockfile':   'lockfiles:lockfileURL',
    'flockfile':    'lockfiles:lockfileURL',
    'winflockfile': 'lockfiles:lockfileURL',
}


def register(propertyMap):
    for k,v in schemeParsers.items():
        propertyMap.setValue(SCHEMES_PREFIX+k, 'peak.naming.factories.'+v)
    

def getObjectInstance(refInfo, name, context, attrs=None):

    if IAddress.isImplementedBy(refInfo):
        return refInfo.retrieve(refInfo, name, context, attrs)

    elif isinstance(refInfo, NNS_Reference):
        # default is to treat the object as its own NNS
        return refInfo.relativeTo




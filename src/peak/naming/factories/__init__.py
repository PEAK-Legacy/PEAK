"""Factories for objects, states, and URL scheme contexts"""

from peak.naming.interfaces import *
from peak.naming.references import *

from peak.binding.imports import importObject, importString

__implements__ = (
    IObjectFactory, IStateFactory, IURLContextFactory, IInitialContextFactory
)

schemes = {
}

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


def getInitialContext(parentComponent=None, **options):
    from peak.naming.contexts import AbstractContext  # XXX temporary hack
    return AbstractContext(parentComponent, **options)
















def getURLContext(scheme, context, iface=IBasicContext):

    lscheme = scheme.lower()    
    factory = schemes.get(lscheme)

    if factory is None:
        try:
            factory = importString(scheme, globals())
        except ImportError:
            pass
           
    elif isinstance(factory,str):
        factory=importObject(factory, globals())


    if factory is not None:
    
        if IURLContextFactory.isImplementedBy(factory):
            schemes[lscheme] = factory
            return factory.getURLContext(scheme, context, iface)

        elif iface.isImplementedByInstancesOf(factory):
            schemes[lscheme] = factory
            return factory(context)


    factory = schemeParsers.get(lscheme)

    if factory is not None:
    
        if isinstance(factory,str):
            factory=importObject(factory,globals())
            schemeParsers[lscheme]=factory
            
        if IAddress.isImplementedByInstancesOf(factory):
            from peak.naming.contexts import GenericURLContext
            return GenericURLContext(context)

    return None


def getObjectInstance(refInfo, name, context, attrs=None):

    if IAddress.isImplementedBy(refInfo):
        return refInfo.retrieve(refInfo, name, context, attrs)

    elif isinstance(refInfo, NNS_Reference):
        # default is to treat the object as its own NNS
        return refInfo.relativeTo


def getStateToBind(obj, name, context, attrs=None):
    pass    # XXX



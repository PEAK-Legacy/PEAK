"""Factories for objects, states, and URL scheme contexts"""

from peak.naming.interfaces import *
from peak.naming.references import *

from peak.binding.imports import importObject, importString

__implements__ = IObjectFactory, IStateFactory, IURLContextFactory

schemes = {
}

schemeParsers = {
    'import':   'peak_imports:importURL',
    'ldap'  :   'ldap:ldapURL',
    'smtp'  :   'smtp:smtpURL',
    'uuid'  :   'uuid:uuidURL',
}























def getURLContext(scheme, context, environment, iface=IBasicContext):

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
            return factory.getURLContext(scheme, context, environment, iface)

        elif iface.isImplementedByInstancesOf(factory):
            schemes[lscheme] = factory
            return factory(environment)


    factory = schemeParsers.get(lscheme)

    if factory is not None:
    
        if isinstance(factory,str):
            factory=importObject(factory,globals())
            schemeParsers[lscheme]=factory
            
        if IAddress.isImplementedByInstancesOf(factory):
            from peak.naming.contexts import GenericURLContext
            return GenericURLContext(environment)

    return None


def getObjectInstance(refInfo, name, context, environment, attrs=None):

    if IAddress.isImplementedBy(refInfo):
        return refInfo.retrieve(refInfo, name, context, environment, attrs)

    elif isinstance(refInfo, NNS_Reference):
        # default is to treat the object as its own NNS
        return refInfo.relativeTo


def getStateToBind(obj, name, context, environment, attrs=None):
    pass    # XXX



"""Factories for objects, states, and URL scheme contexts"""

from peak.naming.interfaces import *
from peak.naming.references import *

from peak.binding.imports import importObject, importString

__implements__ = IObjectFactory, IStateFactory, IURLContextFactory

schemes = {
}

schemeParsers = {
    'smtp'  :   'smtp:smtpURL',
    'ldap'  :   'ldap:ldapURL',
    'import':   'peak_imports:importURL',
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
            
        from peak.naming.contexts import GenericURLContext
        return GenericURLContext(environment)

    return None



addrTypes = {
}


def getObjectInstance(refInfo, name, context, environment, attrs=None):

    def lookupByAddr(refAddr):    
        factory = addrTypes.get(refAddr.type)

        if factory is not None:
            if isinstance(factory,str):
                factory = importObject(factory, globals())
                addrTypes[refAddr.type] = factory

            if IObjectFactory.isImplementedBy(factory):
                factory = factory.getObjectInstance

            return factory(
                refAddr, name, context, environment, attrs
            )

    if isinstance(refInfo, Reference):

        for refAddr in refInfo:
            obj = lookupByAddr(refAddr)
            if obj is not None:
                return obj

    elif isinstance(refInfo, RefAddr):
        return lookupByAddr(refInfo)

    factory = getattr(refInfo,'_defaultObjectFactory',None)

    if factory:
        factory = importObject(factory)
        return factory(refInfo, name, context, environment, attrs)





def getStateToBind(obj, name, context, environment, attrs=None):
    pass    # XXX



"""Factories for objects, states, and URL scheme contexts"""

from peak.naming.interfaces import *
from peak.naming.references import *

from peak.binding.imports import importObject, importString

__implements__ = IObjectFactory, IStateFactory, IURLContextFactory

schemes = {
    'smtp'  :   'smtp:smtpContext',
    'import':   'peak_imports:importContext',
}


def getURLContext(scheme, context, environment, iface=IBasicContext):
    
    factory = schemes.get(scheme.lower())

    if factory is None:
        try:
            factory = importString(scheme, globals())
        except ImportError:
            return None
        schemes[scheme.lower()] = factory
        
    if isinstance(factory,str):
        factory=importObject(factory, globals())
        schemes[scheme.lower()] = factory
        
    if IURLContextFactory.isImplementedBy(factory):
        return factory.getURLContext(scheme, context, environment, iface)

    elif iface.isImplementedByInstancesOf(factory):
        return factory(environment)






addrTypes = {
    'smtp'  :   'smtp:smtpFactory',
    'PEAK Import Specifier' : 'peak_imports:importFactory',
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






def getStateToBind(obj, name, context, environment, attrs=None):
    pass    # XXX



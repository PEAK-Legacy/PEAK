from peak.api import *
from interfaces import *
from types import FunctionType, MethodType

__all__ = ['SimpleLocation', 'ComponentAsLocation', 'ContainerAsLocation']


class SimpleLocation(binding.Component):

    """Basic location object; uses self as its subject and for security"""

    protocols.advise(
        instancesProvide = [IWebLocation]
    )

    def getObject(self):
        return self

    def getSublocation(self, name, interaction, forUser=NOT_GIVEN):

        ob = self.getObject()
        loc = getattr(ob, name, NOT_FOUND)

        if loc is not NOT_FOUND:

            if (forUser is not None
                and not interaction.allows(ob, name, user=forUser)
            ):
                return NOT_ALLOWED

            loc = adapt(loc, interaction.locationProtocol)

        return loc

    def preTraverse(self, interaction):
        pass    # Should do any traversal requirements checks





class ComponentAsLocation(SimpleLocation):

    """Location adapter for simple objects; uses subject's security"""

    protocols.advise(
        instancesProvide = [IWebLocation],
        factoryMethod = 'asLocationFor',
        asAdapterForTypes = [object],
    )

    ob = None

    def asLocationFor(klass, ob, proto):
        return klass(ob = ob)

    asLocationFor = classmethod(asLocationFor)

    def getObject(self):
        return self.ob






















class ContainerAsLocation(ComponentAsLocation):

    """Location adapter for container components"""

    protocols.advise(
        instancesProvide = [IWebLocation],
        factoryMethod = 'asLocationFor',
        asAdapterForProtocols = [naming.IBasicContext, storage.IDataManager],
        asAdapterForTypes = [dict],
    )

    def getSublocation(self, name, interaction, forUser=NOT_GIVEN):

        if name.startswith('@@'):
            return super(ContainerAsLocation,self).getSublocation(
                name[2:], interaction
            )

        try:
            ob = self.ob[name]
        except KeyError:
            return super(ContainerAsLocation,self).getSublocation(
                name,interaction
            )

        if forUser is None or interaction.allows(ob, user=forUser):
            return adapt(ob, interaction.locationProtocol)

        return NOT_ALLOWED












class CallableAsWebMethod(protocols.Adapter):

    """Make functions/methods callable"""

    protocols.advise(
        instancesProvide = [IWebMethod],
        asAdapterForTypes = [FunctionType, MethodType]
    )

    def render(self, interaction):
        request = interaction.request
        from zope.publisher.publish import mapply
        return mapply(self.subject, request.getPositionalArguments(), request)





























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

    def getSublocation(self, name, interaction):

        ob = self.getObject()

        if not interaction.allows(ob, name):
            return NOT_ALLOWED

        ob = getattr(ob, name, NOT_FOUND)

        if ob is not NOT_FOUND:
            ob = adapt(ob, interaction.locationProtocol)

        return ob

    def preTraverse(self, interaction):
        pass    # Should do any traversal requirements checks







class ComponentAsLocation(SimpleLocation):

    """Location adapter for simple components; uses subject's security"""

    protocols.advise(
        instancesProvide = [IWebLocation],
        factoryMethod = 'asLocationFor',
        asAdapterForProtocols = [binding.IComponent],
    )

    ob = None

    def asLocationFor(klass, ob, proto):
        return klass(ob = ob)

    asLocationFor = classmethod(asLocationFor)

























class ContainerAsLocation(ComponentAsLocation):

    """Location adapter for container components"""

    protocols.advise(
        instancesProvide = [IWebLocation],
        factoryMethod = 'asLocationFor',
        asAdapterForProtocols = [naming.IBasicContext, storage.IDataManager],
        asAdapterForTypes = [dict],
    )

    def getSublocation(self, name, interaction):

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

        if interaction.allows(ob):
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




























from peak.api import *
from interfaces import *
from types import FunctionType, MethodType

__all__ = [
    'SimpleTraversable', 'ComponentAsTraversable', 'ContainerAsTraversable'
]


class SimpleTraversable(binding.Component):

    """Basic traversable object; uses self as its subject and for security"""

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    def getObject(self):
        return self

    def traverseTo(self, name, interaction):

        ob = self.getObject()
        loc = getattr(ob, name, NOT_FOUND)

        if loc is not NOT_FOUND:

            if not interaction.allows(ob, name):
                return NOT_ALLOWED

            loc = adapt(loc, interaction.pathProtocol)

        return loc

    def preTraverse(self, interaction):
        pass    # Should do any traversal requirements checks





class ComponentAsTraversable(SimpleTraversable):

    """Traversal adapter for simple objects; uses subject's security"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForTypes = [object],
    )

    ob = None

    def asTraversableFor(klass, ob, proto):
        return klass(ob = ob)

    asTraversableFor = classmethod(asTraversableFor)

    def getObject(self):
        return self.ob






















class ContainerAsTraversable(ComponentAsTraversable):

    """Traversal adapter for container components"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForProtocols = [naming.IBasicContext, storage.IDataManager],
        asAdapterForTypes = [dict],
    )

    def traverseTo(self, name, interaction):

        if name.startswith('@@'):
            return super(ContainerAsTraversable,self).traverseTo(
                name[2:], interaction
            )

        try:
            ob = self.ob[name]
        except KeyError:
            return super(ContainerAsTraversable,self).traverseTo(
                name,interaction
            )

        if interaction.allows(ob):
            return adapt(ob, interaction.pathProtocol)

        return NOT_ALLOWED












class CallableAsWebPage(protocols.Adapter):

    """Make functions/methods callable"""

    protocols.advise(
        instancesProvide = [IWebPage],
        asAdapterForTypes = [FunctionType, MethodType]
    )

    def render(self, interaction):
        request = interaction.request
        from zope.publisher.publish import mapply
        return mapply(self.subject, request.getPositionalArguments(), request)





























from peak.api import *
from interfaces import *
from types import FunctionType, MethodType
import posixpath

__all__ = [
    'Traversable', 'Decorator', 'ContainerAsTraversable',
    'MultiTraverser',
]
































class Traversable(binding.Component):

    """Basic traversable object; uses self as its subject and for security"""

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    def getObject(self, interaction):
        return self

    def traverseTo(self, name, interaction):

        ob = self.getObject(interaction)
        loc = getattr(ob, name, NOT_FOUND)

        if loc is not NOT_FOUND:

            if not interaction.allows(ob, name):
                return NOT_ALLOWED

            loc = adapt(loc, interaction.pathProtocol)

        return loc

    def preTraverse(self, interaction):
        pass    # Should do any traversal requirements checks

    def _getLocalPath(self, d, a):

        name = self.getComponentName()

        if name:
            base = self.getParentComponent().localPath
            return posixpath.join(base, name)   # handles empty parts OK

        raise ValueError("Traversable was not assigned a name", self)

    localPath = binding.Once(_getLocalPath)


class Decorator(Traversable):

    """Traversal adapter whose local attributes add/replace the subject's"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForTypes = [object],
    )

    ob = None

    def asTraversableFor(klass, ob, proto):
        return klass(ob = ob)

    asTraversableFor = classmethod(asTraversableFor)


    def getObject(self, interaction):
        return self.ob

    def traverseTo(self, name, interaction):

        loc = getattr(self, name, NOT_FOUND)

        if loc is not NOT_FOUND:

            if interaction.allows(self, name):
                return adapt(loc, interaction.pathProtocol)

            # Access failed, see if attribute is private
            guard = adapt(self,security.IGuardedObject,None)

            if guard is not None and guard.getPermissionsForName(name):
                # We have explicit permissions defined, so reject access
                return NOT_ALLOWED

        # attribute is absent or private, fall through to underlying object
        return super(Decorator,self).traverseTo(name, interaction)


class ContainerAsTraversable(Decorator):

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












class MultiTraverser(Traversable):

    """Aggregate traversal across a sequence of delegate traversables"""

    items = binding.requireBinding("traversables to traversed")

    def getObject(self, interaction):
        # Return the first item
        for item in self.items:
            return item.getObject(interaction)

    def preTraverse(self, interaction):
        for item in self.items:
            item.preTraverse(interaction)

    def traverseTo(self, name, interaction):

        newItems = []

        for item in self.items:

            loc = item.traverseTo(name, interaction)

            if loc is NOT_ALLOWED:
                return NOT_ALLOWED

            if loc is not NOT_FOUND:
                # we should suggest the parent, since our caller won't
                binding.suggestParentComponent(item, name, loc)
                newItems.append(loc)

        if not newItems:
            return NOT_FOUND
        if len(newItems)==1:
            loc = newItems[0]
        else:
            loc = self._subTraverser(self, name, items = newItems)
        return adapt(loc, interaction.pathProtocol)

    _subTraverser = lambda self, *args, **kw: self.__class__(*args,**kw)

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





























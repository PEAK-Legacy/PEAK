from peak.api import *
from interfaces import *
from places import Traversable, MultiTraverser
from publish import TraversalPath
__all__ = ['Skin',]


class SkinTraverser(MultiTraverser):

    def getAbsoluteURL(self, interaction):
        return self.getParentComponent().getResourceURL('',interaction)

    items = binding.bindTo('../layers')




























class Skin(Traversable):

    protocols.advise(
        instancesProvide = [ISkin]
    )

    traverser = binding.New(SkinTraverser)

    root   = binding.requireBinding("Underlying traversal root")
    policy = binding.requireBinding("Interaction Policy")
    layers = binding.requireBinding("Sequence of resource managers")

    def dummyInteraction(self,d,a):
        policy = self.policy
        return policy.interactionClass(
            policy, None, policy=policy, request=None, skin=self, user=None
        )

    dummyInteraction = binding.Once(dummyInteraction)

    def getResource(self, path):
        traverser = self.traverser
        interaction = self.dummyInteraction
        path = adapt(path,TraversalPath)
        return path.traverse(
            traverser, interaction, getRoot = lambda o,i: traverser
        )

    def traverseTo(self, name, interaction):

        if name == interaction.resourcePrefix:
            return adapt(self.traverser, interaction.pathProtocol)

        return self.root.traverseTo(name, interaction)







    def getAbsoluteURL(self, interaction):
        return interaction.request.getApplicationURL()


    def getResourceURL(self, path, interaction):

        while path.startswith('/'):
            path = path[1:]

        base = self.getAbsoluteURL()
        path = '%s/%s/%s' % base, interaction.resourcePrefix, path

        while path.endswith('/'):
            path = path[:-1]
































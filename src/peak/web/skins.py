from peak.api import *
from interfaces import *
from places import Traversable, MultiTraverser
from publish import TraversalPath

__all__ = ['Skin',]


class SkinTraverser(MultiTraverser):

    # Our local path is effectively '/++resources++'
    localPath = binding.bindTo(RESOURCE_PREFIX)

    items = binding.bindTo('../layers')

    _subTraverser = MultiTraverser

























class Skin(Traversable):

    protocols.advise(
        instancesProvide = [ISkin]
    )

    traverser = binding.New(SkinTraverser)

    root   = binding.requireBinding("Underlying traversal root")
    policy = binding.requireBinding("Interaction Policy")
    layers = binding.requireBinding(
        "Sequence of resource managers", suggestParent=False
        # We don't suggest the parent, so that the layers will bind to our
        # traverser, instead of to us!
    )

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



    localPath = ''  # skin is at root


    def getResourceURL(self, path, interaction):

        while path.startswith('/'):
            path = path[1:]

        base = interaction.getAbsoluteURL(self.traverser)

        if path:
            return '%s/%s' % (base, path)
        else:
            return base




























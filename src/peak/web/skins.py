from peak.api import *
from interfaces import *
from places import Traversable, MultiTraverser, Traversal
from publish import TraversalPath

__all__ = ['Skin',]


class SkinTraverser(MultiTraverser):

    protocols.advise(
        instancesProvide = [IResource]
    )

    # Our local path is effectively '/++resources++'
    resourcePath = binding.bindTo(RESOURCE_PREFIX)

    items = binding.bindTo('../layers')

    _subTraverser = MultiTraverser





















class Skin(Traversable):

    protocols.advise(
        instancesProvide = [ISkin]
    )

    traverser = binding.New(SkinTraverser)
    cache     = binding.New(dict)

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

    def traverseTo(self, name, interaction):

        if name == interaction.resourcePrefix:
            return self.traverser

        return self.root.traverseTo(name, interaction)

    resourcePath = ''  # skin is at root








    def getResource(self, path):

        path = adapt(path,TraversalPath)

        if path in self.cache:
            return self.cache[path]

        interaction = self.dummyInteraction
        start = Traversal(
            self, interaction=interaction
        ).contextFor(interaction.resourcePrefix)   # start at ++resources++

        resourceCtx = path.traverse(start, getRoot = lambda ctx: start)
        self.cache[path] = resourceCtx.subject
        return resourceCtx.subject


    def getResourceURL(self, path, interaction):

        while path.startswith('/'):
            path = path[1:]

        base = interaction.getAbsoluteURL(self.traverser)

        if path:
            return '%s/%s' % (base, path)
        else:
            return base














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
    resourcePath = binding.Obtain(RESOURCE_PREFIX)

    items = binding.Obtain('../layers')

    _subTraverser = MultiTraverser





















class Skin(Traversable):

    protocols.advise(
        instancesProvide = [ISkin]
    )

    traverser = binding.Make(SkinTraverser)
    cache     = binding.Make(dict)

    root   = binding.Require("Underlying traversal root")
    policy = binding.Require("Interaction Policy")
    layers = binding.Require(
        "Sequence of resource managers", suggestParent=False
        # We don't suggest the parent, so that the layers will bind to our
        # traverser, instead of to us!
    )

    def dummyInteraction(self):
        policy = self.policy
        return policy.interactionClass(
            policy, None, policy=policy, request=None, skin=self, user=None
        )

    dummyInteraction = binding.Make(dummyInteraction)

    def traverseTo(self, name, ctx):

        if name == ctx.interaction.resourcePrefix:
            return self.traverser

        return self.root.traverseTo(name, ctx)

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














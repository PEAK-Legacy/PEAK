from peak.api import *
from interfaces import *
from places import Traversable, MultiTraverser
from publish import TraversalPath
from resources import Resource

__all__ = [
    'Skin',
]
































class Skin(Traversable):

    """Skins provide a branch-point between the app root and resources"""

    protocols.advise(
        instancesProvide = [ISkin]
    )

    resources  = binding.Make(lambda self: MultiTraverser(items=self.layers))
    cache      = binding.Make(dict)
    policy     = binding.Obtain('..')
    root       = binding.Delegate("policy")

    layerNames = binding.Require("Sequence of layer names")
    layers     = binding.Make(
        lambda self: map(self.policy.getLayer, self.layerNames)
    )

    dummyInteraction = binding.Make(
        lambda self: self.policy.newInteraction(user=None)
    )

    def traverseTo(self, name, ctx):

        if name == ctx.policy.resourcePrefix:
            return self.resources

        return self.root.traverseTo(name, ctx)

    resourcePath = ''  # skin is at root











    def getResource(self, path):

        path = adapt(path,TraversalPath)

        if path in self.cache:
            return self.cache[path]

        start = self.policy.newContext(
            skin=self, interaction=self.dummyInteraction
        )

        # start at ++resources++
        start = start.traverseName(self.policy.resourcePrefix)

        resourceCtx = path.traverse(start, getRoot = lambda ctx: start)
        self.cache[path] = subject = resourceCtx.current
        return subject

























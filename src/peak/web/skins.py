from peak.api import *
from interfaces import *
from places import Traversable, MultiTraverser
from publish import TraversalPath
from resources import Resource
from wsgiref.util import setup_testing_defaults

__all__ = [
    'Skin',
]































class Skin(MultiTraverser):

    """Skins provide a branch-point between the app root and resources"""

    protocols.advise(
        instancesProvide = [ISkin]
    )

    resources  = binding.Make(lambda self: MultiTraverser(items=self.layers))
    cache      = binding.Make(dict)
    policy     = binding.Obtain('..')
    root       = binding.Delegate("policy")

    layerNames = binding.Require("Sequence of layer names")
    
    items     = binding.Make(
        lambda self: map(self.policy.getLayer, self.layerNames)
    )

    dummyInteraction = binding.Make(
        lambda self: self.policy.newInteraction(user=None)
    )

    dummyEnviron = {}
    setup_testing_defaults(dummyEnviron)

    def getURL(self, ctx):
        # We want an absolute URL
        return ctx.rootURL+'/'[ctx.rootURL.endswith('/'):]+self.resourcePath

    resourcePath = binding.Obtain('policy/resourcePrefix')










    def getResource(self, path):

        path = adapt(path,TraversalPath)

        if path in self.cache:
            return self.cache[path]

        start = self.policy.newContext(
            self.dummyEnviron.copy(), self, self, self.dummyInteraction
        )

        resourceCtx = path.traverse(start, getRoot = lambda ctx: start)
        self.cache[path] = subject = resourceCtx.current
        return subject




























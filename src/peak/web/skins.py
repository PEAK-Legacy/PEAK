from peak.api import *
from interfaces import *
from places import Traversable, MultiTraverser

__all__ = ['Skin',]


class SkinTraverser(Traversable):

    def getAbsoluteURL(self, interaction):
        base = interaction.request.getApplicationURL()
        return '%s/%s' % base, interaction.resourcePrefix

    # def traverseTo(self, name, interaction):
    #   lookup package from interaction.skin



class Skin(Traversable):

    traverser = binding.New(SkinTraverser)

    root = binding.requireBinding("Underlying traversal root")

    layers = binding.requireBinding("Sequence of resource managers")

    def traverseTo(self, name, interaction):

        if name == interaction.resourcePrefix:
            return adapt(self.traverser, interaction.pathProtocol)

        return self.root.traverseTo(name, interaction)

    def getAbsoluteURL(self, interaction):
        return interaction.request.getApplicationURL()



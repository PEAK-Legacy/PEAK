"""Configuration Properties Context

    This context is primarily intended as an example of a simple hierarchical
    naming context, that can easily be tested.  This serves two purposes:
    illustrate how to build such a context, and test the features of the
    naming system that support such contexts.
"""

from peak.api import *


class PropertyPath(naming.CompoundName):

    """Property paths are dot-separated, left-to-right, compound names"""

    syntax = naming.PathSyntax(
        direction = 1,
        separator = '.',
    )


class PropertyURL(naming.URL.Base):

    """The 'config:' URL scheme: property name in a composite name"""

    supportedSchemes = 'config',

    nameAttr = 'body'

    def getCanonicalBody(self):
        return naming.CompositeName.parse(self.body or '', PropertyPath)










class PropertyContext(naming.NameContext):

    schemeParser   = PropertyURL
    compoundParser = PropertyPath


    def _get(self, name, retrieve=1):

        return self.__class__(self,
            namingAuthority = self.namingAuthority,
            nameInContext   = self.nameInContext + name,
        ), None


    def _contextNNS(self, attrs=None):

        ob = config.getProperty(
            self.creationParent, str(self.nameInContext), NOT_FOUND
        )

        if ob is NOT_FOUND:
            return ob

        return ob, attrs


















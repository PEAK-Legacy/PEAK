"""Configuration Properties Context

    This context is primarily intended as an example of a simple hierarchical
    naming context, that can easily be tested.  This serves two purposes:
    illustrate how to build such a context, and test the features of the
    naming system that support such contexts.
"""

from peak.api import *
from peak.naming.contexts import NameContext


class PropertyPath(naming.CompoundName):

    """Property paths are dot-separated, left-to-right, compound names"""

    syntax = naming.Syntax(
        direction = 1,
        separator = '.',
    )


class PropertyURL(naming.ParsedURL):

    """The 'config:' URL scheme: property name in a composite name"""

    supportedSchemes = 'config',

    nameAttr = 'body'

    def parse(self, scheme, body):
        body = naming.CompositeName.parse(body, PropertyPath)
        return locals()








class PropertyContext(NameContext):

    schemeParser   = PropertyURL
    compoundParser = PropertyPath


    def _get(self, name, retrieve=1):

        return self.__class__(self,
            namingAuthority = self.namingAuthority,
            nameInContext   = self.nameInContext + name,
        ), None


    def _contextNNS(self, attrs=None):

        ob = config.getProperty(
            str(self.nameInContext), self.creationParent, NOT_FOUND
        )

        if ob is NOT_FOUND:
            return ob

        return ob, attrs



from protocols import Interface, Attribute
from peak.security.interfaces import IAuthorizedPrincipal, IInteraction

__all__ = [
    'IWebInteraction', 'IWebLocation', 'IWebMethod',
]

try:
    from zope.publisher.interfaces import IPublication
    from zope.publisher.interfaces.browser import IBrowserPublication
    from zope.publisher.interfaces.xmlrpc import IXMLRPCPublication

except ImportError:
    zopePublicationInterfaces = ()

else:
    import protocols.zope_support
    zopePublicationInterfaces = (
        IPublication, IBrowserPublication, IXMLRPCPublication
    )


class IWebInteraction(IInteraction):

    """Component representing a web hit"""

    protocols.advise(
        protocolExtends = zopePublicationInterfaces
    )

    request  = Attribute("""The web request""")
    response = Attribute("""The web response""")

    app = Attribute("""The underlying application object""")

    locationProtocol = Attribute("""Protocol to adapt locations to""")
    behaviorProtocol = Attribute("""Protocol to adapt behaviors to""")

    # XXX skin, ...?


class IWebLocation(Interface):

    """A component representing a URL location"""

    def getSublocation(name, interaction):
        """Return an IWebLocation for the named sublocation, or NOT_FOUND"""

    def getObject(interaction):
        """Return the underlying object that is at this location"""


class IWebMethod(Interface):

    def render(interaction):
        """Render a response"""



























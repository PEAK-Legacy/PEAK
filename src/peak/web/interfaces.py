from protocols import Interface, Attribute
from peak.security.interfaces import IAuthorizedPrincipal, IInteraction
import protocols
from peak.api import PropertyName

__all__ = [
    'IWebInteraction', 'IWebLocation', 'IWebMethod', 'IInteractionPolicy',
    'LOCATION_PROTOCOL', 'BEHAVIOR_PROTOCOL', 'INTERACTION_CLASS',
    'DEFAULT_METHOD', 'APPLICATION_LOG', 'AUTHENTICATION_SERVICE',
    'ERROR_PROTOCOL', 'SKIN_SERVICE', 'IWebException',
]


LOCATION_PROTOCOL = PropertyName('peak.web.locationProtocol')
BEHAVIOR_PROTOCOL = PropertyName('peak.web.behaviorProtocol')
ERROR_PROTOCOL    = PropertyName('peak.web.errorProtocol')

INTERACTION_CLASS = PropertyName('peak.web.interactionClass')
DEFAULT_METHOD    = PropertyName('peak.web.defaultMethod')
APPLICATION_LOG   = PropertyName('peak.web.appLog')

AUTHENTICATION_SERVICE = PropertyName('peak.web.authenticationService')
SKIN_SERVICE           = PropertyName('peak.web.skinService')

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

    errorProtocol    = Attribute("""Protocol to adapt exceptions to""")
    locationProtocol = Attribute("""Protocol to adapt locations to""")
    behaviorProtocol = Attribute("""Protocol to adapt behaviors to""")

    log = Attribute("""Default 'running.ILogger' for interactions""")

    skin = Attribute("""Root namespace for presentation resources""")


class IInteractionPolicy(Interface):

    """Component holding cross-hit configuration"""

    errorProtocol    = Attribute("""Protocol to adapt exceptions to""")
    locationProtocol = Attribute("""Protocol to adapt locations to""")
    behaviorProtocol = Attribute("""Protocol to adapt behaviors to""")

    log = Attribute("""Default 'running.ILogger' for interactions""")

    authSvc = Attribute("""Authentication service component""")
    skinSvc = Attribute("""Skin service component""")

    defaultMethod = Attribute("""Default method name (e.g. 'index_html')""")





class IWebLocation(Interface):

    """A component representing a URL location"""

    def preTraverse(interaction):
        """Invoked before traverse by web requests"""

    def getSublocation(name, interaction, forUser=NOT_GIVEN):
        """Return named IWebLocation, or NOT_ALLOWED/NOT_FOUND

        If 'forUser' is 'None', do not perform security checks.  Otherwise,
        'forUser' should be passed to 'interaction.allows()' for security
        checks.
        """

    def getObject(interaction):
        """Return the underlying object that is at this location"""


class IWebMethod(Interface):

    """A component for rendering an HTTP response"""

    def render(interaction):
        """Render a response"""


class IWebException(Interface):

    """An exception that knows how it should be handled for a web app"""

    def handleException(interaction, thrower, exc_info, retry_allowed=1):
        """Perform necessary recovery actions"""









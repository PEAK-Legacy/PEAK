from protocols import Interface, Attribute
from peak.security.interfaces import IAuthorizedPrincipal, IInteraction
import protocols
from peak.api import PropertyName

__all__ = [
    'IWebInteraction', 'IWebLocation', 'IWebMethod', 'IInteractionPolicy',
    'LOCATION_PROTOCOL', 'BEHAVIOR_PROTOCOL', 'INTERACTION_CLASS',
    'DEFAULT_METHOD', 'APPLICATION_LOG', 'AUTHENTICATION_SERVICE',
]


LOCATION_PROTOCOL = PropertyName('peak.web.locationProtocol')
BEHAVIOR_PROTOCOL = PropertyName('peak.web.behaviorProtocol')
INTERACTION_CLASS = PropertyName('peak.web.interactionClass')

DEFAULT_METHOD    = PropertyName('peak.web.defaultMethod')
APPLICATION_LOG   = PropertyName('peak.web.appLog')
AUTHENTICATION_SERVICE = PropertyName('peak.web.authenticationService')


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

    log = Attribute("""Default 'running.ILogger' for interactions""")   

    # XXX skin, ...?


class IInteractionPolicy(Interface):

    """Component holding cross-hit configuration"""

    locationProtocol = Attribute("""Protocol to adapt locations to""")
    behaviorProtocol = Attribute("""Protocol to adapt behaviors to""")

    log = Attribute("""Default 'running.ILogger' for interactions""")

    authSvc = Attribute("""Authentication service component""")

    defaultMethod = Attribute("""Default method name (e.g. 'index_html')""")








class IWebLocation(Interface):

    """A component representing a URL location"""

    def preTraverse(interaction):
        """Invoked before traverse by web requests"""

    def getSublocation(name, interaction):
        """Return named IWebLocation, or NOT_ALLOWED/NOT_FOUND"""

    def getObject(interaction):
        """Return the underlying object that is at this location"""


class IWebMethod(Interface):

    def render(interaction):
        """Render a response"""






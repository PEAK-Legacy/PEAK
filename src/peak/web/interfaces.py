from protocols import Interface, Attribute
from peak.security.interfaces import IAuthorizedPrincipal, IInteraction
import protocols
from peak.api import PropertyName

__all__ = [
    'IWebInteraction', 'IWebLocation', 'IWebMethod', 'IInteractionPolicy',
    'LOCATION_PROTOCOL', 'BEHAVIOR_PROTOCOL', 'INTERACTION_CLASS',
    'DEFAULT_METHOD', 'APPLICATION_LOG', 'AUTHENTICATION_SERVICE',
    'ERROR_PROTOCOL', 'SKIN_SERVICE', 'IWebException',
    'ITemplateNode',    'ITemplateNodeFactory',
    'ITemplateElement', 'ITemplateElementFactory',
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

    def getSublocation(name, interaction):
        """Return named IWebLocation, or NOT_ALLOWED/NOT_FOUND"""

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













class ITemplateNode(Interface):

    """A component of a page template"""

    def renderTo(interaction, writeFunc, currentModel, executionContext):
        """Write template's output by calling 'writeFunc()' 0 or more times

        'interaction' is the current 'IWebInteraction'.  'currentModel' is
        the current "model" object being rendered (e.g. the object the template
        is a method of).  'executionContext' is a component used to supply
        arbitrary properties/utilities during template execution.  All of these
        parameters should be supplied to executed child nodes as-is, unless
        the current view wishes to change them.

        For example, if a node wishes to add properties to the
        'executionContext' for its children, it should create a new Component
        with the old 'executionContext' as the new component's parent, then
        supply the new component to child nodes as their 'executionContext'.
        """

    staticText = Attribute(
        """The static XML text that represents this node, or None if
        the node contains any dynamic content."""
    )

    # XXX should be some kind of parseInfo w/source file/line/column















class ITemplateNodeFactory(Interface):

    """Factory to produce a literal or text node"""

    def __call__(parentComponent, componentName=None, xml=u'',
        # XXX parse info
    ):
        """Create an ITemplateNode w/specified XML text

        'xml' will contain the text as it would appear in an XML document;
        i.e., it is already XML-escaped, so no further processing is required
        on output.

        Note that only the first two arguments are positional; the 'xml'
        argument must be supplied as a keyword."""


























class ITemplateElement(ITemplateNode):

    """A component representing an XML/HTML element"""

    def addChild(node):
        """Add 'node' (an 'ITemplateNode') to element's direct children"""

    def addPattern(name, element):
        """Declare 'element' (an 'ITemplateElement') as part of pattern 'name'

        Note that 'element' is not necessarily a direct child of the current
        element, and that this method may be called multiple times for the
        same 'name', if multiple pattern nodes are declared with the same name.
        It's up to the element to do any validation/restriction of pattern
        names/values."""


    tagFactory = Attribute(
        """'ITemplateElementFactory' to be used for non-view child tags"""
    )

    textFactory = Attribute(
        """'ITemplateNodeFactory' to be used for plain text child nodes"""
    )

    literalFactory = Attribute(
        """'ITemplateNodeFactory' to be used for literals (e.g. comments,
        processing instructions, etc.) within this element"""
    )












class ITemplateElementFactory(Interface):

    """Produce an 'ITemplateElement' from a source document element"""

    def __call__(parentComponent, componentName,
        tagName=u'', attribItems=(), nonEmpty=False,
        viewProperty=None, modelPath=None, patternName=None,
        # XXX xmlns maps, parse info
    ):
        """Create an ITemplateElement w/specified attribs, etc.

        'tagName' -- the element tag name, exactly as it appeared in the source
        document

        'attribItems' -- a list of '(name,value)' tuples representing the
        source document attributes for this element, in the order they were
        defined, and only the supplied attributes (i.e. no DTD-implied default
        values).  Template markup attributes (view, model, pattern) are
        excluded.

        'nonEmpty' -- indicates that this element should always have an open
        and close tag, even if it has no children.  This is to support HTML.

        'viewProperty' -- the 'PropertyName' used to retrieve this factory
        (minus the 'peak.web.views.' prefix), or None if the source document
        didn't include a 'view' attribute.

        'modelPath' -- a 'naming.CompoundName' representing the path specified
        in the source document's 'model' attribute, or 'None' if not supplied.

        'patternName' -- the value of the 'pattern' attribute in the source
        document, or 'None' if not supplied.

        Note that only the first two arguments are positional; all others must
        be supplied as keywords."""







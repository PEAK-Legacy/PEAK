from protocols import Interface, Attribute
from peak.security.interfaces import IAuthorizedPrincipal, IInteraction
import protocols
from peak.api import PropertyName
from peak.binding.interfaces import IComponent

__all__ = [
    'IWebInteraction', 'IWebTraversable', 'IWebPage', 'IInteractionPolicy',
    'PATH_PROTOCOL', 'PAGE_PROTOCOL', 'INTERACTION_CLASS', 'RESOURCE_PREFIX',
    'DEFAULT_METHOD', 'APPLICATION_LOG', 'AUTHENTICATION_SERVICE',
    'ERROR_PROTOCOL', 'SKIN_SERVICE', 'IWebException', 'IDOMletState',
    'IDOMletNode',    'IDOMletNodeFactory',
    'IDOMletElement', 'IDOMletElementFactory', 'ISkin', 'IPolicyInfo'
]

PATH_PROTOCOL  = PropertyName('peak.web.pathProtocol')
PAGE_PROTOCOL  = PropertyName('peak.web.pageProtocol')
ERROR_PROTOCOL = PropertyName('peak.web.errorProtocol')

INTERACTION_CLASS = PropertyName('peak.web.interactionClass')
DEFAULT_METHOD    = PropertyName('peak.web.defaultMethod')
RESOURCE_PREFIX   = PropertyName('peak.web.resourcePrefix')
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

class IPolicyInfo(Interface):

    """Standard attributes for interaction policy info"""

    app = Attribute("""The underlying application object""")
    log = Attribute("""Default 'running.ILogger' for interactions""")

    resourcePrefix = Attribute("""Name that starts path to resources""")
    errorProtocol  = Attribute("""Protocol for exception handling""")
    pathProtocol   = Attribute("""Protocol for traversing""")
    pageProtocol   = Attribute("""Protocol for rendering pages""")


class IWebInteraction(IInteraction, IPolicyInfo):

    """Component representing a web hit"""

    protocols.advise(
        protocolExtends = zopePublicationInterfaces
    )

    policy   = Attribute("""The IInteractionPolicy for this interaction""")
    request  = Attribute("""The web request""")
    response = Attribute("""The web response""")

    skin = Attribute("""Root namespace for presentation resources""")


class IInteractionPolicy(IPolicyInfo):

    """Component holding cross-hit configuration"""

    authSvc = Attribute("""Authentication service component""")
    skinSvc = Attribute("""Skin service component""")

    defaultMethod = Attribute("""Default method name (e.g. 'index_html')""")
    interactionClass = Attribute("Factory for interaction instances")




class IWebTraversable(Interface):

    """A component that supports path traversal"""

    def preTraverse(interaction):
        """Invoked before traverse by web requests"""

    def traverseTo(name, interaction):
        """Return named 'IWebTraversable', or 'NOT_ALLOWED'/'NOT_FOUND'"""

    def getObject():
        """Return the underlying object that would be traversed"""

    def getAbsoluteURL(interaction):
        """Return an absolute URL for this traversable"""


class IWebPage(Interface):

    """A component for rendering an HTTP response"""

    def render(interaction):
        """Render a response"""


class IWebException(Interface):

    """An exception that knows how it should be handled for a web app"""

    def handleException(interaction, thrower, exc_info, retry_allowed=1):
        """Perform necessary recovery actions"""


class ISkin(IWebTraversable):

    def getResource(path):
        """Return the named resource"""

    def getResourceURL(path, interaction):
        """Return the URL for the named resource"""

class IDOMletState(IComponent):

    """A component representing a DOMlet's current execution state"""

    interaction = Attribute(
        """The 'IWebInteraction' for this rendering"""
    )

    def write(unicodeData):
        """Call this to write data to the output stream"""

    def findState(interface):
        """Return the nearest object supporting 'interface', or 'None'

        If the state supports the interface, the state is returned, otherwise
        the state's parent components are searched and the first parent
        supporting the interface is returned.  'None' is returned if no parent
        supports the requested interface."""























class IDOMletNode(Interface):

    """A component of a page template"""

    def renderFor(data, state):
        """Write template's output by calling 'state.write()' 0 or more times

        'data' is an 'IWebTraversable' for the object being rendered  (e.g. the
        object the template is a method of).  'state' is an 'IDOMletState'
        component used to supply arbitrary properties/utilities to child
        DOMlets during template execution, and to provide access to the
        current output stream and 'IWebInteraction'.  Both of these
        parameters should be supplied to executed child nodes as-is, unless
        the current DOMlet wishes to change them.

        For example, if a node wishes to add properties to the 'state' for its
        children, it should create a new 'IDOMletState' with the old 'state' as
        its parent, then supply the new state to child nodes's 'renderFor()'
        method.
        """

    staticText = Attribute(
        """The static XML text that represents this node, or None if
        the node contains any dynamic content."""
    )

    # XXX should be some kind of parseInfo w/source file/line/column














class IDOMletNodeFactory(Interface):

    """Factory to produce a literal or text node"""

    def __call__(parentComponent, componentName=None, xml=u'',
        # XXX parse info
    ):
        """Create an IDOMletNode w/specified XML text

        'xml' will contain the text as it would appear in an XML document;
        i.e., it is already XML-escaped, so no further processing is required
        on output.

        Note that only the first two arguments are positional; the 'xml'
        argument must be supplied as a keyword."""


























class IDOMletElement(IDOMletNode):

    """A component representing an XML/HTML element"""

    def addChild(node):
        """Add 'node' (an 'IDOMletNode') to element's direct children"""

    def addParameter(name, element):
        """Declare 'element' (an 'IDOMletElement') as part of parameter 'name'

        Note that 'element' is not necessarily a direct child of the current
        element, and that this method may be called multiple times for the
        same 'name', if multiple 'define' nodes use the same name.
        It's up to the element to do any validation/restriction of parameter
        names/values."""


    tagFactory = Attribute(
        """'IDOMletElementFactory' to be used for non-DOMlet child tags"""
    )

    textFactory = Attribute(
        """'IDOMletNodeFactory' to be used for plain text child nodes"""
    )

    literalFactory = Attribute(
        """'IDOMletNodeFactory' to be used for literals (e.g. comments,
        processing instructions, etc.) within this element"""
    )












class IDOMletElementFactory(Interface):

    """Produce an 'IDOMletElement' from a source document element"""

    def __call__(parentComponent, componentName,
        tagName=u'', attribItems=(), nonEmpty=False,
        domletProperty=None, dataSpec=None, paramName=None,
        # XXX xmlns maps, parse info
    ):
        """Create an IDOMletElement w/specified attribs, etc.

        'tagName' -- the element tag name, exactly as it appeared in the source
        document

        'attribItems' -- a list of '(name,value)' tuples representing the
        source document attributes for this element, in the order they were
        defined, and only the supplied attributes (i.e. no DTD-implied default
        values).  Template markup attributes (domlet and define) are
        excluded.

        'nonEmpty' -- indicates that this element should always have an open
        and close tag, even if it has no children.  This is to support HTML.

        'domletProperty' -- the 'PropertyName' used to retrieve this factory
        (minus the 'peak.web.DOMlets.' prefix), or None if the source document
        didn't specify a DOMlet factory.

        'dataSpec' -- the data specifier from the source document's 'domlet'
        attribute, or an empty string.

        'paramName' -- the value of the 'define' attribute in the source
        document, or 'None' if not supplied.

        Note that only the first two arguments are positional; all others must
        be supplied as keywords."""







from protocols import Interface, Attribute
from peak.security.interfaces import IAuthorizedPrincipal, IInteraction
import protocols
from peak.api import PropertyName, NOT_GIVEN
from peak.binding.interfaces import IComponent

__all__ = [
    'IWebTraversable', 'IInteractionPolicy', 'IAuthService', 'IWebException',
    'RESOURCE_PREFIX', 'DEFAULT_METHOD', 'APPLICATION_LOG',
    'IDOMletState', 'IHTTPHandler', 'IHTTPApplication',
    'IDOMletNode',    'IDOMletNodeFactory', 'IResource', 'ITraversalContext',
    'IDOMletElement', 'IDOMletElementFactory', 'ISkin', 'IPolicyInfo'
]

DEFAULT_METHOD    = PropertyName('peak.web.defaultMethod')
RESOURCE_PREFIX   = PropertyName('peak.web.resourcePrefix')
APPLICATION_LOG   = PropertyName('peak.web.appLog')


class IPolicyInfo(Interface):

    """Standard informational attributes for interaction and policy"""

    app = Attribute("""The underlying application object""")
    log = Attribute("""Default 'logs.ILogger' for interactions""")
    root = Attribute("""Start point for non-resource traversals""")

    resourcePrefix = Attribute("""Name that starts path to resources""")
    defaultMethod  = Attribute("""Default method name (e.g. 'index_html')""")


class IAuthService(Interface):

    def getUser(environ):
        """Return a user object for the environment"""






class IInteractionPolicy(IAuthService, IPolicyInfo):

    """Component holding cross-hit configuration and consolidated services"""

    def getSkin(name):
        """Return the named skin"""

    def getLayer(name):
        """Return the named layer"""

    def newInteraction(**options):
        """Create a new 'IInteraction' with given arguments"""

    def newContext(self,environ={}):
        """Create an initial 'ITraversalContext' based on 'environ'"""

    def beforeTraversal(environ):
        """Begin transaction before traversal"""

    def afterCall(environ):
        """Commit transaction after successful hit"""

    def handleException(environ, exc_info, retry_allowed=1):
        """Convert exception to a handler, and invoke it"""

















class ITraversalContext(Interface):

    """A traversed-to location"""
    
    current = Attribute("""Current object location""")
    environ = Attribute("""WSGI (PEP 333) 'environ' mapping""")
    name    = Attribute("""Name of 'current'""")

    def childContext(name,ob):
        """Return a new child context with name 'name' and current->'ob'"""

    def peerContext(name,ob):
        """Return a new peer context with name 'name' and current->'ob'"""

    def parentContext():
        """Return this context's parent, or self if no parent"""

    def getAbsoluteURL():
        """Return current object's absolute URL"""        

    def getTraversedURL():
        """Return URL traversed to this point"""        

    def traverseName(name):
        """Return a new context obtained by traversing to 'name'"""

    def renderHTTP():
        """Equivalent to 'IHTTPHandler(self.current).handle_http()'"""

    def getResource(path):
        """Return the named resource"""

    def allows(subject,name=None,permissionNeeded=NOT_GIVEN,user=NOT_GIVEN):
        """Return true if 'user' has 'permissionNeeded' for 'subject'

        (See 'security.IInteraction.allows()' for full details)"""





class IWebTraversable(Interface):

    """A component that supports path traversal"""

    def preTraverse(context):

        """Invoked before traverse by web requests

        This can be used to enforce any preconditions for interacting with this
        object via the web.  For example, an e-commerce "checkout" traversable
        might want to ensure that there is an active session and there are
        items in the user's cart, or that the connection is secure.

        This method is only invoked when the traversable is about to be
        traversed or rendered via a web request.  It is not invoked when
        app-server code traverses a location (e.g. by paths in page templates).
        Traversables can take advantage of this to have different security
        restrictions for app-server code and via-the-web URL traversal.
        Resources, for example, do not do security checks in 'traverseTo()',
        only in 'preTraverse()', thus ensuring that app-server code can access
        all available resources, whether they are available to the user or not.
        """

    def traverseTo(name, context):
        """Return named 'IWebTraversable', or raise 'NotAllowed'/'NotFound'"""

    def getURL(context):
        """Return this object's URL in traversal context 'context'"""


class IResource(IWebTraversable):

    """Traversable with a fixed location"""

    resourcePath = Attribute("Relative URL (no leading '/') from skin")






class IHTTPHandler(Interface):

    """A component for rendering an HTTP response"""

    def handle_http(ctx):
        """Return '(status,headers,output_iterable)' tuple

        For the definition of 'status', 'headers', and 'output_iterable',
        see PEP 333.
        """


class IHTTPApplication(IHTTPHandler):

    """An IHTTPHandler that handles exceptions, transactions, etc."""


class IWebException(Interface):

    """An exception that knows how it should be handled for a web app"""

    def handleException(environ,exc_info,retry_allowed=1):
        """Perform necessary recovery actions"""


class IResourceService(Interface):

    resources = Attribute("""ITraversable for resource root""")

    def getResource(path):
        """Return the named resource"""


class ISkin(IResource, IResourceService):
    """A resource container, and the root resource for its contents"""






class IDOMletState(IComponent):

    """A component representing a DOMlet's current execution state"""

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

    def renderFor(environ, state):
        """Write template's output by calling 'state.write()' 0 or more times

        'environ' is an environment mapping for the object being rendered  (e.g.
        the object the template is a method of).  'state' is an 'IDOMletState'
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







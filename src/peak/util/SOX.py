"""Simple Objects from XML - quick-and-dirty XML parsing without a DOM

    This module implements most of the overhead needed for turning SAX
    events into a hierarchy of objects.  E.g., stack handling,
    delegation to node classes, etc.
    
    Note: I originally wrote this module because the Python default DOM
    for XML (way back in the XML-SIG for Python 1.5.2 days) was horrendously
    slow for processing (typically enormous) XMI files.  If 2.2 minidom
    is fast enough and easy enough to use, this package may go away once
    I've ported the XMI support to minidom.  So let me know if you're using
    this module for anything;  I have some non-TransWarp uses for it myself,
    but depending on how easy using minidom turns out to be...  I may switch
    them over too!    
"""


from xml.sax import ContentHandler, parse
from Interface import Interface






















class ISOXNode(Interface):

    """Object mapping from an XML element

        Objects implementing ISOXNode are used to construct object structures
        from XML elements.  Each node gets to control how its subnodes are
        created, and what will be passed back to its parent node once its
        element subtree is complete.  In the simplest possible case, one can
        create a simple DOM-like tree of nodes which closely resemble the
        original XML.  Or, one can create a tree of objects with only minor
        structural similarities, or even use nodes just to do "side-effect"
        processing guided by the XML structures, like an interpretive parser.
    """

    def _newNode(self,name,attributeMap):
        """Create new child node from 'name' and 'attributeMap'

           Child node must implement the 'ISOXNode' interface."""
           
    def _acquireFrom(self,parentNode):
        """Parent-child relationship hook

           Called on newly created nodes to give them a chance to acquire
           context information from their parent node"""
           
    def _addText(self,text):
        """Add text string 'text' to node"""

    def _addNode(self,subObj):
        """Add sub-node 'subObj' to node"""
        
    def _finish(self):
        """Return an object to be used in place of this node in call to the
            parent's '_addNode()' method.  Returning 'None' will result in
            nothing being added to the parent."""






class ObjectMakingHandler(ContentHandler):

    """SAX handler that makes a pseudo-DOM"""
    
    def __init__(self,documentRoot):
        self.stack = [documentRoot]
        ContentHandler.__init__(self)
        
    def startElement(self, name, atts):
        top = self.stack[-1]
        node = top._newNode(name,atts)
        node._acquireFrom(top)
        self.stack.append(node)

    def characters(self, ch):
        self.stack[-1]._addText(ch)

    def endElement(self, name):    
        stack = self.stack
        top = stack.pop()
        
        if top._name != name:
            raise SyntaxError,"End tag '%s' found when '%s' was wanted" % (name, top._name)
            
        out = top._finish()
        
        if out is not None:
            stack[-1]._addNode(name,out)

    def endDocument(self):
        self.document = self.stack[0]._finish()
        del self.stack









class Node:

    """Simple, DOM-like ISOXNode implementation"""
    
    __implements__ = ISOXNode
    
    def __init__(self,name='',atts={},**kw):
        self._name = name
        self._subNodes = []
        self._allNodes = []        
        d=self.__dict__
        for a in atts.keys():
            d[a]=atts[a]

        self.__dict__.update(kw)
        
    def _addNode(self,name,node):
        self._allNodes.append(node)
        self._subNodes.append(node)
        d=self.__dict__
        if not d.has_key(name): d[name]=[]
        d[name].append(node)

    def _newNode(self,name,atts):
        return self.__class__(name,atts)
        
    def _addText(self,text):
        self._allNodes.append(text)

    def _get(self,name):
        return self.__dict__.get(name,[])

    def _findFirst(self,name):
        d=self._get(name)
        if d: return d
        for n in self._subNodes:
            if hasattr(n,'_findFirst'):
                d = n._findFirst(name)
                if d: return d


    def _finish(self): return self

    _acquiredAttrs = ()

    def _acquireFrom(self,parentNode):
        d=self.__dict__
        have=d.has_key
        for k in self._acquiredAttrs:
            if not have(k): d[k]=getattr(parentNode,k)


class Document(Node):

    def _finish(self):
        self.documentElement = self._subNodes[0]
        return self
        
    def _newNode(self,name,atts):
        return Node(name,atts)



def load(filename_or_stream, documentObject=None):

    """Build a tree from a filename/stream, rooted in a document object"""
    
    if documentObject is None:
        documentObject = Document()
        
    handler = ObjectMakingHandler(documentObject)
    parse(filename_or_stream, handler)
    return handler.document


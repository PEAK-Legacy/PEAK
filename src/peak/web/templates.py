"""XML/XHTML Templates for 'peak.web', similar to Twisted's Woven

TODO

 - implement interaction wrapper for "/skin", "/request", etc. data paths

 - implement sub-template support (convert doc->DOMlet in another doc)

 - add hooks for DOMlets to validate the list of supplied parameters

 - 'list' DOMlet needs iteration variables, maybe paging

 - need translation DOMlets, among lots of other kinds of DOMlets

 - support DTD fragments, and the rest of the XML standard
"""

from __future__ import generators
from peak.api import *
from interfaces import *
from xml.sax.saxutils import quoteattr, escape
from publish import TraversalPath
from peak.util import SOX

__all__ = [
    'TEMPLATE_NS', 'DOMLETS_PROPERTY', 'TemplateDocument'
]

TEMPLATE_NS = 'http://peak.telecommunity.com/DOMlets/'
DOMLETS_PROPERTY = PropertyName('peak.web.DOMlets')

unicodeJoin = u''.join

def infiniter(sequence):
    while 1:
        for item in sequence:
            yield item




class DOMletState(binding.Component):

    """Execution state for a DOMlet"""

    protocols.advise(
        instancesProvide = [IDOMletState],
    )

    write = binding.Require("Unicode output stream write() method")


    def findState(self, iface):

        """Find nearest DOMletState implementing 'iface'"""

        for c in binding.iterParents(self):     # XXX not covered by tests!
            state = adapt(c,iface,None)
            if state is not None:
                return state






















class DOMletAsHTTP(binding.Component):

    """Render a template component"""

    protocols.advise(
        instancesProvide = [IHTTPHandler],
        asAdapterForProtocols = [IDOMletNode],
        factoryMethod = 'fromNode'
    )

    templateNode = binding.Require("""Node to render""")

    def fromNode(klass, subject):
        return klass(templateNode = subject)

    fromNode = classmethod(fromNode)

    def handle_http(self, ctx):
        ctx = ctx.parentContext()
        data = []
        self.templateNode.renderFor(
            ctx,
            DOMletState(ctx.current, write=data.append)
        )
        return '200 OK', [], [str(unicodeJoin(data))]    # XXX content-type
















def startElement(parser,data):
    parent = data['previous']['pwt.element']

    domlet = data.get('pwt.domlet')
    if domlet:
        factory = DOMLETS_PROPERTY.of(parent)[domlet]
    else:
        factory = parent.tagFactory

    param = data.get('pwt.define')

    data['pwt.element'] = element = factory(parent,
        tagName=data['name'],
        attribItems=data['attributes'],
        domletProperty = domlet or None,
        dataSpec  = data.get('pwt.data',''),
        paramName = param or None,
    )

    if param:
        parent.addParameter(param,element)


def finishElement(parser,data):
    return data['pwt.element']


def negotiateDomlet(parser, data, name, value):
    data['attributes'].remove((name,value))
    if ':' in value:
        data['pwt.domlet'],data['pwt.data'] = value.split(':',1)
    else:
        data['pwt.domlet'] = value


def negotiateDefine(parser, data, name, value):
    data['attributes'].remove((name,value))
    data['pwt.define'] = value



def setupElement(parser,data):
    d = dict(data.get('attributes',()))
    if 'domlet' in d:
        negotiateDomlet(parser,data,'domlet',d['domlet'])
    if 'define' in d:
        negotiateDefine(parser,data,'define',d['define'])

    def child(result):
        data['pwt.element'].addChild(result)

    def text(xml):
        top = data['pwt.element']
        top.addChild(top.textFactory(top,xml=escape(xml)))

    def literal(xml):
        top = data['pwt.element']
        top.addChild(top.literalFactory(top,xml=xml))

    data['start'] = startElement
    data['finish'] = finishElement
    data['child'] = child
    data['text'] = text
    data['literal'] = literal
    

def setupDocument(parser,data):
    setupElement(parser,data)
    data['pwt.element'] = TemplateDocument(data['parent'])













class Literal(binding.Component):

    """Simple static text node"""

    protocols.advise(
        classProvides = [IDOMletNodeFactory],
        instancesProvide = [IDOMletNode],
    )

    xml = u''

    staticText = binding.Obtain('xml')

    def renderFor(self, data, state):
        state.write(self.xml)


























class Element(binding.Component):

    protocols.advise(
        classProvides = [IDOMletElementFactory],
        instancesProvide = [IDOMletElement],
    )

    children       = binding.Make(list)
    params         = binding.Make(dict)

    tagName        = binding.Require("Tag name of element")
    attribItems    = binding.Require("Attribute name,value pairs")
    nonEmpty       = False
    domletProperty = None
    dataSpec       = binding.Make(lambda: '', adaptTo=TraversalPath)
    paramName      = None
    acceptParams   = binding.Obtain('domletProperty')

    # IDOMletNode

    def staticText(self):

        """Note: replace w/staticText = None in dynamic element subclasses"""

        texts = [child.staticText for child in self.optimizedChildren]

        if None in texts:
            return None

        if texts or self.nonEmpty:
            texts.insert(0, self._openTag)
            texts.append(self._closeTag)
            return unicodeJoin(texts)
        else:
            return self._emptyTag

    staticText = binding.Make(staticText, suggestParent=False)




    def optimizedChildren(self):

        """Child nodes with as many separate text nodes combined as possible"""

        all = []
        texts = []

        def flush():
            if texts:
                all.append(
                    self.literalFactory(self, xml=unicodeJoin(texts))
                )
                texts[:]=[]

        for child in self.children:
            t = child.staticText
            if t is None:
                flush()
                all.append(child)
            else:
                texts.append(t)

        flush()
        return all

    optimizedChildren = binding.Make(optimizedChildren)


    def _traverse(self, data, state):

        return self.dataSpec.traverse(
            data, lambda ctx: self._wrapInteraction(ctx)
        ), state








    def renderFor(self, data, state):

        text = self.staticText
        if text is not None:
            state.write(text)
            return

        if not self.optimizedChildren and not self.nonEmpty:
            state.write(self._emptyTag)
            return

        if self.dataSpec:
            data, state = self._traverse(data, state)

        state.write(self._openTag)

        for child in self.optimizedChildren:
            child.renderFor(data,state)

        state.write(self._closeTag)


    def addChild(self, node):
        """Add 'node' (an 'IDOMletNode') to element's direct children"""

        if self._hasBinding('optimizedChildren'):
            raise TypeError(
                "Attempt to add child after rendering", self, node
            )
        self.children.append(node)


    def addParameter(self, name, element):
        """Declare 'element' as part of parameter 'name'"""
        if self.acceptParams:
            self.params.setdefault(name,[]).append(element)
        else:
            self.getParentComponent().addParameter(name,element)



    # Override in subclasses

    def _wrapInteraction(self,interaction):
        # XXX This should wrap the interaction in an IWebTraversable simulator,
        # XXX which should include access to this element's parameters as well
        # XXX as interaction variables.
        raise NotImplementedError


    _emptyTag = binding.Make(
        lambda self: self._openTag[:-1]+u' />'
    )

    _closeTag = binding.Make(
        lambda self: u'</%s>' % self.tagName
    )

    _openTag = binding.Make(
        lambda self: u'<%s%s>' % ( self.tagName,
            unicodeJoin([
                u' %s=%s' % (k,quoteattr(v)) for (k,v) in self.attribItems
            ])
        )
    )

    tagFactory     = None # real value is set below
    textFactory    = Literal
    literalFactory = Literal

Element.tagFactory = Element











class TaglessElement(Element):

    """Element w/out tags"""

    _openTag = _closeTag = _emptyTag = ''


class TemplateDocument(TaglessElement):

    """Document-level template element"""

    acceptParams = True     # handle any top-level parameters





























class ContentReplacer(Element):

    """Abstract base for elements that replace their contents"""

    staticText = None
    children   = optimizedChildren = binding.Obtain('contents')
    contents   = binding.Require("nodes to render in element body")

    def addChild(self, node):
        pass    # ignore children, only parameters count with us


class Text(ContentReplacer):

    """Replace element contents w/data (XML-quoted)"""

    def renderFor(self, data, state):
        if self.dataSpec:
            data, state = self._traverse(data, state)

        write = state.write
        write(self._openTag)
        write(escape(unicode(data.current)))
        write(self._closeTag)


class XML(ContentReplacer):

    """Replace element contents w/data (XML structure)"""

    def renderFor(self, data, state):
        if self.dataSpec:
            data, state = self._traverse(data, state)

        write = state.write
        write(self._openTag)
        write(unicode(data.current))
        write(self._closeTag)



class TaglessText(Text):

    """Text w/out open/close tag"""

    _openTag = _closeTag = _emptyTag = ''


class TaglessXML(XML):

    """XML w/out open/close tag"""

    _openTag = _closeTag = _emptyTag = ''





























class URLAttribute(Element):

    """Put the URL in an attribute"""

    staticText = None

    def renderFor(self, data, state):

        if self.dataSpec:
            data, state = self._traverse(data, state)

        url = unicode(data.absoluteURL)

        if not self.optimizedChildren and not self.nonEmpty:
            state.write(self._emptyTag % locals())
            return

        state.write(self._openTag % locals())
        for child in self.optimizedChildren:
            child.renderFor(data,state)
        state.write(self._closeTag)


class URLText(ContentReplacer):

    """Write absolute URL as body text"""

    def renderFor(self, data, state):

        if self.dataSpec:
            data, state = self._traverse(data, state)

        write = state.write

        write(self._openTag)
        write(unicode(data.absoluteURL))
        write(self._closeTag)




def URLTag(parentComponent, componentName=None, domletProperty=None, **kw):

    """Create a URLText or URLAttribute DOMlet based on parameters"""

    kw['domletProperty'] = domletProperty
    prop = (domletProperty or '').split('.')

    if len(prop)==1 or prop[-1]=='text':
        return URLText(parentComponent, componentName, **kw)

    elif prop[-1]=='notag':
        kw['_openTag'] = kw['_closeTag'] = ''
        return URLText(parentComponent, componentName, **kw)

    else:
        attrName = prop[-1].replace('+',':')
        attrs = [(k,v.replace('%','%%')) for (k,v) in kw.get('attribItems',())]
        d = dict(attrs)

        if attrName not in d:
            attrs.append((attrName,'%(url)s'))
        else:
            attrs = [
                tuple([k]+((k!=attrName) and [v] or ['%(url)s']))
                    for (k,v) in attrs
            ]

        kw['attribItems'] = attrs
        return URLAttribute(parentComponent, componentName, **kw)

protocols.adviseObject(URLTag, provides=[IDOMletElementFactory])










class List(ContentReplacer):

    def renderFor(self, data, state):

        if self.dataSpec:
            data, state = self._traverse(data, state)

        state.write(self._openTag)

        nextPattern = infiniter(self.params['listItem']).next
        allowed     = data.allows
        ct = 0

        # XXX this should probably use an iteration location, or maybe
        # XXX put some properties in execution context for loop vars?

        for item in data.current:

            if not allowed(item):
                continue

            if not ct:
                for child in self.params.get('header',()):
                    child.renderFor(data,state)

            loc = data.childContext(str(ct), item)
            nextPattern().renderFor(loc, state)
            ct += 1

        if not ct:
            # Handle list being empty
            for child in self.params.get('emptyList',()):
                child.renderFor(data, state)
        else:
            for child in self.params.get('footer',()):
                child.renderFor(data,state)

        state.write(self._closeTag)




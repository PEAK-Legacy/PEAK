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
from environ import getAbsoluteURL, getInteraction, getCurrent
from environ import childContext, parentContext
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

    def fromNode(klass, subject, protocol):
        return klass(templateNode = subject)

    fromNode = classmethod(fromNode)

    def handle_http(self, environ, input, errors):
        myOwner = parentContext(environ)

        data = []

        self.templateNode.renderFor(
            myOwner,
            DOMletState(myOwner, write=data.append)
        )

        return '200 OK', [], [unicodeJoin(data)]    # XXX content-type













class ElementAsBuilder(protocols.Adapter):

    protocols.advise(
        instancesProvide = [SOX.IXMLBuilder],
        asAdapterForProtocols=[IDOMletElement]
    )

    def _xml_newTag(self, name,attrs,stack,parser):
        self.nsUri = parser.nsInfo
        myNs = self.myNs or ('',)   # use unprefixed NS if no NS defined
        top = self.subject
        factory = top.tagFactory
        domletName = dataSpec = paramName = None
        a = []; append = a.append

        for k,v in attrs:

            if ':' in k:
                ns, n = k.split(':',1)
            else:
                ns, n = '', k

            if n=='domlet' and ns in myNs:
                # XXX if domletName is not None or dataSpec is not None:
                # XXX     raise ???
                if ':' in v:
                    domletName, dataSpec = v.split(':',1)
                else:
                    domletName, dataSpec = v, ''

                if domletName:
                    factory = DOMLETS_PROPERTY.of(top)[domletName]
                    factory = adapt(factory, IDOMletElementFactory)

            elif n=='define' and ns in myNs:
                # XXX if paramName is not None:
                # XXX     raise ???
                paramName = v
            else:
                append((k,v))

        element = factory(top, tagName=name, attribItems=a,
            domletProperty = domletName or None, dataSpec  = dataSpec or '',
            paramName = paramName or None,
        )

        if paramName:
            top.addParameter(paramName,element)

        return element


    def _xml_addChild(self,data):
        self.subject.addChild(data)

    def _xml_finish(self):
        return self.subject

    def _xml_addText(self,xml):
        top = self.subject
        top.addChild(top.textFactory(top,xml=escape(xml)))

    def _xml_addLiteral(xml):
        top = self.subject
        top.addChild(top.literalFactory(top,xml=xml))


    myNs = binding.Make(        # prefixes that currently map to TEMPLATE_NS
        lambda self: dict(
            [(p,1) for (p,u) in self.nsUri.items() if u and u[-1]==TEMPLATE_NS]
        ),
        attrName = 'myNs'
    )









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

    parserClass = SOX.ExpatBuilder

    acceptParams = True     # handle any top-level parameters

    def parseFile(self, stream):
        self.parserClass().parseFile(stream,self)
























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
        write(escape(unicode(getCurrent(data))))
        write(self._closeTag)


class XML(ContentReplacer):

    """Replace element contents w/data (XML structure)"""

    def renderFor(self, data, state):
        if self.dataSpec:
            data, state = self._traverse(data, state)

        write = state.write
        write(self._openTag)
        write(unicode(getCurrent(data)))
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

        url = unicode(getAbsoluteURL(data))

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
        write(unicode(getAbsoluteURL(data)))
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
        allowed     = getInteraction(data).allows
        ct = 0

        # XXX this should probably use an iteration location, or maybe
        # XXX put some properties in execution context for loop vars?

        for item in getCurrent(data):

            if not allowed(item):
                continue

            if not ct:
                for child in self.params.get('header',()):
                    child.renderFor(data,state)

            loc = childContext(data, str(ct), item)
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




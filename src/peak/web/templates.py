"""XML/XHTML Templates for 'peak.web', similar to Twisted's Woven

TODO

 - Address traversal nesting for referenced data
 
 - Dynamic attributes, independent of element?

 - Phase out old PWT syntax
 
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
















def startElement(parser,data):

    parent = data['previous']['pwt.content']
    factory = data.get('this.factory', parent.tagFactory)

    data['pwt.content'] = outer = factory(parent,
        tagName=data['name'],
        attribItems=data['attributes'],
        domletProperty = data.get('this.domlet'),
        dataSpec  = data.get('this.data',''),
        paramName = data.get('this.is'),
    )

    inner = data.get('content.factory')
    if inner:
        data['pwt.this'] = outer
        data['pwt.content'] = inner(outer,
            tagName='',
            attribItems=[],
            domletProperty = data.get('content.domlet'),
            dataSpec=data.get('content.data',''),
            paramName = data.get('content.is'),
        )
        

def finishElement(parser,data):    
    content = data['pwt.content']
    for f in data.get('content.register',()):
        f(content)
    if 'pwt.this' in data:
        this = data['pwt.this']
        this.addChild(content)
    else:
        this = content        
    for f in data.get('this.register',()):
        f(this)
    if 'previous' in data:
        data['previous']['pwt.content'].addChild(this)
    return this


def negotiateDomlet(parser, data, name, value):
    data['attributes'].remove((name,value))
    if ':' in value:
        data['this.domlet'],data['this.data'] = value.split(':',1)
        domlet = data['this.domlet']
    else:
        data['this.domlet'] = domlet = value

    factory = DOMLETS_PROPERTY.of(data['previous']['pwt.content'])[domlet]
    if data.setdefault('this.factory',factory) is not factory: 
        parser.err('More than one "domlet" or "this:" replacement defined')


def negotiateDefine(parser, data, name, value):
    data['attributes'].remove((name,value))
    data['this.is'] = value
    parent = data['previous']['pwt.content']
    data.setdefault('this.register',[]).append(
        lambda ob: parent.addParameter(value,ob)
    )


def negotiatorFactory(domletFactory):
    def negotiate(mode, parser, data, name, value):
        data['attributes'].remove((name,value))
        factory = data.setdefault(mode+'.factory',domletFactory)
        if factory is not domletFactory:
            parser.err('More than one "domlet" or "this:" replacement defined')
        data[mode+'.data'] = value
        data[mode+'.domlet'] = parser.splitName(name)[1]
    return negotiate

def nodeIs(mode, parser, data, name, value):
    data['attributes'].remove((name,value))
    data[mode+'.is'] = value
    parent = data['previous']['pwt.content']
    data.setdefault(mode+'.register',[]).append(
        lambda ob: parent.addParameter(value,ob)
    )


def setupElement(parser,data):

    d = dict(data.get('attributes',()))

    if 'domlet' in d:
        negotiateDomlet(parser,data,'domlet',d['domlet'])

    if 'define' in d:
        negotiateDefine(parser,data,'define',d['define'])

    def text(xml):
        top = data['pwt.content']
        top.addChild(top.textFactory(top,xml=escape(xml)))

    def literal(xml):
        top = data['pwt.content']
        top.addChild(top.literalFactory(top,xml=xml))

    data['start'] = startElement
    data['finish'] = finishElement
    data['text'] = text
    data['literal'] = literal
    

def setupDocument(parser,data):
    setupElement(parser,data)
    data['pwt.content'] = data['pwt_document']














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
        return self.dataSpec.traverse(data), state











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

    _emptyTag = binding.Make(
        lambda self: self.tagName and self._openTag[:-1]+u' />' or ''
    )

    _closeTag = binding.Make(
        lambda self: self.tagName and u'</%s>' % self.tagName or ''
    )

    _openTag = binding.Make(
        lambda self: self.tagName and u'<%s%s>' % ( self.tagName,
            unicodeJoin([
                u' %s=%s' % (k,quoteattr(v)) for (k,v) in self.attribItems
            ])
        ) or ''
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

    protocols.advise(
        instancesProvide = [IHTTPHandler],
        classProvides = [naming.IObjectFactory],
    )

    security.allow(security.Anybody)

    acceptParams = True     # handle any top-level parameters


    def renderFor(self, ctx, state):
        return super(TemplateDocument,self).renderFor(ctx.parentContext(),state)


    def handle_http(self, ctx):
        name = ctx.shift()
        if name is not None:
            raise web.NotFound(ctx,name,self)   # No traversal to subobjects!
        data = []
        self.renderFor(
            ctx, DOMletState(self, write=data.append)
        )
        # XXX set content-type header
        return '200 OK', [], [str(unicodeJoin(data))]    # XXX encoding


    def getObjectInstance(klass, context, refInfo, name, attrs=None):
        #print "loading template"; import pdb; pdb.set_trace()
        url, = refInfo.addresses
        return config.processXML(
            web.TEMPLATE_SCHEMA(context),str(url),pwt_document=klass(context),
        )

    getObjectInstance = classmethod(getObjectInstance)



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

        url = unicode(data.url)

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
        write(unicode(data.url))
        write(self._closeTag)

class TaglessURLText(URLText):
    _openTag = _closeTag = _emptyTag = ''

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

class TaglessList(List):
    _openTag = _closeTag = _emptyTag = ''


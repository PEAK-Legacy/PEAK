"""XML/XHTML Templates for 'peak.web', similar to Twisted's Woven

TODO

 - implement interaction wrapper for "/skin", "/request", etc. model paths

 - implement sub-template support (convert template->view in another template)

 - add hooks for views to validate the list of supplied patterns

 - 'list' view needs iteration variables, maybe paging

 - need translation views, among lots of other kinds of views

 - support DTD fragments, and the rest of the XML standard
"""

from __future__ import generators
from peak.api import *
from interfaces import *
from xml.sax.saxutils import quoteattr, escape
from publish import LocationPath

__all__ = [
    'TEMPLATE_NS', 'VIEWS_PROPERTY', 'TemplateParser', 'TemplateDocument'
]

TEMPLATE_NS = 'http://peak.telecommunity.com/peak.web.templates/'
VIEWS_PROPERTY = PropertyName('peak.web.views')

unicodeJoin = u''.join

def infiniter(sequence):
    while 1:
        for item in sequence:
            yield item

def isNull(ob):
    return ob is NOT_FOUND or ob is NOT_ALLOWED


class TemplateAsMethod(binding.Component):

    """Render a template component"""

    protocols.advise(
        instancesProvide = [IWebMethod],
        asAdapterForProtocols = [ITemplateNode],
        factoryMethod = 'fromNode'
    )

    templateNode = binding.requireBinding("""Node to render""")

    def fromNode(klass, subject, protocol):
        return klass(templateNode = subject)

    fromNode = classmethod(fromNode)

    def render(self, interaction):
        myLocation = self.getParentComponent()
        myOwner = myLocation.getParentComponent()
        data = []
        self.templateNode.renderTo(
            interaction, data.append, myOwner, interaction
        )
        return unicodeJoin(data)
















class TemplateParser(binding.Component):

    """Parser that assembles a TemplateDocument"""

    def parser(self,d,a):

        from xml.parsers.expat import ParserCreate
        p = ParserCreate()

        p.ordered_attributes = True
        p.returns_unicode = True
        p.specified_attributes = True

        p.StartDoctypeDeclHandler = self.startDoctype
        p.StartElementHandler = self.startElement
        p.EndElementHandler = self.endElement
        p.CharacterDataHandler = self.characters
        p.StartNamespaceDeclHandler = self.startNS
        p.EndNamespaceDeclHandler = self.endNS
        p.CommentHandler = self.comment

        # We don't use:
        # .XmlDeclHandler(version, encoding, standalone)
        # .ElementDeclHandler(name, model)
        # .AttlistDeclHandler(elname, attname, type, default, required)
        # .EndDoctypeDeclHandler()
        # .ProcessingInstructionHandler(target, data)
        # .UnparsedEntityDeclHandler(entityN,base,systemId,publicId,notationN)
        # .EntityDeclHandler(
        #      entityName, is_parameter_entity, value, base,
        #      systemId, publicId, notationName)
        # .NotationDeclHandler(notationName, base, systemId, publicId)
        # .StartCdataSectionHandler()
        # .EndCdataSectionHandler()
        # .NotStandaloneHandler()
        return p

    parser = binding.Once(parser)



    views = binding.New(list)
    stack = binding.New(list)
    nsUri = binding.New(dict)
    myNs  = binding.New(dict)

    myNs = binding.Once(
        lambda self,d,a: dict(
            [(p,1) for (p,u) in self.nsUri.items() if u and u[-1]==TEMPLATE_NS]
        )
    )


    def parseFile(self, stream, document=None):
        if document is None:
            document = TemplateDocument(self.getParentComponent())
        self.stack.append(document)
        self.views.append(document)
        self.parser.ParseFile(stream)


    def comment(self,data):
        self.buildLiteral(u'<!--%s-->' % data)


    def startNS(self, prefix, uri):
        self.nsUri.setdefault(prefix,[]).append(uri)
        if uri==TEMPLATE_NS:
            self._delBinding('myNs')


    def endNS(self, prefix):
        uri = self.nsUri[prefix].pop()
        if uri==TEMPLATE_NS:
            self._delBinding('myNs')







    def startElement(self, name, attrs):

        a = []
        append = a.append
        myNs = self.myNs

        top = self.stack[-1]
        factory = top.tagFactory
        model = ''
        view = pattern = None

        for i in range(0,len(attrs),2):
            k,v = attrs[i], attrs[i+1]
            if ':' in k:
                ns, n = k.split(':',1)
            else:
                ns, n = '', k

            if myNs:
                if ns not in myNs:
                    append((k,v))
                    continue
            elif ns:
                append((k,v))
                continue

            if k=='view':
                view = v
                factory = VIEWS_PROPERTY.of(top)[v]
                factory = adapt(factory, ITemplateElementFactory)
                continue
            elif k=='model':
                model = v
                continue
            elif k=='pattern':
                pattern = v
                continue

            append((k,v))
            continue

        tag = factory(top, tagName=name, attribItems=a,
            # XXX nonEmpty=False,
            viewProperty=view, modelPath=model, patternName=pattern
        )

        if pattern:
            self.views[-1].addPattern(pattern,tag)

        if view:
            # New view, put it on the view stack
            self.views.append(tag)
        else:
            # Duplicate the old view
            self.views.append(self.views[-1])

        self.stack.append(tag)


    def endElement(self, name):
        self.views.pop()
        last = self.stack.pop()
        self.stack[-1].addChild(last)


    def buildLiteral(self,xml):
        top = self.stack[-1]
        literal = top.literalFactory(top, xml=xml)
        top.addChild(literal)


    def characters(self, data):
        top = self.stack[-1]
        text = top.textFactory(top, xml=escape(data))
        top.addChild(text)







    def startDoctype(self, doctypeName, systemId, publicId, has_internal):

        if publicId:
            p = ' PUBLIC %s %s' % (quoteattr(publicId),quoteattr(systemId))
        elif systemId:
            p = ' SYSTEM %s' % quoteattr(systemId)
        else:
            p = ''

        # we ignore internal DTD subsets; they're not useful for HTML
        xml = u'<!DOCTYPE %s%s>\n' % (doctypeName, p)

        self.buildLiteral(xml)




























class TemplateLiteral(binding.Component):

    """Simple static text node"""

    protocols.advise(
        classProvides = [ITemplateNodeFactory],
        instancesProvide = [ITemplateNode],
    )

    xml = u''

    staticText = binding.bindTo('xml')

    def renderTo(self, interaction, writeFunc, currentModel, executionContext):
        writeFunc(self.xml)


























class TemplateElement(binding.Component):

    protocols.advise(
        classProvides = [ITemplateElementFactory],
        instancesProvide = [ITemplateElement],
    )

    children   = binding.New(list)
    patternMap = binding.New(dict)

    tagName      = binding.requireBinding("Tag name of element")
    attribItems  = binding.requireBinding("Attribute name,value pairs")
    nonEmpty     = False
    viewProperty = None
    modelPath    = binding.Constant('', adaptTo=LocationPath)
    patternName  = None

    # ITemplateNode

    def staticText(self, d, a):

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

    staticText = binding.Once(staticText, suggestParent=False)





    def optimizedChildren(self, d, a):

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

    optimizedChildren = binding.Once(optimizedChildren)


    def _getSubModel(self, interaction, currentModel):

        if isNull(currentModel):
            return currentModel

        return self.modelPath.traverse(
            currentModel, interaction, lambda o,i: self._wrapInteraction(i)
        )





    def renderTo(self, interaction, writeFunc, currentModel, executionContext):

        text = self.staticText
        if text is not None:
            writeFunc(text)
            return

        if self.modelPath:
            currentModel = self._getSubModel(interaction, currentModel)

        if not self.optimizedChildren and not self.nonEmpty:
            self._renderEmpty(
                interaction, writeFunc, currentModel, executionContext
            )
            return

        self._open(interaction, writeFunc, currentModel, executionContext)
        for child in self.optimizedChildren:
            child.renderTo(
                interaction, writeFunc, currentModel, executionContext
            )
        writeFunc(self._closeTag)


    def addChild(self, node):
        """Add 'node' (an 'ITemplateNode') to element's direct children"""

        if self._hasBinding('optimizedChildren'):
            raise TypeError(
                "Attempt to add child after rendering", self, node
            )
        self.children.append(node)


    def addPattern(self, name, element):
        """Declare 'element' as part of pattern 'name'"""

        # self.patterns.append( (name,element) )
        self.patternMap.setdefault(name,[]).append(element)


    # Override in subclasses

    def _open(self, interaction, writeFunc, currentModel, executionContext):
        writeFunc(self._openTag)

    def _renderEmpty(self,
        interaction, writeFunc, currentModel, executionContext
    ):
        writeFunc(self._emptyTag)


    def _wrapInteraction(self,interaction):
        # XXX This should wrap the interaction in an IWebLocation simulator,
        # XXX which should include access to this element's patterns as well
        # XXX as interaction variables.
        raise NotImplementedError


    _emptyTag = binding.Once(
        lambda self,d,a: self._openTag[:-1]+u' />'
    )

    _closeTag = binding.Once(
        lambda self,d,a: u'</%s>' % self.tagName
    )

    _openTag = binding.Once(
        lambda self,d,a: u'<%s%s>' % ( self.tagName,
            unicodeJoin([
                u' %s=%s' % (k,quoteattr(v)) for (k,v) in self.attribItems
            ])
        )
    )

    tagFactory     = None # real value is set below
    textFactory    = TemplateLiteral
    literalFactory = TemplateLiteral

TemplateElement.tagFactory = TemplateElement


class TemplateDocument(TemplateElement):

    """Document-level template element"""

    _openTag = _closeTag = _emptyTag = ''

    parserClass = TemplateParser

    def parseFile(self, stream):
        parser = self.parserClass(self)
        parser.parseFile(stream,self)






























class TemplateReplacement(TemplateElement):

    """Abstract base for elements that replace their contents"""

    staticText = None
    children   = optimizedChildren = binding.bindTo('contents')
    contents   = binding.requireBinding("nodes to render in element body")

    def addChild(self, node):
        pass    # ignore children, only patterns count with us


class TemplateText(TemplateReplacement):

    """Replace element contents w/model"""

    def renderTo(self, interaction, writeFunc, currentModel, executionContext):

        if self.modelPath:
            currentModel = self._getSubModel(interaction, currentModel)

        writeFunc(self._openTag)

        if not isNull(currentModel):
            writeFunc(unicode(currentModel.getObject()))

        writeFunc(self._closeTag)














class TemplateList(TemplateReplacement):

    def renderTo(self, interaction, writeFunc, currentModel, executionContext):

        if self.modelPath:
            currentModel = self._getSubModel(interaction, currentModel)

        writeFunc(self._openTag)

        i = infiniter(self.patternMap['listItem'])
        locationProtocol = interaction.locationProtocol
        ct = 0

        if not isNull(currentModel):

            for item in currentModel.getObject():
                if not interaction.allows(item):
                    continue

                loc = adapt(item, locationProtocol, None)
                if loc is None:
                    continue

                # XXX this should probably use an iteration location, or maybe
                # XXX put some properties in execution context for loop vars?

                i.next().renderTo(
                    interaction, writeFunc, loc, executionContext
                )
                ct += 1

        if not ct:
            # Handle list being empty
            for child in self.patternMap.get('emptyList',()):
                child.renderTo(
                    interaction, writeFunc, currentModel, executionContext
                )

        writeFunc(self._closeTag)


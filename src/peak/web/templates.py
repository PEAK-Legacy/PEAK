from __future__ import generators
from peak.api import *
from interfaces import *
from xml.sax.saxutils import quoteattr
from publish import LocationPath

__all__ = [
    # really only the parser, bindings, etc. should be public
]


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
        data = []
        self.templateNode.renderTo(
            interaction, data.append, self.getParentComponent(), interaction
        )
        return unicodeJoin(data)


















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
    paterns    = binding.New(list)
    patternMap = binding.New(dict)

    tagName      = binding.requireBinding("Tag name of element")
    attribItems  = binding.requireBinding("Attribute name,value pairs")
    nonEmpty     = False
    viewProperty = None
    modelPath    = binding.Constant(None, adaptTo=LocationPath)
    patternName  = None

    # ITemplateNode

    def staticText(self, d, a):

        """Note: replace w/staticText = None in dynamic element subclasses"""

        texts = [child.staticText for child in self.optimizedChildren]

        if None in texts or self.isDynamic:
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

        self.patterns.append( (name,element) )
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

    tagFactory     = classAttr(binding.bindTo('TemplateElement'))
    textFactory    = TemplateLiteral
    literalFactory = TemplateLiteral




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


from peak.api import *
from interfaces import *
from xml.sax.saxutils import quoteattr

__all__ = [
    'TemplateLiteral', 'TemplateElement',
]

unicodeJoin = u''.join


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
    isDynamic  = False   # Set in subclasses to force dynamic rendering

    tagName      = binding.requireBinding("Tag name of element")
    attribItems  = binding.requireBinding("Attribute name,value pairs")
    nonEmpty     = False
    viewProperty = None
    modelPath    = None
    patternName  = None

    # ITemplateNode

    def staticText(self, d, a):

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




    def _getSubModel(self, interaction, currentModel):

        path = iter(self.modelPath)
        part = path.next()

        if not part:
            currentModel = self._wrapInteraction(interaction)
        else:
            # reset to beginning
            path = iter(self.modelPath)

        for part in path:
            if part == '..':
                currentModel = binding.getParentComponent(currentModel)
            elif part=='.':
                pass
            else:
                currentModel = currentModel.getSublocation(
                    part, interaction
                )
            if (currentModel is None or currentModel is NOT_FOUND
                or currentModel is NOT_ALLOWED
            ):  break

        return currentModel
















"""Template tests

TODO

 - Mixed namespaces

 - DOMlet property redefinition within a component

 - Security used

 - DOCTYPE
"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from cStringIO import StringIO
import peak.web.templates as pwt
from urllib import quote

class TestApp(web.Location):

    security.allow(
        foo = security.Anybody,
        bar = security.Anybody,
        someXML = security.Anybody,
        baz = security.Nobody,
    )

    foo = "The title (with <xml/> & such in it)"
    baz = "can't touch this!"
    bar = 1,2,3

    someXML = "<li>This has &lt;xml/&gt; in it</li>"

    show = binding.Require(
        "Template to dump this out with",
        permissionNeeded = security.Anybody
    )


class BasicTest(TestCase):

    template = "pkgfile:peak.web.tests/template1.pwt"

    rendered = """<html><head>
<title>Template test: The title (with &lt;xml/&gt; &amp; such in it)</title>
</head>
<body>
<h1>The title (with &lt;xml/&gt; &amp; such in it)</h1>
<ul><li>1</li><li>2</li><li>3</li></ul>
<ul><li>This has &lt;xml/&gt; in it</li></ul>
<ul><li>This has &lt;xml/&gt; in it</li></ul>
</body></html>
"""

    def setUp(self):
        r = testRoot()
        app = TestApp(r, show = self.mkTemplate())
        self.policy = web.TestPolicy(app)

    def mkTemplate(self):
        return config.processXML(
            web.TEMPLATE_SCHEMA(testRoot()), self.template,
            pwt_document=web.TemplateDocument(testRoot())
        )

    def render(self):
        return self.policy.simpleTraverse('show')

    def testRendering(self):
        self.assertEqual(self.render(),self.rendered)










class NSTest(BasicTest):

    template = "data:,"+quote("""<body>
<h1 content:replace="foo">Title Goes Here</h1>
<ul content:list="bar">
    <li this:is="listItem" content:replace="."></li>
</ul>
</body>""")

    rendered = """<body>
<h1>The title (with &lt;xml/&gt; &amp; such in it)</h1>
<ul><li>1</li><li>2</li><li>3</li></ul>
</body>"""


class NSTest2(NSTest):

    template = "data:,"+quote("""<body>
<h1 content:replace="foo">Title Goes Here</h1>
<ul><div this:list="bar">
    <li this:is="listItem"><span this:replace=".">foo</span></li>
</div></ul>
</body>""")

class ListHeaderFooterTest(BasicTest):
    template = "data:,"+quote("""<ul content:list="bar"
    ><li this:is="header">Header</li><li this:is="listItem" content:replace="."
    ></li><li this:is="footer">Footer</li></ul>""")

    rendered = "<ul><li>Header</li><li>1</li><li>2</li><li>3</li>" \
               "<li>Footer</li></ul>"










class MiscTests(TestCase):

    def setUp(self):
        self.app = TestApp(testRoot())
        self.policy = web.TestPolicy(self.app)
        self.ctx = self.policy.newContext()

    def testParameters(self):

        class MockTemplate:
            protocols.advise(instancesProvide=[web.IDOMletRenderable])
            renderCt = 0
            def renderFor(_self,ctx,state):
                self.assert_(ctx is self.ctx)
                self.assertEqual(state,123)
                _self.renderCt+=1

        t = MockTemplate()
        p = pwt.Parameters(self.ctx,{'t':t, 'p':u'bar', 'd':123})
        ctx = self.ctx.childContext('xyz',p)
        c2 = ctx.traverseName('t')

        # Test a second time to ensure that result is cached
        c2 = ctx.traverseName('t')

        # It should render with the original context
        c2.current.renderFor(c2,123)

        # and the mock 'renderFor' should have been called exactly once:
        self.assertEqual(t.renderCt, 1)

        # Paths should be traversed from the start point
        c2 = ctx.traverseName('p')
        self.assertEqual(c2.current, (1,2,3))
        
        # And data should just be returned
        c2 = ctx.traverseName('d')
        self.assertEqual(c2.current, (123))



class ParserTests(TestCase):

    def setUp(self,**kw):
        self.xml_parser = config.XMLParser(
            web.TEMPLATE_SCHEMA(testRoot()),
            pwt_document = web.TemplateDocument(testRoot()),
            **kw
        )
        self.parse = self.xml_parser.parse
        self.nparser = nparser = self.xml_parser.makeParser()
        self.startElement = nparser.startElement
        self.endElement = nparser.endElement
        nparser._beforeParsing(self.xml_parser.parseFunctions())
        self.finish = nparser._afterParsing
        self.policy = web.TestPolicy(TestApp(testRoot()))

    def testInvalidArgs(self):
        self.startElement('ul',['content:list','bar'])

        # Unrecognized argument for 'list'
        self.startElement('li',['this:is','invalid'])
        self.assertRaises(SyntaxError,self.endElement)

        # Multiple 'header' definitions
        self.startElement('li',['this:is','header'])
        self.endElement()
        self.startElement('li',['this:is','header'])
        self.assertRaises(SyntaxError,self.endElement)


TestClasses = (
    MiscTests, ParserTests, BasicTest, NSTest, NSTest2, ListHeaderFooterTest
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])






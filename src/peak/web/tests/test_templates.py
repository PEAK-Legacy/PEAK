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
    ParserTests, BasicTest, NSTest, NSTest2, ListHeaderFooterTest
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])






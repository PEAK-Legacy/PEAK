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

class TestApp(web.Traversable):

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


TestClasses = (
    BasicTest, NSTest, NSTest2
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])











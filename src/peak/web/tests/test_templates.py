"""Template tests

TODO

 - Mixed namespaces

 - View property redefinition within a component

 - Security used

 - DOCTYPE
"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from cStringIO import StringIO


class TestApp(web.SimpleLocation):

    security.allow(
        foo = [security.Anybody],
        bar = [security.Anybody],
        show = [security.Anybody],
    )

    foo = "The title"

    bar = 1,2,3

    show = binding.requireBinding("Template to dump this out with")









class BasicTest(TestCase):

    template = """<body>
<h1 model="foo" view="text">Title Goes Here</h1>
<ul model="bar" view="list">
    <li pattern="listItem" view="text"></li>
</ul>
</body>"""

    rendered = """<body>
<h1>The title</h1>
<ul><li>1</li><li>2</li><li>3</li></ul>
</body>"""

    def setUp(self):
        r = testRoot()
        self.app = TestApp(r, show = self.mkTemplate())
        self.interaction = web.Interaction(r, app = self.app)

    def mkTemplate(self):
        d = web.TemplateDocument(testRoot())
        d.parseFile(StringIO(self.template))
        return d

    def render(self):
        meth = web.LocationPath('show').traverse(
            self.interaction.root, self.interaction
        )
        return self.interaction.callObject(None, meth)


    def checkRendering(self):
        assert self.render() == self.rendered








TestClasses = (
    BasicTest,
)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])




































from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

from test_templates import TestApp, BasicTest

class ResourceApp1(TestApp):

    # This makes all 'peak.*' package resources available for testing;
    # Ordinarily, you'd do this via a config file, but this is quick and easy

    __makePkgAvailable = binding.Make(lambda: True,
        offerAs = ['peak.web.resource_packages.peak.*']
    )

    show = web.bindResource('template1')

class MethodTest1(BasicTest):

    appClass = ResourceApp1

    def setUp(self):
        r = testRoot()
        self.policy = web.TestPolicy(self.appClass(r))

















class ResourceApp2(ResourceApp1):

    show = web.bindResource('template2')

    xml = web.bindResource(
        '/peak.running/EventDriven', permissionNeeded=security.Anybody
    )

class MethodTest2(MethodTest1):
    appClass = ResourceApp2

    rendered = """<body>
<h1>The title (with &lt;xml/&gt; &amp; such in it)</h1>

<ul><li>1</li><li>2</li><li>3</li></ul>

<a href="http://127.0.0.1/++resources++/peak.running/EventDriven.xml">
The EventDriven.xml file, found at
http://127.0.0.1/++resources++/peak.running/EventDriven.xml
</a>

</body>
"""


















class LocationTests(TestCase):

    def setUp(self):
        self.root = web.Location(testRoot())
        self.policy = web.TestPolicy(self.root)
        self.ctx = self.policy.newContext()

    def testBasics(self):
        self.failUnless(web.IConfigurableLocation(self.root) is self.root)
        self.assertEqual(self.root.place_url, '')

    def testContainers(self):
        c1 = {'bar':'baz'}; c2={'foo':'bar'}
        self.assertEqual(self.ctx.traverseName('foo',None), None)
        self.assertEqual(self.ctx.traverseName('bar',None), None)
        self.root.addContainer(c1,security.Nobody)
        self.assertEqual(self.ctx.traverseName('foo',None), None)
        self.assertEqual(self.ctx.traverseName('bar',None), None)
        self.root.addContainer(c2)
        self.assertEqual(self.ctx.traverseName('foo',None).current, 'bar')
        self.assertEqual(self.ctx.traverseName('bar',None), None)
        self.root.addContainer(c1,security.Anybody)
        self.assertEqual(self.ctx.traverseName('foo',None).current, 'bar')
        self.assertEqual(self.ctx.traverseName('bar',None).current, 'baz')

    def testOffers(self):
        self.root.addContainer({'bar':'baz'})
        self.root.registerLocation('test.1','bar')
        self.assertEqual(
            self.ctx.traverseName('++id++test.1',None).current,'baz'
        )
        self.root.registerLocation('test2','.')
        self.failUnless(self.ctx.traverseName('++id++test2') is self.ctx)

    def testAppViews(self):
        self.checkView(self.root,int,123)
        self.checkView(self.root,protocols.IOpenProtocol,web.IWebTraversable)




    def checkView(self,loc,tgt,src):
        bar_handler = lambda ctx,o,ns,nm,qn,d: ctx.childContext(qn,"baz")
        loc.registerView(tgt,'bar',bar_handler)
        loc.addContainer({'foo':src})
        ctx = web.TraversalPath('foo/@@bar').traverse(
            self.ctx.clone(current=loc)
        )
        self.assertEqual(ctx.current,'baz')
        
    def testNestedViews(self):
        loc = web.Location(self.root)
        self.checkView(loc,int,123)
        self.checkView(loc,protocols.IOpenProtocol,web.IWebTraversable)




























class ResourceTests(TestCase):

    def testSubObjectRejection(self):
        # Files and templates shouldn't allow subitems in PATH_INFO
        paths = 'peak.web/resource_defaults.ini', 'peak.web.tests/template1'
        policy = web.TestPolicy(ResourceApp1(testRoot()))
        for path in paths:
            try:
                policy.simpleTraverse('/++resources++/%s/subitem' % path, True)
            except web.NotFound,v:
                self.assertEqual(v.args[0], "subitem")
            else:
                raise AssertionError("Should have raised NotFound:", path)

    def testURLcalculations(self):

        # Root locations: direct children of a non-IPlace parent
        r=web.Resource(testRoot())
        self.assertEqual(r.place_url,'')
        r=web.Resource(testRoot(),'foo')
        self.assertEqual(r.place_url,'')

        # Skin path is resource prefix
        policy = web.TestPolicy(ResourceApp1(testRoot()))
        ctx = policy.simpleTraverse('/++resources++', False)
        self.assertEqual(ctx.current.place_url, '++resources++')

        # Skin children should include resource prefix
        ctx2 = ctx.traverseName('peak.web')
        self.assertEqual(ctx2.current.place_url, '++resources++/peak.web')

        # check absolute ("mount point") URL
        r=web.Resource(testRoot(),'foo',place_url="http://example.com/foo")
        ctx = policy.newContext()
        ctx = ctx.childContext('foo',r)
        self.assertEqual(ctx.absoluteURL, ctx.current.place_url)





TestClasses = (
    LocationTests, MethodTest1, MethodTest2, ResourceTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])




































from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

class TestTraversals(TestCase):
    default_url_base = 'http://127.0.0.1'
    script_name = '/x'

    def setUp(self):
        self.url_base = self.default_url_base + self.script_name
        self.ob1 = object()
        self.ob2 = object()
        self.ob3 = object()
        self.policy = web.TestPolicy(testRoot())
        self.ctx = self.policy.newContext({'SCRIPT_NAME':self.script_name})
        self.root = self.ctx.current    # XXX

    def getCurrent(self):
        return self.ctx.current

    def setChild(self,name,ob):
        self.ctx = self.ctx.childContext(name,ob)
        self.failUnless(self.getCurrent() is ob)

    def setPeer(self,name,ob):
        self.ctx = self.ctx.peerContext(name,ob)
        self.failUnless(self.getCurrent() is ob)

    def setParent(self,ob):
        self.ctx = self.ctx.parentContext()
        self.failUnless(self.getCurrent() is ob)

    def checkURLs(self,url):
        self.assertEqual(self.ctx.absoluteURL,self.url_base+url)
        self.assertEqual(self.ctx.traversedURL,self.url_base+url)

    def setName(self,name,ob,url):
        self.ctx = self.ctx.traverseName(name)
        self.failUnless(self.getCurrent() is ob)
        self.checkURLs(url)

    def testGotoChild(self):
        self.setChild('test',self.ob1)
        self.checkURLs('/test')
        self.setChild('test2',self.ob2)
        self.checkURLs('/test/test2')
        self.setChild('test3',self.ob3)
        self.checkURLs('/test/test2/test3')

    def testGotoPeer(self):
        self.setPeer('test',self.ob1)
        self.checkURLs('')
        self.setChild('test2',self.ob2)
        self.checkURLs('/test2')
        ob3 = object()
        self.setPeer('test3',self.ob3)
        self.checkURLs('/test3')

    def testGotoParent(self):
        self.setParent(self.root)    # test initially-empty case
        self.setChild('test',self.ob1)
        self.setChild('test2',self.ob2)
        self.setChild('test3',self.ob3)
        self.checkURLs('/test/test2/test3')
        self.setParent(self.ob2)
        self.checkURLs('/test/test2')
        self.setParent(self.ob1)
        self.checkURLs('/test')
        self.setParent(self.root)    # test return-to-empty case
        self.checkURLs('')

    def testGotoName(self):
        from test_templates import TestApp
        app = TestApp(testRoot())
        self.setChild('test',app)
        self.setName('.',app,'/test')
        self.setName('',app,'/test')
        self.setName('..',self.root,'')
        self.setChild('test',app)
        self.setName('foo',app.foo,'/test/foo')


    def testGetStuff(self):
        self.failUnless(self.ctx.policy is self.policy)
        self.failUnless(
            security.IInteraction(self.ctx.interaction,None) is not None
        )

    def diffCtx(self,ctx1,ctx2):
        return [a
            for a in 'name','current','environ','policy','interaction','skin'
                if getattr(ctx1,a) is not getattr(ctx2,a)
        ]

    def testClone(self):
        ctx = self.ctx.clone()
        self.assertEqual(self.diffCtx(ctx,self.ctx),[])
        ctx1 = ctx.childContext('test',self.ob1)
        ctx2 = ctx1.clone(interaction = ctx.policy.newInteraction())
        self.assertEqual(self.diffCtx(ctx1,ctx2),['interaction'])
        ctx3 = ctx2.clone(skin = "foo")
        self.assertEqual(self.diffCtx(ctx2,ctx3),['skin'])
        self.assertRaises(TypeError,ctx3.clone,foo="bar")

    def testChangeRoot(self):
        self.setChild('test',self.ob1)
        self.setChild('test2',self.ob2)
        self.setChild('test3',self.ob3)
        self.checkURLs('/test/test2/test3')
        self.url_base += '/++skin++foo'
        self.ctx = self.ctx.clone(rootURL=self.url_base)
        self.checkURLs('/test/test2/test3')











class TestContext(TestCase):

    def setUp(self):
        self.policy = web.TestPolicy(testRoot())
        self.ctx = self.policy.newContext({'SCRIPT_NAME':'/x'})
        self.root = self.ctx.current    # XXX

    def newCtx(self,env={},**kw):
        return self.policy.newContext(env,**kw)

    def checkShift(self,sn_in,pi_in,part,sn_out,pi_out):
        ctx = self.newCtx({'SCRIPT_NAME':sn_in,'PATH_INFO':pi_in})
        self.assertEqual(ctx.shift(),part)
        self.assertEqual(ctx.environ['PATH_INFO'],pi_out)
        self.assertEqual(ctx.environ['SCRIPT_NAME'],sn_out)
        return ctx

    def testNewContext(self):
        d = {}
        ctx = web.StartContext('',None,d,policy=self.policy)
        self.failUnless(ctx.environ is d)
        self.failUnless(web.ITraversalContext(ctx) is ctx)

    def testSingleShift(self):
        dm = self.policy.defaultMethod
        self.checkShift('','/', dm, '/'+dm, '')
        self.checkShift('','/x', 'x', '/x', '')
        self.checkShift('/','', None, '/', '')

        ctx = self.newCtx({})
        self.assertEqual(ctx.shift(),dm)
        self.assertEqual(ctx.environ['PATH_INFO'],'')
        self.assertEqual(ctx.environ['SCRIPT_NAME'],'/'+dm)


    def testDoubleShift(self):
        self.checkShift('/a','/x/y', 'x', '/a/x', '/y')
        self.checkShift('/a','/x/',  'x', '/a/x', '/')



    def testNormalizedShift(self):
        dm = self.policy.defaultMethod
        self.checkShift('/a/b', '/../y', '..', '/a', '/y')
        self.checkShift('', '/../y', '..', '', '/y')
        self.checkShift('/a/b', '//y', 'y', '/a/b/y', '')
        self.checkShift('/a/b', '//y/', 'y', '/a/b/y', '/')
        self.checkShift('/a/b', '/./y', 'y', '/a/b/y', '')
        self.checkShift('/a/b', '/./y/', 'y', '/a/b/y', '/')
        self.checkShift('/a/b', '///./..//y/.//', '..', '/a', '/y/')
        self.checkShift('/a/b', '///', dm, '/a/b/'+dm, '')
        self.checkShift('/a/b', '/.//', dm, '/a/b/'+dm, '')
        self.checkShift('/a/b', '/x//', 'x', '/a/b/x', '/')
        self.checkShift('/a/b', '/.', None, '/a/b', '')

    def assertEmptyNS(self,name):
        self.assertEqual(web.parseName(name), ('',name))

    def testSplitNS(self):
        self.assertEmptyNS('xyz')
        self.assertEmptyNS('++abcdef')
        self.assertEmptyNS('++abc+def')
        self.assertEmptyNS('++++def')
        self.assertEmptyNS('+++def+++')
        self.assertEmptyNS('++abc+foo++def')
        self.assertEmptyNS('++9abc++def')
        self.assertEmptyNS('++9abc++def++')

        self.assertEqual(web.parseName('@@xyz'), ('view','xyz'))
        self.assertEqual(web.parseName('++abc++def'), ('abc','def'))
        self.assertEqual(web.parseName('++abc9++def'), ('abc9','def'))











class TestNamespaces(TestCase):

    def setUp(self):
        self.policy = web.TestPolicy(testRoot())
        self.foo_skin = web.Skin()

        foo_dapter = lambda *args: self
        bar_dapter = lambda *args: "baz"

        self.policy.registerProvider(
            web.NAMESPACE_NAMES+'.foo', config.Value(foo_dapter)
        )
        self.policy.registerProvider(
            web.NAMESPACE_NAMES+'.bar', config.Value(bar_dapter)
        )
        self.policy.registerProvider(
            'peak.web.skins.foo', config.Value(self.foo_skin)
        )
        self.p1 = config.registeredProtocol(self.policy,web.VIEW_NAMES+'.foo')
        protocols.declareAdapter(lambda ob:foo_dapter,[self.p1],forTypes=[int])
        protocols.declareAdapter(lambda ob:bar_dapter,[self.p1],forTypes=[str])

        from test_templates import TestApp
        self.app = TestApp(testRoot())

    def invokeHandler(self,ctx,handler,qname,check_context=True):
        ns, nm = web.parseName(qname)
        res = handler(ctx,ns,nm,qname)
        if check_context:
            self.failUnless(res.parentContext() is ctx)
            self.assertEqual(res.name, qname)
        return res

    def testRegisteredNS(self):
        ctx = self.policy.newContext(start=123)
        args = ctx, '', '', ''
        self.failUnless(self.policy.ns_handler('foo')(*args) is self)
        self.assertEqual(self.policy.ns_handler('bar')(*args), "baz")



    def testTraverseResource(self):
        RESOURCE_NS = self.policy.resourcePrefix
        ctx = self.policy.newContext(start=123)

        res = self.invokeHandler(ctx, web.traverseResource, RESOURCE_NS)
        self.failUnless(res.current is ctx.skin)

        self.assertRaises(web.NotFound, web.traverseResource,
            ctx, RESOURCE_NS[2:-2], 'xyz', RESOURCE_NS+"xyz"
        )

    def testRegisteredView(self):
        self.failUnless(self.policy.view_protocol('foo') is self.p1)
        ctx = self.policy.newContext(start=123)
        self.failUnless(ctx.getView('foo') is self)
        self.assertRaises(web.NotFound, ctx.getView, NO_SUCH_NAME)
        self.failUnless(ctx.getView(NO_SUCH_NAME,NOT_FOUND) is NOT_FOUND)
        ctx = ctx.clone(current="123")
        self.assertEqual(ctx.getView('foo'), "baz")
        ctx = ctx.clone(current=[])
        self.assertRaises(web.NotFound, ctx.getView, 'foo')
        self.failUnless(ctx.getView('foo',NOT_FOUND) is NOT_FOUND)

    def testTraverseView(self):
        ctx = self.policy.newContext(start=123)
        for name in '@@foo', '++view++foo':
            res = self.invokeHandler(ctx, web.traverseView, name)
            self.failUnless(res.current is self)
        self.assertRaises(web.NotFound,
            self.invokeHandler, ctx, web.traverseView, "@@"+NO_SUCH_NAME
        )

    def testTraverseSkin(self):
        ctx = self.policy.newContext(start=123)
        res = self.invokeHandler(ctx, web.traverseSkin, '++skin++foo', False)
        self.failUnless(res.skin is self.foo_skin)
        self.assertEqual(res.rootURL, ctx.rootURL+'/++skin++foo')
        self.assertRaises(web.NotFound,
            self.invokeHandler, ctx, web.traverseSkin, "++skin++"+NO_SUCH_NAME
        )

    def testTraverseAttr(self):
        ctx = self.policy.newContext(start=self.app)
        res = self.invokeHandler(ctx, web.traverseAttr, '++attr++foo')
        self.failUnless(res.current is self.app.foo)
        self.assertRaises(web.NotFound,
            self.invokeHandler, ctx, web.traverseAttr, "++attr++"+NO_SUCH_NAME
        )
        self.assertRaises(web.NotAllowed,
            self.invokeHandler, ctx, web.traverseAttr, "++attr++__class__"
        )

    def testTraverseItem(self):
        ctx = self.policy.newContext(start={'foo':'bar'})
        res = self.invokeHandler(ctx, web.traverseItem, '++item++foo')
        self.failUnless(res.current=='bar')
        self.assertRaises(web.NotFound,
            self.invokeHandler, ctx, web.traverseItem, "++item++"+NO_SUCH_NAME
        )
        #self.assertRaises(web.NotAllowed,
        #    self.invokeHandler, ctx, web.traverseItem, "++item++...?"
        #)

    def testTraverseNames(self):
        ctx = self.policy.newContext(start=123)
        self.failUnless(ctx.traverseName('++foo++bar') is self)
        self.assertEqual(ctx.traverseName('++bar++baz'), 'baz')
        self.failUnless(ctx.traverseName('@@foo').current is self)
        self.failUnless(ctx.traverseName('++view++foo').current is self)
        self.failUnless(
            ctx.traverseName('++skin++foo').skin is self.foo_skin
        )
        for pfx in '@@','++view++','++skin++':
            self.assertRaises(web.NotFound, ctx.traverseName, pfx+NO_SUCH_NAME)
        ctx = self.policy.newContext(start=self.app)
        foo = self.app.foo
        self.failUnless(ctx.traverseName('++attr++foo').current is foo)
        ctx = self.policy.newContext(start={'foo':'bar'})
        self.assertEqual(ctx.traverseName('++item++foo').current, 'bar')



NO_SUCH_NAME = '__nonexistent__$$@'

TestClasses = (
    TestTraversals, TestContext, TestNamespaces,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])


































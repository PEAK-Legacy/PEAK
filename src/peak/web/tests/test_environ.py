from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

class TestTraversals(TestCase):

    url_base = 'http://127.0.0.1'   # must not end in /

    def setUp(self):
        self.ob1 = object()
        self.ob2 = object()
        self.ob3 = object()
        self.policy = web.TestPolicy(testRoot())
        self.ctx = self.policy.newContext()
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
        self.checkURLs('/')
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
        self.checkURLs('/')

    def testGotoName(self):
        from test_templates import TestApp
        app = TestApp(testRoot())
        self.setChild('test',app)
        self.setName('.',app,'/test')
        self.setName('',app,'/test')
        self.setName('..',self.root,'/')
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

class TestContext(TestCase):
    def testNewContext(self):
        d = {}
        ctx = web.StartContext('',None,d,policy=web.TestPolicy(testRoot()))
        self.failUnless(ctx.environ is d)
        self.failUnless(web.ITraversalContext(ctx) is ctx)













TestClasses = (
    TestTraversals, TestContext,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])




































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




























TestClasses = (
    TestTraversals, TestContext,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])




































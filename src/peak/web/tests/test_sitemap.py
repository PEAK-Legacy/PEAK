from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
import peak.web.sitemaps as sm
from urllib import quote
from test_resources import ResourceApp1

class ParserTests(TestCase):

    def setUp(self,**kw):
        self.xml_parser = config.XMLParser(
            web.SITEMAP_SCHEMA(testRoot()),
            parent = testRoot(), sm_globals=globals(), **kw
        )
        self.parse = self.xml_parser.parse

        self.nparser = nparser = self.xml_parser.makeParser()
        self.startElement = nparser.startElement
        self.endElement = nparser.endElement
        nparser._beforeParsing(self.xml_parser.parseFunctions())
        self.finish = nparser._afterParsing
        self.policy = web.TestPolicy(ResourceApp1(testRoot()))

    def traverse(self,start,name):
        return self.policy.newContext(start=start).traverseName(name)

    def testRoot(self):
        self.startElement('location',[])
        v = self.endElement('location')
        self.failUnless(web.IPlace(v) is v)
        self.assertEqual(v.place_url,'')










    def testChild(self):
        self.startElement('location',[])
        self.startElement('location',['name','foo'])
        inner = self.endElement('location')
        self.failUnless(web.IPlace(inner) is inner)
        self.assertEqual(inner.place_url,'foo')
        outer = self.endElement('location')
        self.failUnless(inner.getParentComponent() is outer)
        self.assertEqual(outer.place_url,'')
        self.failUnless(self.traverse(outer,'foo').current is inner)

    def testRootIsValid(self):
        self.assertRaises(SyntaxError, self.startElement, 'nosuchthing',[])

    def testRootIsNameless(self):
        self.assertRaises(SyntaxError,
            self.startElement, 'location',['name','foo'])

    def testLocationClassAndGlobals(self):
        self.startElement('location',['class','TestLocation'])
        self.failUnless(isinstance(self.endElement('location'),TestLocation))
        self.startElement('location',['class','TestLocation'])
        self.startElement('location',['name','y'])
        self.failIf(isinstance(self.endElement('location'),TestLocation))
        self.failUnless(isinstance(self.endElement('location'),TestLocation))

    def testImportElement(self):
        self.startElement('location',[])
        self.startElement('import',['module','peak.web.tests.test_sitemap'])
        self.assertEqual(self.endElement('import'),None)
        self.startElement('location',
            ['class','test_sitemap.TestLocation','name','x'])
        self.failUnless(isinstance(self.endElement('location'),TestLocation))

    def testImportEmpty(self):
        self.startElement('location',[])
        self.startElement('import',['module','peak.web.tests.test_sitemap'])
        self.assertRaises(SyntaxError, self.startElement, 'location',[])



    def testRootIsLocation(self):
        self.assertRaises(SyntaxError, self.startElement,
            'import',['module','peak.web.tests.test_sitemap'])

    def testInvalidAttrs(self):
        self.assertRaises(SyntaxError,
            self.startElement, 'location',['foo','bar'])

    def testMissingAttrs(self):
        self.startElement('location',[])
        self.assertRaises(SyntaxError, self.startElement, 'import',[])

    def testChildLocationMustBeNamed(self):
        self.startElement('location',[])
        self.assertRaises(SyntaxError, self.startElement, 'location',[])

    def testContainer(self):
        self.startElement('location',[])
        self.startElement('location',['name','foo'])
        self.startElement('container',['object','globals()'])
        self.endElement()
        loc = self.endElement()
        self.failUnless(
            self.traverse(loc,'TestLocation').current is TestLocation
        )

        self.startElement('location',['name','bar'])
        self.startElement('container',
            ['object','globals()','permission','security.Nobody']
        )
        self.endElement()
        loc = self.endElement()
        self.assertRaises(web.NotFound, self.traverse, loc, 'TestLocation')

    def testLocationId(self):
        self.startElement('location',['id','root'])
        loc = self.endElement()
        self.failUnless(
            self.traverse(loc,'++id++root').current is loc
        )

    def testOfferPath(self):
        self.startElement('location',[])
        self.startElement('offer',['path','foo', 'as','bar'])
        self.endElement()
        self.startElement('location',['name','foo'])
        foo = self.endElement()
        loc = self.endElement()
        self.failUnless(
            self.traverse(loc,'++id++bar').current is foo
        )


    def testRequirePermission(self):
        self.startElement('location', [])

        self.startElement('location',['name','foo'])
        self.startElement('require',['permission','security.Anybody'])
        self.startElement('container',['object','globals()',])
        self.endElement('container')
        self.endElement('require')
        foo = self.endElement('location')
        self.failUnless(
            self.traverse(foo,'TestLocation').current is TestLocation
        )

        self.startElement('location',['name','bar'])
        self.startElement('require',['permission','security.Nobody'])
        self.startElement('container',['object','globals()',])
        self.endElement('container')
        self.endElement('require')
        bar = self.endElement('location')
        self.assertRaises(web.NotFound, self.traverse, bar, 'TestLocation')









    def testNotAllowedInContent(self):
        self.startElement('location', [])
        self.startElement('content', ['type','int'])
        self.assertRaises(SyntaxError, self.startElement,
            'offer',['path','foo', 'as','bar'])
        self.endElement('offer')
        self.assertRaises(SyntaxError, self.startElement,
            'container',['object','{}'])
        self.endElement('container')
        self.assertRaises(SyntaxError, self.startElement,
            'content',['type','int'])


    def testChoice(self):
        choose = lambda names,**kw: sm.choose(self.nparser,names,kw)
        self.assertRaises(SyntaxError, choose, ('a','b'))
        self.assertEqual(choose(['a','b'],b=1), ('b',1))
        self.assertRaises(SyntaxError, choose, ('a','b'), a=1, b=2)


    def testViewWrappers(self):
        ctx = self.policy.newContext()
        permHandler = sm.addPermission(nullHandler,security.Nobody)
        self.assertRaises(web.NotAllowed,permHandler,ctx,None,'','x','x')
        permHandler = sm.addPermission(nullHandler,security.Anybody)
        self.failUnless(permHandler(ctx,None,'','x','x').current is None)
        helpedHandler = sm.addHelper(nullHandler,lambda x: [x])
        self.assertEqual(helpedHandler(ctx,None,'','x','x').current, [None])













    def testBasicViews(self):
        end=self.endElement
        self.startElement('location', [])
        self.startElement('content', ['type','int'])
        self.startElement('view',['name','foo','object','"xyz"']); end()
        self.startElement('view',['name','bar','attribute',"__class__"]); end()
        self.startElement('view',['name','baz','expr','ob','helper','repr'])
        end()
        self.startElement('view',['name','fiz','function','nullHandler']);end()
        self.startElement('view',
            ['name','fuz','resource','peak.web.tests/template1']
        );end()
        end('content')
        loc = end('location')
        ctx = self.policy.newContext(start=loc).childContext('test',123)
        ctx = loc.beforeHTTP(ctx)
        self.assertEqual(ctx.traverseName("foo").current, "xyz")
        self.assertEqual(ctx.traverseName("bar").current, int)
        self.assertEqual(ctx.traverseName("baz").current, "123")
        self.assertEqual(ctx.traverseName("fiz").current, 123)
        self.failUnless(isinstance(ctx.traverseName("fuz").current,
                web.TemplateDocument)
        )

    def testViewHandlers(self):
        ctx = self.policy.newContext()
        handler = sm.attributeView('url')
        self.assertEqual(handler(ctx,ctx,'','x','x').current, ctx.url)
        handler = sm.objectView(123)
        self.assertEqual(handler(ctx,ctx,'','x','x').current, 123)
        handler = sm.resourceView('peak.web.tests/template1')
        self.failUnless(isinstance(handler(ctx,ctx,'','x','x').current,
            web.TemplateDocument))

    def testExtendedLocation(self):
        self.setUp(sm_included_from={'name':'foo','class':'TestLocation'})
        self.startElement('location', [])
        loc = self.endElement('location')
        self.assertEqual(loc.getComponentName(), 'foo')
        self.failUnless(isinstance(loc,TestLocation))

    def testLocationExtends(self):
        self.startElement('location', ['extends','data:,'+quote("""
                <location id="nested.root">
                <import module="peak.web.tests.test_sitemap" as="tsm"/>
                <location name="foo" class="tsm.TestLocation"/>
                </location>"""), 'id','root'
            ]
        )
        loc = self.endElement('location')
        self.failUnless(
            isinstance(self.traverse(loc,'foo').current,TestLocation)
        )
        self.failUnless(self.traverse(loc,'++id++root').current is loc)
        self.failUnless(self.traverse(loc,'++id++nested.root').current is loc)
        
    # content [location]

    # location[configure]

    # Extending location's views should override extendee's

    # XXX Containers in extending are *after* those in extendee!

    # allow(attributes+interfaces)[permission]

    # XXX Location should support direct permissions, and ignore redundant ones

    # view[id?]

class TestLocation(web.Location):
    pass

def nullHandler(ctx, ob, namespace, name, qname, default=NOT_GIVEN):
    return ctx.childContext(qname,ob)







TestClasses = (
    ParserTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])




































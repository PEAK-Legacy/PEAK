from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

class ParserTests(TestCase):

    def setUp(self):
        self.xml_parser = config.XMLParser(
            config.lookup(testRoot(), 'peak.web.sitemap_schema'),
            parent = testRoot(), sm_globals=globals()
        )
        self.parse = self.xml_parser.parse

        self.nparser = nparser = self.xml_parser.makeParser()
        nparser.addNamespace('','mid:pw-sitemap@peak-dev.org')
        self.startElement = nparser.startElement
        self.endElement = nparser.endElement
        nparser._beforeParsing(self.xml_parser.parseFunctions())
        self.finish = nparser._afterParsing
        self.policy = web.TestPolicy(testRoot())

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


    # content(type) [location,helper,permission]
    #   'offer' and 'container' should fail if inside 'content'

    # view(name, resource|attribute|object|function)[helper,id,permission]

    # allow(attributes|interfaces)[permission]

    # location[include,configure]
    # require[helper]

    # XXX Location should support direct permissions, and ignore redundant ones


class TestLocation(web.Location):
    pass

TestClasses = (
    ParserTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])




















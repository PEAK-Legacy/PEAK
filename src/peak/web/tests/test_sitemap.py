from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

class ParserTests(TestCase):

    def setUp(self):
        self.xml_parser = config.XMLParser(
            config.lookup(testRoot(), 'peak.web.sitemap_schema'),
            parent = testRoot(),
        )
        self.parse = self.xml_parser.parse

        self.nparser = nparser = self.xml_parser.makeParser()
        nparser.addNamespace('','mid:pw-sitemap@peak-dev.org')
        self.startElement = nparser.startElement
        self.endElement = nparser.endElement
        nparser._beforeParsing(self.xml_parser.parseFunctions())
        self.finish = nparser._afterParsing
        self.policy = web.TestPolicy(testRoot())

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
        ctx = self.policy.newContext(start=outer)
        self.failUnless(ctx.traverseName('foo').current is inner)
        


    # Validate attrs - no name on root, no unrecognized non-ns attrs
    # Validate elements - no unrecognized elements
    # Fail if top element is not 'location'
    # Root parser stack has 'sm.globals' (from peak.config.ini_files)
    # Each location level copies previous location's sm.globals
    # Import element adds lazyModule to globals
    # Import element disallows children
    # Container element evals immediately and adds to current location
    # 'id' on location registers '.' for id
    # 'offer' registers path
    # 'offer' and 'container' fail if not direct child of location

    # content, require, allow, view...
    # XXX Permissions should be per-location

                
TestClasses = (
    ParserTests, 
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])




















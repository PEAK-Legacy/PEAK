"""Tests for SOX"""

from unittest import TestCase, makeSuite, TestSuite
from cStringIO import StringIO
from xml.sax import InputSource
from TW.Utils import SOX

def stream(str):
    inpsrc = InputSource()
    inpsrc.setByteStream(StringIO(str))
    return inpsrc

    
class SOXTest(TestCase):
    text = "<nothing/>"

    def setUp(self):
        self.object = SOX.load(stream(self.text))























class Simple(SOXTest):

    text = """<top foo="bar" baz="spam">TE<middle/>XT</top>"""
    
    def checkTop(self):
        assert self.object.documentElement._name == 'top'

    def checkNodelist(self):
        object = self.object
        top = object._get('top')
        assert len(top)==1
        assert object.top is top

    def checkText(self):
        t = []
        for n in self.object.documentElement._allNodes:
            if n == str(n): t.append(n)
        assert ''.join(t) == 'TEXT'

    def checkAttrs(self):
        assert self.object.documentElement.foo=='bar'
        assert self.object.documentElement.baz=='spam'

TestClasses = (
    Simple,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)


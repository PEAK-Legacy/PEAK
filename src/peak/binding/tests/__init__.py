"""Module inheritance and metaclass tests"""

from unittest import TestCase, makeSuite, TestSuite
from TW.API import *

class ModuleTest(TestCase):

    def checkBase(self):
        from testM1 import BaseClass as B1
        from testM2 import BaseClass as B2
        assert B1.foo==1
        assert B2.foo==2
        
    def checkSub(self):
        from testM1 import Subclass as S1
        from testM2 import Subclass as S2
        assert S1.foo==1
        assert S2.foo==2

    def checkNested(self):
        from testM1 import Subclass as S1
        from testM2 import Subclass as S2
        assert S1.Nested.bar=='baz'
        assert S2.Nested.bar=='baz'
        assert S1.NestedSub.bar == 'baz'
        assert S2.NestedSub.bar == 'baz'
        assert not hasattr(S1.NestedSub,'spam')
        assert S2.NestedSub.spam == 'Nested'

    def checkFuncGlobals(self):
        from testM1 import aFunc1 as F11
        from testM2 import aFunc1 as F12
        assert F11()=='M1'
        assert F12()=='M2'

    def checkWrapping(self):
        from testM1 import aFunc2 as F21
        from testM2 import aFunc2 as F22
        assert F21('x')=='M1(x)'
        assert F22('x')=='after(M1(before(x)))'

    def checkBaseBinding(self):
        import testM2, UserList
        assert testM2.RebindSub.M1=='M1'
        assert testM2.RebindSub.M2=='M2'
        assert testM2.RebindSub.__bases__ == (
            testM2.UnusedBase, UserList.UserList, object  
        ), testM2.RebindSub.__bases__

    def checkRefBetweenClasses(self):
        from testM2 import Referencer as R
        assert R.containedClass.M1=='M1'

class DescriptorData(SEF.App):

    thing1 = "this is my thing"

    thing2 = SEF.bindTo('thing1')

    thing3 = SEF.requireBinding('This is required')

    thing4 = SEF.bindToNames('thing1','thing2')

    underflow = SEF.bindToParent(50)

    class aService(SEF.Service):

        thing5 = SEF.bindToParent()

        class nestedService(SEF.Service):

            thing6 = SEF.bindToParent(2)













class DescriptorTest(TestCase):

    def setUp(self):
        self.data = DescriptorData()

    def checkBinding(self):
        thing2 = self.data.thing2 
        assert (thing2 is self.data.thing1), thing2
        assert self.data.__dict__['thing2'] is thing2

    def checkMulti(self):

        thing4 = self.data.thing4
        assert len(thing4)==2
        assert type(thing4) is tuple
        assert thing4[0] is self.data.thing1
        assert thing4[1] is self.data.thing2

    def checkParents(self):

        p1 = self.data.aService.thing5
        p2 = self.data.aService.nestedService.thing6
        p3 = self.data.underflow

        try:
            assert p1 is p2
            assert p1 is self.data
            assert p3 is p2
        finally:
            del self.data.aService.thing5
            del self.data.aService.nestedService.thing6
            del self.data.underflow

    def checkForError(self):
        try:
            self.data.thing3
        except NameError:
            pass
        else:
            raise AssertionError("Didn't get an error retrieving 'thing3'")

TestClasses = (
    ModuleTest, DescriptorTest
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































"""Module inheritance and metaclass tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *

class ModuleTest(TestCase):

    def setUp(self):
        import testM1, testM2
        self.M1, self.M2 = testM1, testM2

    def checkBase(self):
        assert self.M1.BaseClass.foo==1
        assert self.M2.BaseClass.foo==2
        
    def checkSub(self):
        assert self.M1.Subclass.foo==1
        assert self.M2.Subclass.foo==2

    def checkNested(self):
        assert self.M1.Subclass.Nested.bar=='baz'
        assert self.M2.Subclass.Nested.bar=='baz'
        assert self.M1.Subclass.NestedSub.bar == 'baz'
        assert self.M2.Subclass.NestedSub.bar == 'baz'
        assert not hasattr(self.M1.Subclass.NestedSub,'spam')
        assert self.M2.Subclass.NestedSub.spam == 'Nested'

    def checkFuncGlobals(self):
        assert self.M1.aFunc1()=='M1'
        assert self.M2.aFunc1()=='M2'

    def checkWrapping(self):
        assert self.M1.aFunc2('x')=='M1(x)'
        assert self.M2.aFunc2('x')=='after(M1(before(x)))'

    def checkRefBetweenClasses(self):
        assert self.M2.Referencer.containedClass.M1=='M1'




    def checkBaseBinding(self):
        import UserList
        assert self.M2.RebindSub.M1=='M1'
        assert self.M2.RebindSub.M2=='M2'
        assert self.M2.RebindSub.__bases__ == (
            self.M2.UnusedBase, UserList.UserList, object  
        ), self.M2.RebindSub.__bases__


class AdviceTest(ModuleTest):
    
    def setUp(self):
        import testM2a, testM1a, testM1
        self.M1 = testM1
        self.M2 = testM1a


























class DescriptorData(binding.Component):

    thing1 = "this is my thing"

    thing2 = binding.bindTo('thing1')

    thing3 = binding.requireBinding('This is required')

    thing4 = binding.bindToNames('thing1','thing2')

    underflow = binding.bindToParent(50)

    class aService(binding.AutoCreated):

        thing5 = binding.bindToParent()

        class nestedService(binding.AutoCreated):

            thing6 = binding.bindToParent(2)






















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
    ModuleTest, AdviceTest, DescriptorTest,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































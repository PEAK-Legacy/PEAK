"""Configuration system tests"""

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


























TestClasses = (
    ModuleTest, AdviceTest, 
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































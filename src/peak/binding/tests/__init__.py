"""Module inheritance tests"""

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

TestClasses = (
    ModuleTest,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































"""Tests for advice"""

from unittest import TestCase, makeSuite, TestSuite
from peak.util.advice import *

def ping(log, value):

    def pong(klass):
        log.append((value,klass))
        return [klass]

    addClassAdvisor(pong)





























class AdviceTests(TestCase):

    def checkOrder(self):
        log = []
        class Foo:
            ping(log, 1)
            ping(log, 2)
            ping(log, 3)

        # Strip the list nesting
        for i in 1,2,3:
            assert isinstance(Foo,list)
            Foo, = Foo

        assert log == [
            (1, Foo),
            (2, [Foo]),
            (3, [[Foo]]),
        ]






















    def checkMixedMetas(self):

        class M1(type): pass
        class M2(type): pass

        class B1: __metaclass__ = M1
        class B2: __metaclass__ = M2

        try:
            class C(B1,B2):
                ping([],1)
        except TypeError:
            pass
        else:
            raise AssertionError("Should have gotten incompatibility error")

        class M3(M1,M2): pass
        
        class C(B1,B2):
            __metaclass__ = M3
            ping([],1)

        assert isinstance(C,list)
        C, = C
        assert isinstance(C,M3)
















    def checkRootMetas(self):

        # Create a new root metaclass; this is akin to an ExtensionClass,
        # one of the Don Beaudry metaclasses, or 'type' itself.

        class _type(type): pass
        _type.__class__ = _type

        try:
            class C(type,_type):
                ping([],1)
        except TypeError:
            pass
        else:
            raise AssertionError("Should have found incompatible roots")


TestClasses = (
    AdviceTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])


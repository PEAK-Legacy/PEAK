"""Unit tests for relational algebra"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from peak.query.api import *

class TestFlatConditions(TestCase):

    """Verify that logical expressions automatically flatten themselves

    Relational algebra is at its best when conditions are expressed in
    conjunctive normal form.  That is, all conditions are and-ed together in
    as flat a structure as possible.  Apart from that, conditions should be
    as simple as possible.  So, we want the following transformations to
    occur wherever possible:

        * NOT(OR(x,y)) -> AND(NOT(x),NOT(y))

        * AND(x,AND(y,z)) -> AND(x,y,z)

        * OR(x,OR(y,z)) -> OR(x,y,z)

        * NOT(NOT(x)) -> x

        * NOT(EQ(x,y)) -> NE(x,y) (and similar for all comparison ops)

    The test cases in this class will verify that expressions are as simple
    as possible, but no simpler.  :)
    """











TestClasses = (
    TestFlatConditions,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))
    return TestSuite(s)
































"""Unit tests for relational algebra"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from peak.query.api import *
#from peak.query.algebra import And, Or

class SimplificationAndEquality(TestCase):

    """Verify that boolean expressions are equal to their simpler forms

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

    def setUp(self):
        self.condX = adapt('x',IBooleanExpression)
        self.condY = adapt('y',IBooleanExpression)
        self.condZ = adapt('z',IBooleanExpression)





    def testCommutativity(self):

        x,y,z = self.condX, self.condY, self.condZ

        self.assertEqual( (x & y & z), (z & y & x) )
        self.assertNotEqual( (x & y & z), (x & y) )

        self.assertEqual( (x|y|z), (z|y|x) )
        self.assertNotEqual( (x|y|z), (x|y) )


    def testAndIsNotOr(self):
        x,y,z = self.condX, self.condY, self.condZ
        self.assertNotEqual( (x&y), (x|y) )


    def testAssociativity(self):
        x,y,z = self.condX, self.condY, self.condZ

        self.assertEqual( (x&(y&z)), ((x&y)&z) )
        self.assertNotEqual( (x|(y&z)), (x&y)|z )

        self.assertEqual( (x|(y|z)), ((x|y)|z) )
        self.assertNotEqual( (x&(y|z)), ((x|y)&z) )


    def testNegation(self):
        x,y,z = self.condX, self.condY, self.condZ

        self.assertEqual( ~x, ~~~x)
        self.assertEqual( x, ~~x)
        self.assertNotEqual( x, ~x)

        self.assertNotEqual( ~(x&y), (x&y) )
        self.assertNotEqual( ~(x&y), (x|y) )
        self.assertEqual( ~(x&y), (~x|~y) )
        self.assertEqual( ~~(x&y), (x&y) )
        self.assertEqual(~((x|y)&z), (~(x|y)|~z) )
        self.assertEqual((~(x&y)&~z), ~((x&y)|z) )


TestClasses = (
    SimplificationAndEquality,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))
    return TestSuite(s)
































"""Unit tests for relational algebra"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from peak.query.api import *
from peak.query.algebra import ThetaJoin, Not, And, Or, Select

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
        self.rvA = adapt('A',IRelationVariable)
        self.rvB = adapt('B',IRelationVariable)
        self.rvC = adapt('C',IRelationVariable)
        self.rvD = adapt('D',IRelationVariable)

    def testBooleanCommutativity(self):
        x,y,z = self.condX, self.condY, self.condZ
        self.assertEqual( (x & y & z), (z & y & x) )
        self.assertNotEqual( (x & y & z), (x & y) )
        self.assertEqual( (x|y|z), (z|y|x) )
        self.assertNotEqual( (x|y|z), (x|y) )

    def testBooleanEqualities(self):
        x,y,z = self.condX, self.condY, self.condZ
        self.assertNotEqual( (x&y), (x|y) )
        self.assertEqual(x,x)
        self.assertNotEqual(x,y)
        self.assertEqual( (x|x), x )
        self.assertEqual( (x&x), x )
        self.assertEqual( (x&y)&(x&y&z), (x&y&z) )

    def testBooleanAssociativity(self):
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





    def testJoinCommutativity(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEqual(A.thetaJoin(x,B), B.thetaJoin(x,A))
        self.assertEqual(A.thetaJoin(x,B,C), B.thetaJoin(x,A,C))
        self.assertEqual(A.thetaJoin(x,B,C), C.thetaJoin(x,B,A))


    def testJoinAssociativity(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEqual(
            ThetaJoin(x,A,B).thetaJoin(y,C),
            ThetaJoin(x&y,A,B,C)
        )

        self.assertEqual(
            A.thetaJoin(x,B).thetaJoin(y,C.thetaJoin(z,D)),
            A.thetaJoin(x&y&z,B,C,D)
        )


    def testSignatures(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertRaises(TypeError,Or)         # too few args
        self.assertRaises(TypeError,And)
        self.assertRaises(TypeError,Not)
        self.assertRaises(TypeError,Select)
        self.assertRaises(TypeError,ThetaJoin)
        self.assertRaises(TypeError,ThetaJoin,x)
        self.assertRaises(TypeError,ThetaJoin,x,A)

        self.assertRaises(TypeError,Not,x,y)    # too many args
        self.assertRaises(TypeError,Select,x,A,B)

    def testSelectionAssociativity(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEquals(
            A.thetaJoin(x,B).select(y),
            A.thetaJoin(x&y,B)
        )

        self.assertEquals(
            A.select(y).select(z),
            A.select(y&z)
        )

        self.assertEquals(
            A.select(z).select(y),
            A.select(y&z)
        )

        self.assertEquals(
            A.thetaJoin(x,B).select(y).select(z),
            A.thetaJoin(x&y&z,B)
        )

        self.assertEquals(
            A.select(y).thetaJoin(x,B),
            A.thetaJoin(x&y,B)
        )












TestClasses = (
    SimplificationAndEquality,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))
    return TestSuite(s)
































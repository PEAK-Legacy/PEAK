"""Unit tests for relational algebra"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from peak.query.api import *
from peak.query.algebra import BasicJoin, Not, And, Or, Table, PhysicalDB
from kjbuckets import kjSet

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

    A_Columns = ('aa','ab','ac')
    B_Columns = ('b1','b2')
    C_Columns = ('CC','DD','EE')
    D_Columns = ('d',)




    def setUp(self):
        self.condX = adapt('x',IBooleanExpression)
        self.condY = adapt('y',IBooleanExpression)
        self.condZ = adapt('z',IBooleanExpression)
        self.rvA = Table('A',self.A_Columns)
        self.rvB = Table('B',self.B_Columns)
        self.rvC = Table('C',self.C_Columns)
        self.rvD = Table('D',self.D_Columns)

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
            A.thetaJoin(x,B).thetaJoin(y,C),
            A.thetaJoin(x&y,B,C)
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
        self.assertRaises(TypeError,BasicJoin)
        self.assertRaises(TypeError,BasicJoin,x)
        self.assertRaises(TypeError,Not,x,y)    # too many args

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


    def testJoinPreservation(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertNotEquals(A.thetaJoin(x,A), A.thetaJoin(x,A,A))
        self.assertNotEquals(A.starJoin(x,A), A.starJoin(x,A,A))


    def testOuterJoinInequalities(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertNotEqual( A.starJoin(x,B), B.starJoin(x,A)  )
        self.assertNotEqual( A.starJoin(x,A), A.starJoin(x,B)  )
        self.assertNotEqual( A.starJoin(x,B), A.thetaJoin(x,B)  )

        self.assertEqual(
            A.starJoin(x,B).starJoin(y,C),
            A.starJoin(y,C).starJoin(x,B)
        )

        self.assertEqual(
            A.thetaJoin(x,B).starJoin(y,C),
            B.thetaJoin(x,A).starJoin(y,C)
        )

        self.assertEqual(
            A.starJoin(y,C).thetaJoin(x,B),
            A.thetaJoin(x,B).starJoin(y,C)
        )









    def testColumns(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEqual( kjSet(A.attributes()), kjSet(self.A_Columns) )
        self.assertEqual( kjSet(B.attributes()), kjSet(self.B_Columns) )
        self.assertEqual( kjSet(C.attributes()), kjSet(self.C_Columns) )
        self.assertEqual( kjSet(D.attributes()), kjSet(self.D_Columns) )

        self._verifyJoinedColumns(A,x,B)
        self._verifyJoinedColumns(C,y,D)
        self._verifyJoinedColumns(B,z,C)
        self._verifyJoinedColumns(A.thetaJoin(x,B),y,C.thetaJoin(z,D))

    def _verifyJoinedColumns(self,base,cond,*relvars):
        AB = base.thetaJoin(cond,*relvars)
        AB_cols = AB.attributes()
        AplusB  = base.attributes()
        for rv in relvars:
            AplusB += rv.attributes()
        self.assertEqual(AB_cols, AplusB)




















    def testPhysicalDB(self):

        db = PhysicalDB(
            tables = Items(
                Branch = (
                    'headempnr','branchnr','cityname','statecode','country'
                ),
                Employee = (
                    'empnr','empname','branchnr','salary','cityname','statecode',
                    'country', 'supervisor_empnr', 'mainphone', 'otherphone'
                ),
                Speaks = ('empnr','languagename'),
                Drives = ('empnr','carregnr'),
                Car = ('carregnr','carmodelname','color'),
                LangUse = ('languagename','country'),
            )
        )

        Branch = db.table('Branch')
        Employee = db.table('Employee')

        x,y,z = self.condX, self.condY, self.condZ

        self.assertEqual(
            Branch.thetaJoin(x,Employee), Employee.thetaJoin(x,Branch)
        )

        for tbl in 'Branch','Employee','Speaks','Drives','Car','LangUse':
            tbl = db.table(tbl)
            self.failUnless(tbl.getDB() is db)
            self.failUnless(tbl.project(tbl.attributes().keys()[:-1]).getDB() is db)

        self.failUnless(Branch.thetaJoin(x,Employee).getDB() is db)

        # Mixed-db joins should have a DB of None (for now)
        self.failUnless(Branch.thetaJoin(x,self.rvA).getDB() is None)





    def testProjection(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        # B and A have no common attrs
        self.failIf( A.project(self.B_Columns).attributes() )

        # columns in A.thetaJoin(x,B).project(B.attributes()) == B.attributes()
        AB = A.thetaJoin(x,B)
        self.assertEqual(
            AB.project(self.B_Columns).attributes(),
            B.attributes()
        )

        # A.proj(a).thetaJoin(x,B.proj(b)) == A.thetaJoin(x,B).proj(a+b)
        self.assertEqual(
            A.thetaJoin(x,B).project(self.A_Columns[:2]+self.B_Columns[:2]),
            A.project(self.A_Columns[:2]).thetaJoin(x,B.project(self.B_Columns[:2]))
        )






















TestClasses = (
    SimplificationAndEquality,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))
    return TestSuite(s)
































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

        self.assertEqual(A(join=[B],where=x), B(join=[A],where=x))
        self.assertEqual(A(join=[B,C],where=x), B(join=[A,C],where=x))
        self.assertEqual(A(join=[B,C],where=x), C(join=[B,A],where=x))


    def testJoinAssociativity(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEqual(
            A(join=[B],where=x)(join=[C],where=y),
            A(join=[B,C],where=x&y)
        )

        self.assertEqual(
            A(join=[B],where=x)(join=[C(join=[D],where=z)],where=y),
            A(join=[B,C,D],where=x&y&z)
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
            A(join=[B],where=x)(where=y),
            A(join=[B],where=x&y)
        )

        self.assertEquals(
            A(where=y)(where=z),
            A(where=y&z)
        )

        self.assertEquals(
            A(where=z)(where=y),
            A(where=y&z)
        )

        self.assertEquals(
            A(join=[B],where=x)(where=y)(where=z),
            A(join=[B],where=x&y&z)
        )

        self.assertEquals(
            A(where=y)(join=[B],where=x),
            A(join=[B],where=x&y)
        )


    def testOuterJoinInequalities(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertNotEqual( A(outer=[B],where=x), B(outer=[A],where=x) )
        self.assertNotEqual( A(outer=[C],where=x), A(outer=[B],where=x) )
        self.assertNotEqual( A(outer=[B],where=x), A(join=[B],where=x) )

        self.assertEqual(
            A(outer=[B],where=x)(outer=[C],where=y),
            A(outer=[C],where=y)(outer=[B],where=x)
        )

        self.assertEqual(
            A(join=[B],where=x)(outer=[C],where=y),
            B(join=[A],where=x)(outer=[C],where=y)
        )

        self.assertEqual(
            A(outer=[C],where=y)(join=[B],where=x),
            A(join=[B],where=x)(outer=[C],where=y)
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
        self._verifyJoinedColumns(A(join=[B],where=x),y,C(join=[D],where=z))

    def _verifyJoinedColumns(self,base,cond,*relvars):
        AB = base(join=relvars, where=cond)
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
            Branch(join=[Employee],where=x), Employee(join=[Branch],where=x)
        )

        # Single-db join should have the same DB
        self.failUnless(Branch(join=[Employee],where=x).getDB() is db)

        # Mixed-db joins should have a DB of None (for now)
        self.failUnless(Branch(join=[self.rvA],where=x).getDB() is None)









        for tbl in 'Branch','Employee','Speaks','Drives','Car','LangUse':

            # table objects must be unique
            self.failUnless(db.table(tbl) is not db.table(tbl))

            # column objects must be unique
            self.assertNotEqual(
                db.table(tbl).attributes(), db.table(tbl).attributes()
            )

            tbl = db.table(tbl)

            # table's db should be db
            self.failUnless(tbl.getDB() is db)

            # a projection of table should still have the same DB
            self.failUnless(
                tbl(keep=tbl.attributes().keys()[:-1]).getDB() is db
            )


    def testReferences(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEqual(A.getReferencedRVs(),[A])
        tmp = A(outer=[B,C,D],where=x)
        self.assertEqual(kjSet(tmp.getReferencedRVs()),kjSet([A,B,C,D,tmp]))


    def testRVReuseNotAllowed(self):
        # The same RV may not appear more than once in a single expression

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertRaises(ValueError, B, join=[A,A])
        self.assertRaises(ValueError, B, outer=[A,A])
        self.assertRaises(ValueError, B(join=[C]), join=[C(join=[D])])


    def testProjection(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        # B and A have no common attrs
        self.failIf( A(keep=self.B_Columns).attributes() )

        # columns in A(join=[B],where=x)(keep=B.attributes()) == B.attributes()
        AB = A(join=[B],where=x)
        self.assertEqual(
            AB(keep=self.B_Columns).attributes(),
            B.attributes()
        )

        # columns in A(outer=[B],where=x)(keep=B.attributes()) == B.attributes()
        AB = A(outer=[B],where=x)
        self.assertEqual(
            AB(keep=self.B_Columns).attributes(),
            B.attributes()
        )

        # A.proj(a)(join=[B.proj(b)],where=x) == A(join=[B],where=x).proj(a+b)
        self.assertEqual(
            A(join=[B],where=x)(keep=self.A_Columns[:2]+self.B_Columns[:2]),
            A(keep=self.A_Columns[:2])(join=[B(keep=self.B_Columns[:2])],where=x)
        )















    def testRename(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        for colNum in range(len(self.A_Columns)):
            theColumn = self.A_Columns[colNum]
            Arenamed = A(rename=[(theColumn,'theColumn')])

            self.assertEqual(
                A.attributes()[theColumn],
                Arenamed.attributes()['theColumn']
            )
            self.assertEqual(
                kjSet(Arenamed.attributes().keys()),
                kjSet(
                    ('theColumn',) + self.A_Columns[:colNum]
                                   + self.A_Columns[colNum+1:]
                )
            )

        for abcd in [ A(join=[B,C,D],where=x), A(outer=[B,C,D],where=x) ]:

            ABCD = abcd(
                rename=[(n,n.upper()) for n in abcd.attributes().keys()]
            )

            self.assertEqual(
                kjSet([n.upper() for n in abcd.attributes().keys()]),
                kjSet(ABCD.attributes())
            )











TestClasses = (
    SimplificationAndEquality,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))
    return TestSuite(s)
































"""Test DDT"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from cStringIO import StringIO
from peak.ddt.api import *
from peak.ddt.html_doc import GREEN,RED,YELLOW,GREY,HTMLDocument

sample_input = """
    <body>
    <table>
        <tr><td>test parser</td></tr>
        <tr><td>one</td><td>two</td></tr>
        <tr><td>buckle</td><td>your</td><td>shoe</td></tr>
    </table>
    </body>
"""

sample_output = """
    <body>
    <table>
        <tr><td%(GREY)s>test parser</td></tr>
        <tr><td%(GREEN)s>one</td><td%(RED)s>two</td></tr>
        <tr><td>buckle</td><td%(RED)s>your</td><td>shoe</td></tr>
    </table>
    </body>
""" % locals()













class BasicTests(TestCase):

    def testScoreArithmetic(self):
        self.assertEqual(Error, Zeros+Error)
        self.assertEqual(Right, Zeros+Right)
        self.assertEqual(Wrong, Zeros+Wrong)
        self.assertEqual(Ignored, Zeros+Ignored)
        self.assertEqual(Error, Error-Zeros)
        self.assertEqual(Right, Right-Zeros)
        self.assertEqual(Wrong, Wrong-Zeros)
        self.assertEqual(Ignored, Ignored-Zeros)

    def testCellScoring(self):
        d=Document()
        d.tables=[Table()]
        d.tables[0].rows=[Row()]
        cells = [Cell(),Cell(),Cell(),Cell()]
        d.tables[0].rows[0].cells = cells
        self.assertEqual(d.score, Zeros)
        cells[0].right()
        self.assertEqual(d.score, Right)
        cells[1].wrong("actual")
        self.assertEqual(cells[1].actual,"actual")
        self.assertEqual(d.score, Right+Wrong)
        cells[2].ignore()
        self.assertEqual(d.score, Right+Wrong+Ignored)
        cells[3].exception((1,2,3))
        self.assertEqual(cells[3].exc_info,(1,2,3))
        self.assertEqual(d.score, Right+Wrong+Ignored+Error)
        self.assertEqual(d.score, Score(right=1,wrong=1,ignored=1,exceptions=1))

        # Shouldn't allow us to change state on these
        self.assertRaises(ValueError,cells[0].wrong)
        self.assertRaises(ValueError,cells[1].right)
        self.assertRaises(ValueError,cells[2].exception)
        self.assertRaises(ValueError,cells[3].ignore)





    def testParsing(self):

        dm = HTMLDocument(testRoot(), text=sample_input)

        storage.beginTransaction(dm)

        try:
            doc = dm.document
            self.assertEqual(len(dm.document.tables),1)
            table = doc.tables[0]
            self.assertEqual(len(table.rows),3)
            rows = table.rows
            self.assertEqual(len(rows[0].cells),1)
            self.assertEqual(len(rows[1].cells),2)
            self.assertEqual(len(rows[2].cells),3)
            self.assertEqual(
                [c.text for c in table.rows[0].cells],
                ['test parser']
            )

            self.assertEqual(
                [c.text for c in table.rows[1].cells],
                ['one','two']
            )
            self.assertEqual(
                [c.text for c in table.rows[2].cells],
                ["buckle","your","shoe"]
            )

        finally:
            storage.abortTransaction(dm)










    def testOutput(self):

        s = StringIO()
        dm = HTMLDocument(testRoot(), text=sample_input, stream=s)

        storage.beginTransaction(dm)

        try:
            doc = dm.document
            table, = doc.tables
            r1,r2,r3 = table.rows
            r1.cells[0].ignore()
            r2.cells[0].right()
            r2.cells[1].wrong()
            r3.cells[1].wrong()
            storage.commitTransaction(dm)
        except:
            storage.abortTransaction(dm)
            raise

        self.assertEqual(s.getvalue(), sample_output)




















TestClasses = (
    BasicTests,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)
































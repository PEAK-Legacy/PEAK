"""Undo-history tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.storage.interfaces import *
from peak.storage.undo import AbstractDelta, History

class TestDelta(AbstractDelta):

    doneCount = 1
    finishCount = 0
    merges = ()
    
    def _undo(self):
        self.doneCount -= 1

    def _redo(self):
        self.doneCount += 1

    def _finish(self):
        self.finishCount += 1

    def _merge(self,delta):
        if not isinstance(delta,TestDelta):
            raise TypeError("Incompatible delta")
        self.merges += (delta,)
















class DeltaTests(TestCase):

    def testActive(self):
        d = TestDelta()
        self.failUnless(IDelta(d,None) is d)
        self.failUnless(d.active)
        self.assertEqual(d.doneCount, 1)
        self.assertEqual(d.finishCount, 0)
        d.finish()
        self.assertEqual(d.doneCount, 1)
        self.assertEqual(d.finishCount, 1)
        self.failIf(d.active)
        self.assertRaises(UndoError, d.finish)

    def testUndo(self):
        d = TestDelta()
        self.assertEqual(d.doneCount, 1)
        self.assertEqual(d.finishCount, 0)
        d.undo()
        self.assertEqual(d.doneCount, 0)
        self.assertEqual(d.finishCount, 1)
        self.assertRaises(UndoError, d.finish)
        self.assertRaises(UndoError, d.undo)

    def testRedo(self):
        d = TestDelta()
        self.assertRaises(UndoError, d.redo)
        self.assertEqual(d.doneCount, 1)
        d.undo()
        self.assertEqual(d.doneCount, 0)
        d.redo()
        self.assertEqual(d.doneCount, 1)

    def testUndoable(self):
        d = TestDelta()
        self.failUnless(d.undoable)
        d.undoable = False
        self.assertRaises(UndoError, d.undo)
        self.assertEqual(d.doneCount, 1)


    def testMerge(self):
        d1,d2 = TestDelta(), TestDelta()
        d1.merge(d2)
        d1.finish()
        self.assertRaises(UndoError, d1.merge, TestDelta())
        d1.undo()
        self.assertRaises(UndoError, d1.merge, TestDelta())
        d1.redo()
        self.assertRaises(UndoError, d1.merge, TestDelta())
        self.assertEqual(d1.merges, (d2,))































class HistoryTests(TestCase):

    def testHistoryCollection(self):
        d1, d2, d3 = TestDelta(), TestDelta(), TestDelta()
        h = History()
        map(h.merge, [d1,d2,d3])
        l = list(h)
        self.assertEqual(l, [d1,d2,d3])
        h.undo()
        for d in l:
            self.assertEqual(d.doneCount, 0)
        h.redo()
        for d in l:
            self.assertEqual(d.doneCount, 1)

    def testHistoryUndoable(self):
        h = History()
        self.failUnless(h.undoable)
        h.merge(TestDelta())
        self.failUnless(h.undoable)
        d = TestDelta()
        d.undoable = False
        h.merge(d)
        self.failIf(h.undoable)
        
    def testMergeByKey(self):
        d1, d2, d3 = TestDelta(), TestDelta(), TestDelta()
        d1.key = d3.key = 'a'; d2.key = 'b'
        h = History()
        map(h.merge, [d1,d2,d3])
        l = list(h)
        self.assertEqual(l, [d1,d2])
        self.assertEqual(d1.merges, (d3,))
        
        
        
        
        
        
        
        
    def testMergeHistory(self):
        d1, d2, d3, d4 = TestDelta(), TestDelta(), TestDelta(), TestDelta()
        d1.key = d3.key = 'a'; d2.key = 'b'
        h1 = History()
        h2 = History()
        h1.merge(d1); h1.merge(d2)
        h2.merge(d3); h2.merge(d4)
        h1.merge(h2)
        self.assertEqual(list(h1), [d1,d2,d4])
        self.assertEqual(d1.merges, (d3,))
        
        #self.failUnless('a' in h1)
        #self.failUnless('b' in h1)
        #self.failIf('c' in h1)
        


























TestClasses = (
    DeltaTests, HistoryTests,
)


def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])


































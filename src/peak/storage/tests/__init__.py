"""Transaction and Persistence tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from Interface import Interface


class TxnStateTest(TestCase):


    def setUp(self):
        self.ts = storage.TransactionService()
        self.p  = LogParticipant()
        self.log = self.p.log = []

    def checkOutside(self):

        ts = self.ts
        
        for op in ts.commit, ts.abort, ts.fail:
            self.assertRaises(exceptions.OutsideTransaction, op)
            
        self.assertRaises(exceptions.OutsideTransaction, ts.join, self.p)
        assert self.log == []


    def checkFail(self):

        ts = self.ts

        ts.begin()
        ts.fail()

        self.assertRaises(exceptions.BrokenTransaction, ts.join, self.p)
        self.assertRaises(exceptions.BrokenTransaction, ts.commit)

        ts.abort()
        assert self.log == []



    def checkStampAndActive(self):

        ts = self.ts

        assert not ts.isActive()
        assert ts.getTimestamp() is None
        
        for fini in ts.commit, ts.abort:

            ts.begin()
            assert ts.isActive()

            from time import time
            assert abs(time() - ts.getTimestamp()) < 5

            fini()

            assert not ts.isActive()
            assert ts.getTimestamp() is None

        assert self.log ==[]


    def checkSimpleUse(self):

        ts = self.ts
        ts.begin()
        ts.join(self.p)
        ts.commit()

        ts.begin()
        ts.join(self.p)
        ts.abort()

        assert self.log == [
            ('readyToVote',ts), ('voteForCommit',ts), ('commit',ts),
            ('finish',ts,True), ('abort',ts), ('finish',ts,False),
        ]



class LogParticipant(storage.AbstractParticipant):

    def readyToVote(self, txnService):
        self.log.append(("readyToVote", txnService))
        return True

    def voteForCommit(self, txnService):
        self.log.append(("voteForCommit", txnService))


    def commitTransaction(self, txnService):
        self.log.append(("commit", txnService))

    def abortTransaction(self, txnService):
        self.log.append(("abort", txnService))

    def finishTransaction(self, txnService, committed):
        self.log.append(("finish", txnService, committed))























class UnreadyParticipant(LogParticipant):

    def readyToVote(self, txnService):
        self.log.append(("readyToVote", txnService))
        return False

class ProcrastinatingParticipant(LogParticipant):

    status = 0

    def readyToVote(self, txnService):
        self.log.append(("readyToVote", txnService))
        old = self.status
        self.status += 1
        return old


class VotingTest(TestCase):

    def setUp(self):
        self.ts = storage.TransactionService()
        self.p_u  = UnreadyParticipant()
        self.p_p  = ProcrastinatingParticipant()
        self.p_n  = LogParticipant()
        self.log = self.p_u.log = self.p_p.log = self.p_n.log = []

    def checkUnready(self):

        ts = self.ts

        ts.begin()
        ts.join(self.p_u)
        ts.join(self.p_p)
        ts.join(self.p_n)
        
        self.assertRaises(exceptions.NotReadyError, ts.commit)

        # just a lot of ready-to-vote attempts
        assert self.log == [('readyToVote',ts)]*len(self.log)


    def checkMixed(self):

        ts = self.ts

        ts.begin()
        ts.join(self.p_p)
        ts.join(self.p_n)
        
        ts.commit()


        # 2 participants * 1 retry for first, rest are all * 2 participants

        assert self.log == \
            [('readyToVote',ts)]   * 4 + \
            [('voteForCommit',ts)] * 2 + \
            [('commit',ts)]        * 2 + \
            [('finish',ts,True)]   * 2


    def checkNormal(self):

        ts = self.ts

        ts.begin()
        ts.join(self.p_n)
        ts.commit()

        assert self.log == [
            ('readyToVote',ts),
            ('voteForCommit',ts),
            ('commit',ts),
            ('finish',ts,True),
        ]







TestClasses = (
    TxnStateTest, VotingTest,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































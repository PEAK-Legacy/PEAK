"""Transaction and Persistence tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from Interface import Interface
from peak.util.MiniTable import Table
from Persistence import Persistent


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







class TxnTable(storage.TransactionComponent):

    stableState = ()
    colNames = ()

    def table(self,d,a):
        return Table( self.colNames, self.stableState )

    table = binding.Once(table)

    def dump(self):
        colNames = self.colNames
        return [row.dump(colNames) for row in self.table]

    def commitTransaction(self, txnService):
        self.stableState = self.dump()            

    def abortTransaction(self, txnService):
        self._delBinding('table')

    def DELETE(self, whereItems):
        self.txnSvc
        self.table.DELETE(whereItems)

    def INSERT(self, items):
        self.txnSvc
        self.table.INSERT(items)

    def INSERT_ROWS(self, rowList):
        self.txnSvc
        self.table.INSERT_ROWS(self.colNames, rowList)

    def SELECT(self, whereItems=()):
        return self.table.SELECT(whereItems)

    def SET(self, whereItems, setItems):
        self.txnSvc
        self.table.SET(whereItems, setItems)



class Harness(binding.Component):

    class sampleTable(TxnTable):
        colNames = 'a', 'b'
        

    class testDM(storage.EntityDM):

        table = binding.bindTo('sampleTable')
        
        class defaultClass(Persistent):
            pass

        def load(self, oid, ob):

            rows = self.table.SELECT(Items(a=oid))

            if rows:
                return dict(rows[0].items())
            else:
                raise KeyError, oid


        def save(self, ob):
            self.table.SET(Items(a=ob._p_oid),Items(b=ob.b))


        def new(self,ob):
            self.table.INSERT(Items(a=ob.a,b=ob.b))
            return ob.a

        def defaultState(self,ob):
            return {}








class TableTest(TestCase):

    def setUp(self):
        self.harness = Harness()
        self.table = self.harness.sampleTable

    def tearDown(self):
        if storage.getTransaction().isActive():
            storage.abortTransaction()
    
    def checkNoChangeOutsideTxn(self):
        self.assertRaises(exceptions.OutsideTransaction,
            self.table.INSERT, Items(a=1,b=2)
        )

    def checkRollback(self):
        assert self.table.dump()==[]

        storage.beginTransaction()
        self.table.INSERT(Items(a=1,b=2))
        assert self.table.dump()==[(1,2)]
        storage.abortTransaction()

        assert self.table.dump()==[]

    def checkCommit(self):
        assert self.table.dump()==[]

        storage.beginTransaction()
        self.table.INSERT(Items(a=1,b=2))
        assert self.table.dump()==[(1,2)]
        storage.commitTransaction()

        assert self.table.dump()==[(1,2)]

        storage.beginTransaction()
        self.table.INSERT(Items(a=3,b=4))
        assert self.table.dump()==[(1,2),(3,4)]
        storage.abortTransaction()
        assert self.table.dump()==[(1,2)]

class DMTest(TestCase):

    def setUp(self):
        self.harness = Harness()
        self.table = self.harness.sampleTable
        self.dm  = self.harness.testDM

    def tearDown(self):
        if storage.getTransaction().isActive():
            storage.abortTransaction()

    def _addData(self):
        storage.beginTransaction()
        self.table.INSERT(Items(a=1,b=2))
    
    def checkExistence(self):

        self._addData()

        ob = self.dm[1]
        assert ob.b==2
        storage.abortTransaction()

        storage.beginTransaction()
        self.assertRaises(KeyError, lambda: ob.b)

    def checkFlush(self):

        self._addData()
        assert self.table.dump()==[(1,2)]
        storage.commitTransaction()
        
        storage.beginTransaction()
        ob = self.dm[1]
        ob.b = 4
        self.dm.flush()
        assert self.table.dump()==[(1,4)]

        storage.abortTransaction()
        assert self.table.dump()==[(1,2)]

    def checkModify(self):
        self._addData()
        ob = self.dm[1]
        ob.b = 4
        assert self.table.dump()==[(1,2)]
        storage.commitTransaction()
        assert self.table.dump()==[(1,4)]


    def checkNew(self):
        storage.beginTransaction()
        ob = self.dm.newItem()
        ob.a = 1
        ob.b = 2
        assert self.table.dump()==[]
        storage.commitTransaction()
        assert self.table.dump()==[(1,2)]
























from peak.storage.LDAP import LDAPCursor, LDAPConnection

class TestCursor(LDAPCursor):

    msgid = 9999

    def fooCvt(name,values):
        if values: return values[0]

    fooCvt = binding.Constant(
        PropertyName('peak.ldap.field_converters.foo'), fooCvt
    )

    def barCvt(name,values):
        if values: return int(values[0])

    barCvt = binding.Constant(
        PropertyName('peak.ldap.field_converters.bar'), barCvt
    )

    class _conn(object):

        def result(msgid, getall, timeout):
            return 'RES_SEARCH_RESULT', [
                ('uid=thing1', {'foo':[], 'baz':['a','b']}),
                ('uid=thing2', {'foo':['spam'], 'bar':['999']}),
            ]

        result = staticmethod(result)


class LDAPSchemaTest(TestCase):

    def checkConversions(self):
        ob = TestCursor(LDAPConnection(), None)
        assert list(ob)==[
            ('uid=thing1', None, ['a','b']),
            ('uid=thing2', 'spam', None, 999),
        ]


TestClasses = (
    LDAPSchemaTest, TxnStateTest, VotingTest, TableTest, DMTest
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































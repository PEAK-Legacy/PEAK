from __future__ import generators
from peak.api import *
from transactions import TransactionComponent
from interfaces import *
from weakref import WeakValueDictionary


__all__ = [
    'ManagedConnection', 'AbstractCursor', 'RowBase',
]

from peak.util.Struct import struct

class RowBase(struct):
    implements(IRow)





























class AbstractCursor(binding.Component):

    implements(ICursor)

    _conn = binding.bindTo('../connection')


    def __init__(self,parentComponent,componentName=None,**kw):

        self.setParentComponent(parentComponent,componentName)

        for k,v in kw.items():
            binding.suggestParentComponent(self,k,v)
            setattr(self,k,v)

        parentComponent.registerCursor(self)


    def close(self):
        self._delBinding('_conn')


    def __iter__(self, onlyOneSet=True):
        raise NotImplementedError


    def nextset(self):
        raise NotImplementedError













    def allSets(self):

        oneSet = self.__iter__

        yield list(oneSet(False))

        while self.nextset():
            yield list(oneSet(False))


    def justOne(self):

        i = iter(self)

        try:
            row = i.next()

        except StopIteration:
            raise exceptions.TooFewResults

        try:
            next = i.next()
        except StopIteration:
            return row

        raise exceptions.TooManyResults


    __invert__ = justOne












class ManagedConnection(TransactionComponent):

    implements(IManagedConnection)

    connection = binding.Once(lambda s,d,a: s._open())
    _closeASAP = False

    txnAttrs = TransactionComponent.txnAttrs + ('txnTime',)

    def closeASAP(self):
        """Close the connection as soon as it's not in a transaction"""

        if self.inTransaction:
            self._closeASAP = True
        else:
            self.close()

    def close(self):
        """Close the connection immediately"""

        if self._hasBinding('connection'):
            self.closeCursors()
            self._close()
            del self.connection

        self._delBinding('_closeASAP')


    def finishTransaction(self, txnService, committed):

        super(ManagedConnection,self).finishTransaction(txnService, committed)

        if self._closeASAP:
            self.close()


    def _open(self):
        """Return new "real" connection to be saved as 'self.connection'"""
        raise NotImplementedError


    def _close(self):
        """Actions to take before 'del self.connection', if needed."""

    __txnTimeConverter = binding.bindToProperty(
        'peak.storage.txnTimeType', default=float
    )

    def txnTime(self,d,a):
        """Per-transaction timestamp, based on this connection's clock

            Note that this default should be overridden for subclasses that
            interact with a database that has a clock!  An SQL connection,
            for example, should perform a query against the database to get
            the DB server's idea of the time.  Connections which have no
            notion of time should just return the transaction's timestamp,
            and so this default implementation will do.  Note that if you
            override this implementation, you must ensure that the
            connection has joined the transaction first!
        """
        return self.__txnTimeConverter( self.joinedTxn.getTimestamp() )

    txnTime = binding.Once(txnTime)


    def joinTxn(self):
        """Join the current transaction, if not already joined"""
        return self.joinedTxn

    def voteForCommit(self, txnService):
        self.closeCursors()

    def abortTransaction(self, txnService):
        self.closeCursors()

    def assertUntransacted(self):
        if self in self.txnSvc:
            raise exceptions.TransactionInProgress(
                """Connection has already joined transaction"""
            )


    _cursors = binding.New(WeakValueDictionary)


    def registerCursor(self,cursor):
        self._cursors[id(cursor)] = cursor


    def closeCursors(self):
        if self._hasBinding('_cursors'):
            for c in self._cursors.values():
                c.close()


    def __call__(self, *args, **kw):

        cursor = self.cursorClass(self, **kw)

        if args:
            cursor.execute(*args)

        return cursor


    cursorClass = AbstractCursor

    address = binding.requireBinding(
        "Address used to create the actual connection"
    )














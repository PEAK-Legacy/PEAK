from __future__ import generators
from peak.api import binding
from transactions import TransactionComponent
from interfaces import *
from weakref import WeakValueDictionary
from peak.util.Struct import makeStructType, makeFieldProperty

__all__ = [
    'ManagedConnection', 'DBCursor', 'LDAPCursor',
]


def _nothing():
    pass



























class DBCursor(binding.Component):

    """Iterable cursor bridge/proxy"""

    __implements__ = ICursor
    
    tooMany = AssertionError
    tooFew  = EOFError

    def __init__(self,parent,**kw):

        self.setParentComponent(parent)

        for k,v in kw.items():
            setattr(self,k,v)

        parent.registerCursor(self)


    def _cursor(self,d,a):
        return self._conn.cursor()

    _cursor = binding.Once(_cursor)
    _conn   = binding.bindTo('../connection')

    def close(self):
        if self.hasBinding('_cursor'):
            self._cursor.close()
            del self._cursor
        if self.hasBinding('_conn'):
            del self._conn
            
    def __setattr__(self,attr,val):
        if self.hasBinding(attr) or hasattr(self.__class__,attr):
            self.__dict__[attr]=val
        else:
            setattr(self._cursor,attr,val)

    def __getattr__(self,attr):
        return getattr(self._cursor,attr)

    def __iter__(self, onlyOneSet=True):

        fetch = self._cursor.fetchmany
        rows = fetch()

        if rows:

            # we don't want to mess with souped-up row types
            # so require an exact match to 'tuple' type

            row = rows[0]

            if type(row) is tuple:  

                rowStruct = makeStructType('rowStruct',
                    [d[0] for d in self._cursor.description],
                    __implements__ = IRow, __module__ = __name__,
                )

                while rows:

                    for row in rows:
                        row.__class__ = rowStruct
                        yield row

                    rows = fetch()

            else:

                while rows:

                    for row in rows:
                        yield row

                    rows = fetch()

        if onlyOneSet and self.nextset():
            raise self.tooMany



    def allSets(self):

        oneSet = self.__iter__

        yield list(oneSet(False))

        while self.nextset():
            yield list(oneSet(False))


    def nextset(self):
        return getattr(self._cursor, 'nextset', _nothing)()


    def justOne(self):

        i = iter(self)

        try:
            row = i.next()
        except StopIteration:
            raise self.tooFew

        try:
            next = i.next()
        except StopIteration:
            return row

        raise self.tooMany


    __invert__ = justOne









class ManagedConnection(TransactionComponent):

    __implements__ = IManagedConnection

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

        have = self.hasBinding

        if have('connection'):
            self.closeCursors()
            self._close()
            del self.connection

        if have('_closeASAP'):
            del self._closeASAP



    def finishTransaction(self, txnService, committed):

        super(ManagedConnection,self).finishTransaction(txnService, committed)

        if self._closeASAP:
            self.close()


    def _open(self):
        """Return new "real" connection to be saved as 'self.connection'"""
        raise NotImplementedError


    def _close(self):
        """Actions to take before 'del self.connection', if needed."""


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
        return self.txnSvc.getTimestamp()

    txnTime = binding.Once(txnTime)


    def joinTxn(self):
        """Join the current transaction, if not already joined"""
        return self.txnSvc


    def voteForCommit(self, txnService):
        self.closeCursors()

    def abortTransaction(self, txnService):
        self.closeCursors()





    _cursors = binding.New(WeakValueDictionary)


    def registerCursor(self,cursor):
        self._cursors[id(cursor)] = cursor


    def closeCursors(self):
        if self.hasBinding('_cursors'):
            for c in self._cursors.values():
                c.close()


    def __call__(self, *args, **kw):

        cursor = self.cursorClass(self, **kw)

        if args:
            cursor.execute(*args)

        return cursor


    cursorClass = DBCursor

















class LDAPCursor(DBCursor):

    """LDAP pseudo-cursor"""

    _cursor = None

    timeout      = -1
    msgid        = None
    bulkRetrieve = False

    disconnects = binding.bindSequence('import:ldap.SERVER_DOWN',)

    def close(self):

        if self.msgid is not None:
            self._conn.abandon(self.msgid)
            self.msgid = None

        super(LDAPCursor,self).close()


    def execute(self,dn,scope,filter='objectclass=*',attrs=None,dnonly=0):

        try:
            self.msgid = self._conn.search(dn,scope,filter,attrs,dnonly)

        except self.disconnects:
            self.errorDisconnect()


    def errorDisconnect(self):
        self.close()
        self.getParentComponent().close()
        raise
    

    def nextset(self):
        """LDAP doesn't do multi-sets"""
        return False


    def __iter__(self):

        msgid, timeout = self.msgid, self.timeout

        if msgid is None:
            raise ValueError("No operation in progress")

        getall = self.bulkRetrieve and 1 or 0
        fetch = self._conn.result

        ldapEntry = makeStructType('ldapEntry',
            [], __implements__ = IRow, __module__ = __name__,
        )

        newEntry = ldapEntry.fromMapping; restype = None

        while restype != 'RES_SEARCH_RESULT':

            try:
                restype, data = fetch(msgid, getall, timeout)

            except self.disconnects:
                self.errorDisconnect()

            if restype is None:               
                yield None  # for timeout errors

            for dn,m in data:

                m['dn']=dn

                try:
                    yield newEntry(m)                

                except ValueError:
                    map(ldapEntry.addField, m.keys())
                    yield newEntry(m)        

        # Mark us as done with this query
        self.msgid = None





























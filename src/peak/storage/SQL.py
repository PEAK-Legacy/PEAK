from __future__ import generators
from peak.api import *
from interfaces import *
from peak.util.Struct import makeStructType
from peak.util.imports import importObject
from connections import ManagedConnection, AbstractCursor
import sys

__all__ = [
    'SQLCursor', 'GenericSQL_URL', 'SQLConnection', 'SybaseConnection',
    'GadflyURL', 'GadflyConnection',
]


def _nothing():
    pass

def NullConverter(descr,value):
    return value






















class SQLCursor(AbstractCursor):

    """Iterable cursor bridge/proxy"""

    conn = binding.bindToParent()
    typeMap = binding.bindTo('conn/typeMap')


    def _cursor(self,d,a):
        return self._conn.cursor()

    _cursor = binding.Once(_cursor)


    def close(self):

        if self._hasBinding('_cursor'):
            self._cursor.close()
            del self._cursor

        super(SQLCursor,self).close()


    def __setattr__(self,attr,val):

        descr = getattr(self.__class__,attr,None)

        if hasattr(descr,'__set__'):
            descr.__set__(self,val)
        elif self._hasBinding(attr) or descr is not None:
            self._setBinding(attr,val)
        else:
            setattr(self._cursor,attr,val)


    def __getattr__(self,attr):
        return getattr(self._cursor,attr)




    def nextset(self):
        try:
            return getattr(self._cursor, 'nextset', _nothing)()
        except self.conn.NotSupportedError:
            pass


    def _setOutsideTxn(self,value):
        self._delBinding('setTxnState')
        self._setBinding('outsideTxn',value)

    def _getOutsideTxn(self):
        return self._getBinding('outsideTxn',False)

    outsideTxn = property(_getOutsideTxn,_setOutsideTxn)


    def setTxnState(self,d,a):
        if self.outsideTxn:
            return self.conn.assertUntransacted
        else:
            return self.conn.joinTxn

    setTxnState = binding.Once(setTxnState)

















    def execute(self, *args):

        self.setTxnState()

        try:

            # XXX need some sort of flags for timing/logging here
            # XXX perhaps best handled as cursor subclass(es) set on
            # XXX the SQLConnection?

            return self._cursor.execute(*args)

        except self.conn.Exceptions:

            __traceback_info__ = args

            LOG_ERROR(
                "Error executing SQL query", self, exc_info=True
            )

            self.conn.closeASAP()    # close connection after error
            raise



















    def __iter__(self, onlyOneSet=True):

        fetch = self._cursor.fetchmany
        rows = fetch()

        if rows:

            descr = self._cursor.description

            rowStruct = makeStructType('rowStruct',
                [d[0] for d in descr],
                __implements__ = IRow, __module__ = __name__,
            )

            typeMap = self.typeMap
            convert = [(typeMap.get(d[1],NullConverter),d) for d in descr]
            mkTuple = tuple.__new__


        while rows:

            for row in rows:
                yield mkTuple(rowStruct,
                    [ c(d,f) for (f,(c,d)) in zip(row,convert) ]
                )

            rows = fetch()


        if onlyOneSet and self.nextset():
            raise exceptions.TooManyResults










class SQLConnection(ManagedConnection):

    __implements__ = ISQLConnection

    def commitTransaction(self, txnService):
        self.connection.commit()

    def abortTransaction(self, txnService):
        self.connection.rollback()

    cursorClass = SQLCursor

    API = binding.requireBinding("DBAPI module for SQL connection")

    Error               = binding.bindTo("API/Error")
    Warning             = binding.bindTo("API/Warning")
    Exceptions          = binding.bindSequence("Error", "Warning")
    NotSupportedError   = binding.bindTo("API/NotSupportedError")
    Date                = binding.bindTo("API/Date")
    Time                = binding.bindTo("API/Time")
    Binary              = binding.bindTo("API/Binary")
    Timestamp           = binding.bindTo("API/Timestamp")
    DateFromTicks       = binding.bindTo("API/DateFromTicks")
    TimeFromTicks       = binding.bindTo("API/TimeFromTicks")
    TimestampFromTicks  = binding.bindTo("API/TimestampFromTicks")

    supportedTypes      = 'STRING','BINARY','NUMBER','DATETIME','ROWID'

    def typeMap(self, d, a):

        tm = {}
        ps = PropertyName('peak.sql_types').of(self)
        api = self.API

        for k in self.supportedTypes:
            tm[getattr(api,k)] = importObject(ps.get(k,NullConverter))

        return tm

    typeMap = binding.Once(typeMap)

class SybaseConnection(SQLConnection):

    API = binding.bindTo("import:Sybase")

    hostname  = binding.bindToProperty('Sybase.client.hostname',  default=None)
    appname   = binding.bindToProperty('Sybase.client.appname',   default=None)
    textlimit = binding.bindToProperty('Sybase.client.textlimit', default=None)
    textsize  = binding.bindToProperty('Sybase.client.textsize',  default=None)


    def _open(self):

        a = self.address

        db = self.API.connect(
            a.server, a.user, a.passwd, a.db, auto_commit=1, delay_connect=1
        )

        if self.hostname is not None:
            db.set_property(self.API.CS_HOSTNAME, self.hostname)

        if self.appname is not None:
            db.set_property(self.API.CS_APPNAME, str(self.appname))

        if self.textlimit is not None:
            db.set_property(self.API.CS_TEXTLIMIT, int(self.textlimit))

        db.connect()

        if self.textsize is not None:
            db.execute('set textsize %d' % int(self.textsize))

        return db


    def onJoinTxn(self, txnService):
        # Sybase doesn't auto-chain transactions...
        self.connection.begin()



    def txnTime(self,d,a):

        # First, ensure that we're in a transaction
        self.joinedTxn

        # Then retrieve the server's idea of the current time
        r = ~ self('SELECT getdate()')
        return r[0]

    txnTime = binding.Once(txnTime)































class PGSQLConnection(SQLConnection):

    API = binding.bindTo("import:pgdb")

    def _open(self):

        a = self.address

        return self.API.connect(
            host=a.server, database=a.db, user=a.user, password=a.passwd
        )


    def txnTime(self,d,a):
        self.joinedTxn              # Ensure that we're in a transaction,
        r = ~ self('SELECT now()')  # retrieve the server's idea of the time
        return r[0]

    txnTime = binding.Once(txnTime)

    supportedTypes = (
        'BINARY','BOOL','DATETIME','FLOAT','INTEGER',
        'LONG','MONEY','ROWID','STRING',
    )

















    def typeMap(self, d, a):

        tm = {}
        ps = PropertyName('peak.sql_types').of(self)
        api = self.API

        for k in self.supportedTypes:

            c = ps.get(k,NullConverter)

            for v in getattr(api,k).values:
                # We support either '.int4' or '.INTEGER' style properties
                tm[v] = importObject(ps.get(v,c))

        return tm

    typeMap = binding.Once(typeMap)
























class GadflyConnection(SQLConnection):

    API = binding.bindTo("import:gadfly")

    Error    = Exception    # Gadfly doesn't really do DBAPI...  Sigh.
    Warning  = Warning

    supportedTypes = ()

    def _open(self):
        a = self.address
        return self.API.gadfly(a.db, a.dir)

    def createDB(self):

        """Close, clear, and re-create the database"""

        self.close()
        a = self.address

        from gadfly import gadfly
        g = gadfly()
        g.startup(self.address.db, self.address.dir)
        g.commit()
        g.close()
















class GadflyURL(naming.ParsedURL):

    supportedSchemes = ('gadfly',)

    pattern = "(//)?(?P<db>[^@]+)@(?P<dir>.+)"

    def __init__(self, scheme=None, body=None, db=None, dir=None):
        self.setup(locals())

    def retrieve(self, refInfo, name, context, attrs=None):

        return GadflyConnection(
            context.creationParent, context.creationName,
            address = self
        )


























class GenericSQL_URL(naming.ParsedURL):

    supportedSchemes = ('sybase', 'pgsql')

    pattern = """(?x)
    (//)?
    (   # optional user:pass@
        (?P<user>[^:]+)
        (:(?P<passwd>[^@]+))?
        @
    )?

    (?P<server>[^/]+)
    (/(?P<db>.+))?
    """

    def __init__(self, scheme=None, body=None,
                 user=None, passwd=None, server=None, db=None,
        ):
        self.setup(locals())


    def retrieve(self, refInfo, name, context, attrs=None):

        return drivers[self.scheme](
            context.creationParent, context.creationName,
            address = self
        )



drivers = {
    'sybase': SybaseConnection,
    'pgsql':  PGSQLConnection,
}







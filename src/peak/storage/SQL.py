from __future__ import generators
from peak.api import *
from interfaces import *
from peak.util.Struct import makeStructType
from peak.util.imports import importObject
from connections import ManagedConnection, AbstractCursor, RowBase

__all__ = [
    'SQLCursor', 'GenericSQL_URL', 'SQLConnection', 'SybaseConnection',
    'GadflyURL', 'GadflyConnection'
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

        if hasattr(self.__class__,attr):
            super(SQLCursor,self).__setattr__(attr,val)

        elif self._hasBinding(attr):
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

















    logger = binding.bindToProperty('peak.logs.sql')

    __path = binding.Once(lambda s,d,a: binding.getComponentPath(s))

    def execute(self, *args):

        self.setTxnState()

        try:

            # XXX need some sort of flags for timing/logging here
            # XXX perhaps best handled as cursor subclass(es) set on
            # XXX the SQLConnection?

            return self._cursor.execute(*args)

        except self.conn.Exceptions:

            __traceback_info__ = args

            self.logger.exception(
                "%s: error executing SQL query: %s\n"
                "Traceback:",
                self.__path, args
            )

            self.conn.closeASAP()    # close connection after error
            raise













    def __iter__(self, onlyOneSet=True):

        fetch = self._cursor.fetchmany
        rows = fetch()

        if rows:

            descr = self._cursor.description

            rowStruct = makeStructType('rowStruct',
                [d[0] for d in descr], RowBase,
                __module__ = __name__,
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

    protocols.advise(
        instancesProvide=[ISQLConnection]
    )

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

class ValueBasedTypeConn(SQLConnection):

    def typeMap(self, d, a):

        tm = {}
        ps = PropertyName('peak.sql_types').of(self)
        api = self.API

        for k in self.supportedTypes:

            c = ps.get(k,NullConverter)

            for v in getattr(api,k).values:
                try:
                    v+''
                except:
                    tm[v] = c
                else:
                    # We support either '.int4' or '.INTEGER' style properties
                    tm[v] = importObject(
                        ps.get(PropertyName.fromString(v),c)
                    )

        return tm

    typeMap = binding.Once(typeMap)

















class SybaseConnection(ValueBasedTypeConn):

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































class PGSQLConnection(ValueBasedTypeConn):

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

















class SqliteConnection(ValueBasedTypeConn):

    API = binding.bindTo("import:sqlite")

    supportedTypes = (
        'DATE', 'INT', 'NUMBER', 'ROWID', 'STRING', 'TIME', 'TIMESTAMP',
    )

    def _open(self):
        return self.API.connect(self.address.getFilename())

    def listObjects(self, full=False, obtypes=NOT_GIVEN):
        addsel = addwhere = ''

        if full:
            addsel = ', rootpage, sql '

        if obtypes is not NOT_GIVEN:
            addwhere = 'where type in (%s)' % \
                ', '.join(["'%s'" % s for s in obtypes])
            
        return self('''select name as obname, type as obtype%s
            from SQLITE_MASTER %s''' % (addsel, addwhere))

    protocols.advise(
        instancesProvide=[ISQLIntrospector]
    )

    

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




class GadflyURL(naming.URL.Base):

    supportedSchemes = ('gadfly',)
    defaultFactory = 'peak.storage.SQL.GadflyConnection'

    class db(naming.URL.RequiredField):
        pass

    class dir(naming.URL.RequiredField):
        pass

    syntax = naming.URL.Sequence(
        ('//',), db, '@', dir
    )










from peak.naming.factories.openable import FileURL

class SqliteURL(FileURL):
    supportedSchemes = 'sqlite',
    defaultFactory = 'peak.storage.SQL.SqliteConnection'












class GenericSQL_URL(naming.URL.Base):

    supportedSchemes = {
        'sybase': 'peak.storage.SQL.SybaseConnection',
        'pgsql':  'peak.storage.SQL.PGSQLConnection',
    }

    defaultFactory = property(
        lambda self: self.supportedSchemes[self.scheme]
    )

    class user(naming.URL.Field):
        pass

    class passwd(naming.URL.Field):
        pass

    class server(naming.URL.RequiredField):
        pass

    class db(naming.URL.Field):
        pass

    syntax = naming.URL.Sequence(
        ('//',), (user, (':', passwd), '@'), server, ('/', db)
    )
















class OracleURL(naming.URL.Base):

    supportedSchemes = {
        'cxoracle':  'peak.storage.SQL.CXOracleConnection',
        'dcoracle2': 'peak.storage.SQL.DCOracle2Connection',
    }

    defaultFactory = property(
        lambda self: self.supportedSchemes[self.scheme]
    )

    class user(naming.URL.Field):
        pass

    class passwd(naming.URL.Field):
        pass

    class server(naming.URL.RequiredField):
        pass

    syntax = naming.URL.Sequence(
        ('//',), (user, (':', passwd), '@'), server, ('/',)
    )



class CXOracleConnection(SQLConnection):

    API = binding.bindTo("import:cx_Oracle")

    def _open(self):
        a = self.address

        return self.API.connect(a.user, a.passwd, a.server)


    def txnTime(self,d,a):
        self.joinedTxn              # Ensure that we're in a transaction,
        r = ~ self('SELECT SYSDATE FROM DUAL')  # retrieve the server's idea of the time
        return r[0]

    txnTime = binding.Once(txnTime)

    supportedTypes = (
        'BINARY','CURSOR','DATETIME','FIXED_CHAR','LONG_BINARY',
        'LONG_STRING','NUMBER','ROWID','STRING',
    )



class DCOracle2Connection(ValueBasedTypeConn):

    API = binding.bindTo("import:DCOracle2")

    def _open(self):
        a = self.address

        return self.API.connect(
            user=a.user, password=a.passwd, database=a.server,
        )


    def txnTime(self,d,a):
        self.joinedTxn              # Ensure that we're in a transaction,
        r = ~ self('SELECT SYSDATE FROM DUAL')  # retrieve the server's idea of the time
        return r[0]

    txnTime = binding.Once(txnTime)

    supportedTypes = (
        'BINARY','DATETIME','NUMBER','ROWID','STRING',
    )


from __future__ import generators
from peak.api import *
from interfaces import *
from peak.util.Struct import makeStructType
from peak.util.imports import importObject
from connections import ManagedConnection, AbstractCursor

__all__ = [
    'SQLCursor', 'GenericSQL_URL', 'SQLConnection', 'SybaseConnection',
    'GadflyURL', 'GadflyConnection',
]


def _nothing():
    pass

def NullConverter(name,descr,value):
    return value























class SQLCursor(AbstractCursor):

    """Iterable cursor bridge/proxy"""


    def _cursor(self,d,a):
        return self._conn.cursor()

    _cursor = binding.Once(_cursor)


    def close(self):

        if self._hasBinding('_cursor'):
            self._cursor.close()
            del self._cursor

        super(SQLCursor,self).close()

            
    def __setattr__(self,attr,val):
        if self._hasBinding(attr) or hasattr(self.__class__,attr):
            self._setBinding(attr,val)
        else:
            setattr(self._cursor,attr,val)


    def __getattr__(self,attr):
        return getattr(self._cursor,attr)


    def nextset(self):
        return getattr(self._cursor, 'nextset', _nothing)()








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

                mkTuple = tuple.__new__

                while rows:

                    for row in rows:
                        yield mkTuple(rowStruct,row)

                    rows = fetch()

            else:

                while rows:

                    for row in rows:
                        yield row

                    rows = fetch()

        if onlyOneSet and self.nextset():
            raise exceptions.TooManyResults


class SQLConnection(ManagedConnection):

    def commitTransaction(self, txnService):
        self.connection.commit()

    def abortTransaction(self, txnService):
        self.connection.rollback()

    cursorClass = SQLCursor

    API = binding.requireBinding("DBAPI module for SQL connection")

    Error               = binding.bindTo("API/Error")
    Warning             = binding.bindTo("API/Warning")

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
        ps = naming.PropertyName('peak.sql_types').of(self)
        api = self.API

        for k in self.supportedTypes:
            tm[getattr(api,k)] = importObject(ps.get(k,NullConverter))

        return tm

    typeMap = binding.Once(typeMap)




class SybaseConnection(SQLConnection):

    API = binding.bindTo("Sybase")

    def _open(self):
        a = self.address
        return self.API.connect(a.server, a.user, a.passwd, a.db)
            
    def onJoinTxn(self, txnService):
        # Sybase doesn't auto-chain transactions...
        self.connection.begin()

    def txnTime(self,d,a):

        # First, ensure that we're in a transaction
        self.txnSvc

        # Then retrieve the server's idea of the current time
        r = ~ self('SELECT getdate()')
        return r[0]

    txnTime = binding.Once(txnTime)



















class GadflyConnection(SQLConnection):

    API = binding.bindTo("gadfly")

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

    _supportedSchemes = ('gadfly',)
    
    _defaultScheme = 'gadfly'

    pattern = "(//)?(?P<db>[^@]+)@(?P<dir>.+)"

    def __init__(self, url=None, db=None, dir=None):
        self.setup(locals())
    
    def retrieve(self, refInfo, name, context, attrs=None):

        return GadflyConnection(
            context.creationParent,
            address = self
        )


class GenericSQL_URL(naming.ParsedURL):

    _supportedSchemes = ('sybase',)

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

    def __init__(self, url=None,
                 user=None, passwd=None, server=None, db=None,
        ):
        self.setup(locals())


    def retrieve(self, refInfo, name, context, attrs=None):

        return drivers[self.scheme](
            context.creationParent,
            address = self
        )



drivers = {
    'sybase': SybaseConnection
}

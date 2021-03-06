"""Mock implementation of a DBAPI 2.0 module"""

from __future__ import generators

apilevel = '2.0'
threadsafety = 0
paramstyle = 'qmark'

from peak.util.symbols import NOT_GIVEN

class _cursor:

    def __init__(self,conn):
        self._conn = conn

    def close(self):
        pass

    description = None

    _next = None

    def execute(self,operation,parameters=None):
        data, desc = self._conn._execute(self,operation,parameters)
        self._next = iter(data).next
        self.description = desc

    # TODO: executemany, rowcount, callproc, nextset, setinputsizes,
    #       setoutputsize

    # EXTENSIONS: rownumber, connection, scroll, messages, next, __iter__,
    #             lastrowid, errorhandler









    def fetchone(self):

        if self.description is None:
            raise ProgrammingError("Fetch without results")

        if self._next is not None:
            try:
                return self._next()
            except StopIteration:
                del self._next


    arraysize = 1

    def _fetch(self,size):

        if size is None:
            size = self.arraysize

        if self.description is None:
            raise ProgrammingError("Fetch without results")

        next = self._next

        while size and next is not None:
            try:
                yield next()
            except StopIteration:
                del self._next
                break
            size -= 1

    def fetchmany(self,size=None):
        return list(self._fetch(size))

    def fetchall(self):
        return list(self._fetch(-1))




class connect:
    verbose = False

    def __init__(self):
        self._expected = []
        self._provide = []
        self._when = {}

    def close(self):
        self._verifyFinished()

    def commit(self):
        self._execute(None,"*COMMIT",None)

    def rollback(self):
        self._execute(None,"*ROLLBACK",None)

    def cursor(self):
        return _cursor(self)

    def expect(self,operation,parameters=None):
        """Expect a cursor to execute 'operation' with 'parameters'"""
        self._verifyFinished()
        self.alsoExpect(operation,parameters)

    def alsoExpect(self,operation,parameters=None):
        """Expect additional operation(s)"""
        self._expected.append((operation,parameters))

    def provide(self,data,description=()):
        """Provide 'data' and 'description' in reply to next operation"""
        if len(self._provide)>=len(self._expected):
            raise ProgrammingError(
                "More results provided than queries expected"
            )
        self._provide.append((data,description))





    def when(self,
        operation, parameters=NOT_GIVEN, data=None, description=(),
        callback=NOT_GIVEN
    ):
        if parameters is not None and parameters is not NOT_GIVEN:
            parameters = tuple(parameters)
        if data is None: data = []
        self._when[(operation,parameters)] = (data, description), callback

    def _verifyFinished(self):
        if self._expected:
            raise AssertionError("Un-executed queries", self._expected)

    def _execute(self,cursor,operation,parameters):
        if self.verbose:
            print operation, parameters
        provide, cb, key, found = ([], None), NOT_GIVEN, parameters, True
        if parameters is not None:
            key = tuple(parameters)
        if (operation, key) in self._when:
            provide, cb = self._when[operation, key]
        elif (operation, NOT_GIVEN) in self._when:
            provide, cb = self._when[operation, NOT_GIVEN]
        else:
            found = False
        if self._expected:
            expected_op, expected_params = self._expected[0]
            if operation==expected_op and (
                parameters!=expected_params or expected_params is not NOT_GIVEN
            ):
                self._expected.pop(0)
                if self._provide:
                    provide = self._provide.pop(0)
            elif not found:                
                self._expected.pop(0)
                raise AssertionError(
                    "Expected: %s; Got: %s" %
                        ((operation,parameters), (expected_op, expected_params))
                )
        elif not found:
            raise AssertionError("Unexpected query", operation, parameters)
        if cb is not NOT_GIVEN:
            return cb(self, operation, parameters, provide)
        return provide


# DBAPI Exceptions

class Error(StandardError):
    pass

class Warning(StandardError):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class DataError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class InternalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass





# DBAPI Constructors

def Binary(text):
    return text

def Date(year,month,day):
    import datetime
    return datetime.date(year,month,day)

def Time(hour,minute,second):
    import datetime
    return datetime.time(hour,minute,second)

def Timestamp(year,month,day,hour,minute,second):
    import datetime
    return datetime.datetime(year,month,day,hour,minute,second)

def DateFromTicks(ticks):
    from time import localtime
    return Date(*localtime(ticks)[:3])

def TimeFromTicks(ticks):
    from time import localtime
    return Time(*localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    from time import localtime
    return Timestamp(*localtime(ticks)[:6])













# DBAPI Type Objects

from peak.util.symbols import Symbol

STRING   = Symbol("STRING",   __name__)
NUMBER   = Symbol("NUMBER",   __name__)
BINARY   = Symbol("BINARY",   __name__)
DATETIME = Symbol("DATETIME", __name__)
ROWID    = Symbol("ROWID",    __name__)

































from __future__ import generators
from peak.api import *
from interfaces import *
from peak.util.Struct import makeStructType

__all__ = [
    'SQLCursor',
]


def _nothing():
    pass





























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




from unittest import TestCase, makeSuite, TestSuite
import peak.util.mockdb as mockdb

class DBAPITest(TestCase):

    API      = mockdb
    connArgs = ()
    connKw   = {}
    cursor   = None
    conn     = None

    def _connect(self):
        return self.API.connect(*self.connArgs,**self.connKw)

    def tearDown(self):
        if self.cursor is not None:
            self.cursor.close()
            del self.cursor
        if self.conn is not None:
            self.conn.close()
            del self.conn




















class DBAPIModuleTests(DBAPITest):

    def testConnect(self):
        assert hasattr(self.API,'connect')
        assert callable(self.API.connect)

    def testMetadata(self):
        assert self.API.apilevel in ('1.0','2.0')
        assert self.API.threadsafety in (0,1,2,3)
        assert self.API.paramstyle in (
            'qmark','numeric','named','format','pyformat'
        )

    def testExceptions(self):

        for err in self.API.Warning, self.API.Error:
            assert issubclass(err,StandardError)

        assert issubclass(self.API.InterfaceError,self.API.Error)
        assert issubclass(self.API.DatabaseError, self.API.Error)

        for errname in (
            "DataError OperationalError IntegrityError"
            " InternalError ProgrammingError NotSupportedError".split()
        ):
            assert issubclass(getattr(self.API,errname),self.API.DatabaseError)

    def testTypeObjects(self):
        assert self.API.STRING <> self.API.NUMBER
        assert self.API.BINARY <> self.API.DATETIME
        assert self.API.ROWID <>  self.API.DATETIME










    def testConstructors(self):

        assert self.API.Binary("xyz") == self.API.Binary("xyz")
        assert self.API.Date(2003,11,14) == self.API.Date(2003,11,14)
        assert self.API.Time(23,59,59) == self.API.Time(23,59,59)
        assert self.API.Timestamp(2003,11,14,23,59,59) == \
               self.API.Timestamp(2003,11,14,23,59,59)

        from time import localtime
        for ticks in 1024,57943759,574385:
            assert self.API.DateFromTicks(ticks) == \
                   self.API.Date(*localtime(ticks)[:3])
            assert self.API.TimeFromTicks(ticks) == \
                   self.API.Time(*localtime(ticks)[3:6])
            assert self.API.TimestampFromTicks(ticks) == \
                   self.API.Timestamp(*localtime(ticks)[:6])

























class ConnectionTests(DBAPITest):

    def setUp(self):
        self.conn = self._connect()

    def testConnectionAttrs(self):
        assert callable(self.conn.close)
        assert callable(self.conn.commit)
        assert callable(self.conn.rollback)
        assert callable(self.conn.cursor)


class CursorTests(DBAPITest):

    def setUp(self):
        self.conn = self._connect()
        self.cursor = self.conn.cursor()

    def testEmptyFetches(self):
        self.assertRaises(self.API.Error, self.cursor.fetchone)
        self.assertRaises(self.API.Error, self.cursor.fetchmany)
        self.assertRaises(self.API.Error, self.cursor.fetchall)


class MockTests(DBAPITest):

    def setUp(self):
        self.conn = self._connect()
        self.cursor = self.conn.cursor()

    def testExpectFails(self):
        self.conn.expect("select * from test")
        self.assertRaises(AssertionError,
            self.cursor.execute, "select * from foo"
        )

    def testExpectSucceeds(self):
        self.conn.expect("select * from test")
        self.cursor.execute("select * from test")


    def testMultiExpect(self):
        # Doing more queries than expected should raise an error
        self.conn.expect("select * from test")
        self.cursor.execute("select * from test")
        self.assertRaises(AssertionError,
            self.cursor.execute, "select * from test"
        )

        # Doing 'require' without being caught up should raise an error
        self.conn.expect("select * from test")
        self.assertRaises(AssertionError,
            self.conn.expect, "select * from test"
        )

        # Since we're still expecting the missing query, trying to close
        # should also raise an error
        self.assertRaises(AssertionError, self.conn.close)

        # Clean up so tearDown doesn't fail.
        self.cursor.execute("select * from test")


    def testAlsoExpect(self):
        # alsoExpect should allow multiple queries
        self.conn.expect("select * from blah",(1,2,3))
        self.conn.alsoExpect("select * from blah",(4,5,6))
        self.cursor.execute("select * from blah",(1,2,3))
        self.cursor.execute("select * from blah",(4,5,6))

        # Doing fewer queries than expected should raise an error
        self.conn.expect("select * from blah",(1,2,3))
        self.conn.alsoExpect("select * from blah",(4,5,6))
        self.cursor.execute("select * from blah",(1,2,3))
        self.assertRaises(AssertionError,
            self.conn.expect, "select * from test"
        )

        # Clear the pending query
        self.cursor.execute("select * from blah",(4,5,6))


    def testProvideAndFetch(self):
        data = [(x,) for x in range(100)]
        self.conn.expect('select * from blah')
        self.conn.provide(data)
        self.cursor.execute('select * from blah')
        self.assertEqual(self.cursor.fetchone(), data[0])
        self.assertEqual(self.cursor.fetchmany(50), data[1:51])
        self.cursor.arraysize = 10
        self.assertEqual(self.cursor.fetchmany(), data[51:61])
        self.assertEqual(self.cursor.fetchall(), data[61:])
        self.assertEqual(self.cursor.fetchmany(50), [])
        self.assertEqual(self.cursor.fetchone(), None)
        self.assertEqual(self.cursor.fetchall(), [])

    def testEmptyFetches(self):
        self.conn.expect('delete foo')
        self.conn.provide([],None)
        self.cursor.execute('delete foo')
        self.assertRaises(self.API.Error, self.cursor.fetchone)
        self.assertRaises(self.API.Error, self.cursor.fetchmany)
        self.assertRaises(self.API.Error, self.cursor.fetchall)

    def testMultiProvide(self):
        data1 = [(x,) for x in range(100)]
        data2 = [(x,) for x in range(50)]
        self.conn.expect('select * from blah')
        self.conn.provide(data1)
        self.conn.alsoExpect('select * from blah')
        self.conn.provide(data2)
        self.cursor.execute('select * from blah')
        self.assertEqual(self.cursor.fetchall(), data1)
        self.cursor.execute('select * from blah')
        self.assertEqual(self.cursor.fetchall(), data2)








    def testWhen(self):
        log = []
        def log_call(conn, operation, parameters, provide):
            self.failUnless(conn is self.conn)
            log.append((operation, parameters, provide))
            return provide
        def check_modify(conn, operation, parameters, provide):
            return [(42,)], (('Bar,'),)

        self.conn.when('foo', data=[(1,)], description=(('Foo,'),))
        self.conn.when('bar ?', ['x'], data=[(47,),(52,)], callback=log_call)
        self.conn.when('baz ?', callback=log_call)
        self.conn.when('fetch', callback=check_modify)

        self.cursor.execute('fetch')
        self.assertEqual(self.cursor.description, (('Bar,'),))
        self.assertEqual(self.cursor.fetchall(), [(42,)])       
        self.cursor.execute('foo')
        self.assertEqual(self.cursor.description, (('Foo,'),))
        self.assertEqual(self.cursor.fetchall(), [(1,)])

        self.assertRaises(AssertionError, self.cursor.execute, 'bar ?', [42])

        self.conn.expect('ping!')
        self.conn.provide([('nee',)], (('say',),))
        self.conn.alsoExpect('pong', [42])

        self.cursor.execute('baz ?')
        self.cursor.execute('baz ?', [99])

        self.cursor.execute('ping!')
        self.assertEqual(self.cursor.description, (('say',),))
        self.assertEqual(self.cursor.fetchall(), [('nee',)])
        
        self.cursor.execute('bar ?', ['x'])
        self.cursor.execute('pong', [42])
        self.assertEqual(log, [
            ('baz ?', None, ([], ())), ('baz ?', [99], ([], ())),
            ('bar ?', ['x'], ([(47,),(52,)], ()))
        ])        

    def testExpectPrecedence(self):
        # expect->provide should match even if a when matches also
        log = []
        def log_call(conn, operation, parameters, provide):
            self.failUnless(conn is self.conn)
            log.append((operation, parameters, provide))
            return provide

        self.conn.when('bar ?', ['x'], data=[(47,),(52,)], callback=log_call)
        self.conn.expect('bar ?', ['x'])
        self.conn.provide([])
        self.cursor.execute('bar ?', ['x'])
        self.assertEqual(log, [('bar ?', ['x'], ([], ()))])        


    def testCommitAndRollback(self):

        self.assertRaises(AssertionError, self.conn.commit)
        self.assertRaises(AssertionError, self.conn.rollback)

        self.conn.expect('*COMMIT')
        self.conn.commit()

        self.conn.expect('*ROLLBACK')
        self.conn.rollback()
















TestClasses = (
    DBAPIModuleTests, ConnectionTests, CursorTests, MockTests
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)
































import os
import unittest

from ZODB.MappingStorage import DB, MappingStorage
from ZODB.utils import U64
import ZODB.DB

from Persistence.PersistentDict import PersistentDict
from Persistence.Module import \
     PersistentModuleManager, PersistentModuleRegistry, \
     PersistentModuleImporter, PersistentPackage
from Persistence import tests

from Transaction import get_transaction

# snippets of source code used by testModules
foo_src = """\
import string
x = 1
def f(y):
    return x + y
"""
quux_src = """\
from foo import x
def f(y):
    return x + y
"""
side_effect_src = """\
x = 1
def inc():
    global x
    x += 1
    return x
"""
builtin_src = """\
x = 1, 2, 3
def f():
    return len(x)
"""
nested_src = """\
def f(x):
    def g(y):
        def z(z):
            return x + y + z
        return x + y
    return g

g = f(3)
"""
closure_src = """\
def f(x):
    def g(y):
        return x + y
    return g

inc = f(1)
"""

class TestPersistentModuleImporter(PersistentModuleImporter):

    def __init__(self, registry):
        self._registry = registry
        self._registry._p_activate()

    def __import__(self, name, globals={}, locals={}, fromlist=[]):
        mod = self._import(self._registry, name, self._get_parent(globals),
                           fromlist)
        if mod is not None:
            return mod
        return self._saved_import(name, globals, locals, fromlist)

class TestModule(unittest.TestCase):

    def setUp(self):
        self.db = DB()
        self.root = self.db.open().root()
        self.registry = PersistentModuleRegistry()
        self.importer = TestPersistentModuleImporter(self.registry)
        self.importer.install()
        self.root["registry"] = self.registry
        get_transaction().commit()
        _dir, _file = os.path.split(tests.__file__)
        self._pmtest = os.path.join(_dir, "_pmtest.py")

    def tearDown(self):
        self.importer.uninstall()

    def testModule(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("pmtest", open(self._pmtest).read())
        get_transaction().commit()
        self.assert_(self.registry.findModule("pmtest"))
        import pmtest
        pmtest._p_deactivate()
        self.assertEqual(pmtest.a, 1)
        pmtest.f(4)

    def testUpdate(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("pmtest", "def f(x): return x")
        get_transaction().commit()
        import pmtest
        self.assertEqual(pmtest.f(3), 3)
        copy = pmtest.f
        mgr.update("def f(x): return x + 1")
        get_transaction().commit()
        pmtest._p_deactivate()
        self.assertEqual(pmtest.f(3), 4)
        self.assertEqual(copy(3), 4)

    def testModules(self):
        foomgr = PersistentModuleManager(self.registry)
        foomgr.new("foo", foo_src)
        # quux has a copy of foo.x
        quuxmgr = PersistentModuleManager(self.registry)
        quuxmgr.new("quux", quux_src)
        # bar has a reference to foo
        barmgr = PersistentModuleManager(self.registry)
        barmgr.new("bar", "import foo")
        # baz has reference to f and copy of x,
        # remember the the global x in f is looked up in foo
        bazmgr = PersistentModuleManager(self.registry)
        bazmgr.new("baz", "from foo import *")
        import foo, bar, baz, quux
        self.assert_(foo._p_oid is None)
        get_transaction().commit()
        self.assert_(foo._p_oid)
        self.assert_(bar._p_oid)
        self.assert_(baz._p_oid)
        self.assert_(quux._p_oid)
        self.assertEqual(foo.f(4), 5)
        self.assertEqual(bar.foo.f(4), 5)
        self.assertEqual(baz.f(4), 5)
        self.assertEqual(quux.f(4), 5)
        self.assert_(foo.f is bar.foo.f)
        self.assert_(foo.f is baz.f)
        foo.x = 42
        self.assertEqual(quux.f(4), 5)
        get_transaction().commit()
        self.assertEqual(quux.f(4), 5)
        foo._p_deactivate()
        # foo is deactivated, which means its dict is empty when f()
        # is activated, how do we guarantee that foo is also
        # activated?
        self.assertEqual(baz.f(4), 46)
        self.assertEqual(bar.foo.f(4), 46)
        self.assertEqual(foo.f(4), 46)

    def testFunctionAttrs(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("foo", foo_src)
        import foo
        A = foo.f.attr = "attr"
        self.assertEqual(foo.f.attr, A)
        get_transaction().commit()
        self.assertEqual(foo.f.attr, A)
        foo.f._p_deactivate()
        self.assertEqual(foo.f.attr, A)
        del foo.f.attr
        self.assertRaises(AttributeError, getattr, foo.f, "attr")
        foo.f.func_code

    def testFunctionSideEffects(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("effect", side_effect_src)
        import effect
        effect.inc()
        get_transaction().commit()
        effect.inc()
        self.assert_(effect._p_changed)

    def testBuiltins(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("test", builtin_src)
        get_transaction().commit()
        import test
        self.assertEqual(test.f(), len(test.x))
        test._p_deactivate()
        self.assertEqual(test.f(), len(test.x))

    def testNested(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("nested", nested_src)
        get_transaction().commit()
        import nested
        self.assertEqual(nested.g(5), 8)

    def testLambda(self):
        mgr = PersistentModuleManager(self.registry)
        # test a lambda that contains another lambda as a default
        src = "f = lambda x, y = lambda: 1: x + y()"
        mgr.new("test", src)
        get_transaction().commit()
        import test
        self.assertEqual(test.f(1), 2)

##    def testClosure(self):

##        # This test causes a seg fault because ???
        
##        self.importer.module_from_source("closure", closure_src)
##        get_transaction().commit()
##        import closure
##        self.assertEqual(closure.inc(5), 6)
##        closure._p_deactivate()
##        self.assertEqual(closure.inc(5), 6)

    def testClass(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("foo", src)
        get_transaction().commit()
        import foo
        obj = foo.Foo()
        obj.m()
        self.root["m"] = obj
        get_transaction().commit()
        foo._p_deactivate()
        o = foo.Foo()
        i = o.m()
        j = o.m()
        self.assertEqual(i + 1, j)

    def testPackage(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.B.C", "def f(x): return x")
        get_transaction().commit()

        import A.B.C
        self.assert_(isinstance(A, PersistentPackage))
        self.assertEqual(A.B.C.f("A"), "A")

        mgr = PersistentModuleManager(self.registry)
        self.assertRaises(ValueError,
                          mgr.new, "A.B", "def f(x): return x + 1")

        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.B.D", "def f(x): return x")
        get_transaction().commit()

        from A.B import D
        self.assert_(hasattr(A.B.D, "f"))

    def testPackageInit(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.B.C", "def f(x): return x")
        get_transaction().commit()

        import A.B.C

        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.B.__init__", "x = 2")
        get_transaction().commit()

        import A.B
        self.assert_(hasattr(A.B, "C"))
        self.assertEqual(A.B.x, 2)

        mgr = PersistentModuleManager(self.registry)
        self.assertRaises(ValueError,
                          mgr.new, "A.__init__.D", "x = 2")

    def testPackageRelativeImport(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.B.C", "def f(x): return x")
        get_transaction().commit()

        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.Q", "from B.C import f")
        get_transaction().commit()

        import A.Q
        self.assertEqual(A.B.C.f, A.Q.f)

        mgr.update("import B.C")
        get_transaction().commit()

        self.assertEqual(A.B.C.f, A.Q.B.C.f)

        try:
            import A.B.Q
        except ImportError:
            pass

    def testImportAll(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.B.C", """__all__ = ["a", "b"]; a, b, c = 1, 2, 3""")
        get_transaction().commit()

        d = {}
        exec "from A.B.C import *" in d
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        self.assertRaises(KeyError, d.__getitem__, "c")

        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.B.D", "from C import *")
        get_transaction().commit()

        import A.B.D
        self.assert_(hasattr(A.B.D, "a"))
        self.assert_(hasattr(A.B.D, "b"))
        self.assert_(not hasattr(A.B.D, "c"))

        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.__init__", """__all__ = ["B", "F"]""")
        get_transaction().commit()

        mgr = PersistentModuleManager(self.registry)
        mgr.new("A.F", "spam = 1")
        get_transaction().commit()

        import A
        self.assertEqual(A.F.spam, 1)

class TestModuleReload(unittest.TestCase):
    """Test reloading of modules"""

    def setUp(self):
        self.storage = MappingStorage()
        self.open()
        _dir, _file = os.path.split(tests.__file__)
        self._pmtest = os.path.join(_dir, "_pmtest.py")

    def open(self):
        # open a new db and importer from the storage
        self.db = ZODB.DB.DB(self.storage)
        self.root = self.db.open().root()
        self.registry = self.root.get("registry")
        if self.registry is None:
            self.root["registry"] = self.registry = PersistentModuleRegistry()
        self.importer = TestPersistentModuleImporter(self.registry)
        self.importer.install()
        get_transaction().commit()

    def close(self):
        self.importer.uninstall()
        self.db.close()

    def testModuleReload(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("pmtest", open(self._pmtest).read())
        get_transaction().commit()
        import pmtest
        pmtest._p_deactivate()
        self.assertEqual(pmtest.a, 1)
        pmtest.f(4)
        self.close()
        pmtest._p_deactivate()
        self.importer.uninstall()
        self.open()
        del pmtest
        import pmtest

    def testClassReload(self):
        mgr = PersistentModuleManager(self.registry)
        mgr.new("foo", src)
        get_transaction().commit()
        import foo
        obj = foo.Foo()
        obj.m()
        self.root["d"] = d = PersistentDict()
        d["m"] = obj
        get_transaction().commit()
        self.close()
        foo._p_deactivate()
        self.importer.uninstall()
        self.open()
        del foo
        import foo

def test_suite():
    s = unittest.TestSuite()
    for klass in TestModule, TestModuleReload:
        s.addTest(unittest.makeSuite(klass))
    return s

src = """\
from Persistence.Class import PersistentBaseClass

class Foo(PersistentBaseClass):
    def __init__(self):
        self.x = id(self)
    def m(self):
        self.x += 1
        return self.x
"""

"""Integration/acceptance tests for SEF.SimpleModel, etc."""

from unittest import TestCase, makeSuite, TestSuite
from TW.SEF.Queries import ANY, Equals
from TW.UML.Model import UMLClass


class UMLTest(TestCase):

    def setUp(self):
        self.m = m = UMLClass()
        self.pkg = m.newElement('Package')

    def checkNameSet(self):
        pkg=self.pkg
        pkg.name.set('SomePackage')
        assert pkg.name()=='SomePackage'
        
    def checkAdd(self):
        pkg = self.pkg
        oe = pkg.ownedElements
        Class = self.m.newElement('Class')
        assert oe.isEmpty()
        oe.addItem(Class)
        assert not oe.isEmpty()
        v = oe()
        assert len(v)==1
        assert v[0] is Class

    def checkDel(self):
        self.checkAdd()
        pkg = self.pkg
        oe = pkg.ownedElements
        oe.removeItem(oe()[0])
        assert oe.isEmpty()
        assert len(oe())==0





class QueryTests(TestCase):

    def setUp(self):
        self.m = m = UMLClass()
        self.pkg = pkg = m.newElement('Package')
        pkg.name.set('SomePackage')
        self.klass = klass = self.m.newElement('Class')
        klass.name.set('FooClass')
        pkg.ownedElements.addItem(klass)
        
        
    def checkNameGet(self):
        for obj in self.pkg, self.klass:
            names = obj.Get('name')
            assert len(names)==1
            assert names[0]==obj.name(), (names[0],obj.name())

    def checkSelfWhere(self):
        for obj in self.pkg, self.klass:
            where = obj.Where(ANY('name',Equals(obj.name())))
            assert len(where)==1

    def checkContentsGet(self):
        pkg = self.pkg
        klass = self.klass
        oe = pkg.Get('ownedElements')
        assert len(oe)==1
        ns = klass.Get('namespace')
        assert len(ns)==1

    def checkContentsWhere(self):
        pkg = self.pkg
        klass = self.klass
        oe = pkg.Get('ownedElements').Where(ANY('name',Equals('FooClass')))
        assert len(oe)==1
        ns = klass.Get('namespace').Where(ANY('name',Equals('SomePackage')))
        assert len(ns)==1
        



LoadedUML = None

class XMILoad(TestCase):

    def checkLoad(self):
        global LoadedUML
        self.m = m = LoadedUML = UMLClass()
        from os import path
        m.roots = m.importFromXMI(path.join(path.split(__file__)[0],'MetaMeta.xml'))

        
class XMITests(TestCase):

    def setUp(self):
        m = LoadedUML
        from TW.SEF.Queries import NodeList
        self.roots = NodeList(m.roots)
        self.root = self.roots[0]
        mm = self.mm = self.root.ownedElements.Where(ANY('name',Equals('Meta-MetaModel')))

    def checkModel(self):
        assert self.root.name()=='Data'
        
    def checkSubModel(self):
        assert self.mm
        assert self.mm.Get('namespace').Get('name')==['Data']

    def checkContents(self):
        assert self.mm.Get('ownedElements').Where(ANY('name',Equals('AttributeKind')))
        assert not self.mm.Get('ownedElements').Where(ANY('name',Equals('foobar')))

    def checkSuperclasses(self):
        enum = self.roots.Get('ownedElements*').Where(ANY('name',Equals('enumeration')))
        assert len(enum)==1
        sc = enum.Get('superclasses')
        assert len(sc)==1
        assert sc.Get('name')==['AttributeKind'],sc.Get('name')
        
        sc = enum.Get('superclasses*').Get('name'); sc.sort()
        assert sc==['AttributeKind','PackageElement'], sc

TestClasses = (
    UMLTest, QueryTests, XMILoad, XMITests
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))
    return TestSuite(s)


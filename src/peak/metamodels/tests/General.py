"""Integration/acceptance tests for SEF.SimpleModel, etc."""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.model.queries import *

class UMLTest(TestCase):

    def setUp(self):
        global UMLClass
        from peak.metamodels.uml.Model import UMLClass
        self.m = m = UMLClass()
        self.pkg = m.Package()

    def checkNameSet(self):
        pkg=self.pkg
        pkg.name = 'SomePackage'
        assert pkg.name=='SomePackage'
        
    def checkAdd(self):
        pkg = self.pkg
        Class = self.m.Class()
        assert not pkg.ownedElements
        pkg.addOwnedElements(Class)
        v = pkg.ownedElements
        assert len(v)==1
        assert v[0] is Class

    def checkDel(self):
        self.checkAdd()
        pkg = self.pkg
        oe = pkg.ownedElements
        pkg.removeOwnedElements(oe[0])
        assert len(oe)==0

    def checkImm(self):
        mr = UMLClass.MultiplicityRange(lower=0,upper=-1)
        m = UMLClass.Multiplicity(ranges=[mr])
        assert m.ranges[0].lower==0
        assert UMLClass.Multiplicity().ranges==[]

class QueryTests(TestCase):

    def setUp(self):
        self.m = m = UMLClass()
        self.pkg = pkg = m.Package()
        pkg.name = 'SomePackage'
        self.klass = klass = self.m.Class()
        klass.name = 'FooClass'
        pkg.addOwnedElements(klass)
        
        
    def checkNameGet(self):
        for obj in self.pkg, self.klass:
            names = list(query([obj])['name'])
            assert len(names)==1, list(names)
            assert names[0]==obj.name, (names[0],obj.name)

    def checkSelfWhere(self):
        for obj in self.pkg, self.klass:
            where = list(query([obj], ANY('name',EQ(obj.name))))
            assert len(where)==1

    def checkContentsGet(self):
        pkg = self.pkg
        klass = self.klass
        oe = list(query([pkg])['ownedElements'])
        assert len(oe)==1, oe
        ns = list(query([klass])['namespace'])
        assert len(ns)==1

    def checkContentsWhere(self):
        pkg = self.pkg
        klass = self.klass
        oe = list(query([pkg])['ownedElements'][ANY('name',EQ('FooClass'))])
        assert len(oe)==1, oe
        ns = list(query([klass])['namespace'][ANY('name',EQ('SomePackage'))])
        assert len(ns)==1
        



LoadedUML = None

class XMILoad(TestCase):
    def checkLoad(self):
        global LoadedUML
        self.m = m = LoadedUML = UMLClass()
        from os import path
        m.roots = m.importFromXMI(
            config.fileNearModule(__name__,'MetaMeta.xml')
        )
        
class XMITests(TestCase):

    def setUp(self):
        m = LoadedUML
        self.roots = query(m.roots)
        self.root = list(self.roots)[0]
        mm = self.mm = query([self.root])['ownedElements'][
            ANY('name',EQ('Meta-MetaModel'))
        ]

    def checkModel(self):
        assert self.root.name=='Data'
        
    def checkSubModel(self):
        assert self.mm; l = list(self.mm['namespace']['name'])
        assert l==['Data'], l

    def checkContents(self):
        assert list(self.mm['ownedElements'][ANY('name',EQ('AttributeKind'))])
        assert not list(self.mm['ownedElements'][ANY('name',EQ('foobar'))])

    def checkSuperclasses(self):
        enum = self.roots['ownedElements*'][ANY('name',EQ('enumeration'))]
        assert len(list(enum))==1
        sc = enum['superclasses']
        assert len(list(sc))==1, list(sc)
        assert list(sc['name'])==['AttributeKind']
        sc = list(enum['superclasses*']['name']); sc.sort()
        assert sc==['AttributeKind','PackageElement'], sc

TestClasses = (
    UMLTest, QueryTests, XMILoad, XMITests
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))
    return TestSuite(s)


"""Integration/acceptance tests for SEF.SimpleModel, etc."""

from unittest import TestCase, makeSuite, TestSuite
from TW.SEF.Queries import ANY, Equals
from TW.API import *

class UMLTest(TestCase):

    def setUp(self):
        global UMLClass
        from TW.UML.Model import UMLClass
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

from TW.SEF.Basic import FeatureMC

class featureBase(object):

    __metaclass__ = FeatureMC

    singular = 1

    newVerbs = Items(
        get     = 'get%(initCap)s',
        set     = 'set%(initCap)s',
        delattr = 'delattr%(initCap)s',
        doubled = '%(name)sDoubled',
    )

    def get_single(feature, self):
        return self.__dict__[feature.attrName][0]

    get_single.verb = 'get'
    get_single.installIf = lambda feature,method: feature.singular


    def get_multi(feature, self):
        return self.__dict__[feature.attrName]

    get_multi.verb = 'get'
    get_multi.installIf = lambda feature,method: not feature.singular


    def set(feature,self,val):
        self.__dict__[feature.attrName]=[val]

    def delattr(feature,self):
        del self.__dict__[feature.attrName]

    def doubled(feature,self):
        return feature.getMethod(self,'get')() * 2




class X(SEF.Element):

    class zebra(featureBase):
        singular = 0

    class Y(zebra):
        # test of subclassing from existing feature...
        singular = 1

    class Overwrite(featureBase):
        pass

    def OverwriteDoubled(self):
        return self.__class__.Overwrite.doubled(self) * 3


class SubclassOfX(X):

    class Overwrite(featureBase):
        # Even though we redefine the feature here,
        # the old OverwriteDoubled method in the class
        # should apply...
        singular = 0


















class checkExport(TestCase):

    def setUp(self):
        self.el = X()

    def checkMethods(self):
        self.el.setY(1)
        assert self.el.getY()==1
        assert self.el.__dict__['Y']==[1]
        assert self.el.YDoubled()==2
        self.el.delattrY()
        assert not self.el.__dict__.has_key('Y')

    def checkDescr(self):
        self.el.zebra = 2
        assert self.el.zebra==[2]
        assert self.el.__dict__['zebra']==[2]
        assert self.el.zebraDoubled()==[2,2]
        del self.el.zebra
        assert not self.el.__dict__.has_key('zebra')

    def checkOverwrite(self):

        self.el.Overwrite = 1
        assert self.el.OverwriteDoubled()==6

        e2 = SubclassOfX()
        e2.Overwrite = 1
        assert e2.OverwriteDoubled()==[1,1,1,1,1,1]












class anElement1(SEF.Element):

    class field1(SEF.Field):
        defaultValue = 1

    class simpleSeq(SEF.Sequence):
        pass

    class fwdRef(SEF.Reference):
        referencedEnd = 'backColl'

    class simpleRef(SEF.Reference):
        pass

    class fwdColl(SEF.Collection):
        referencedEnd = 'backRef'
        upperBound = 3


class anElement2(SEF.Element):

    class backColl(SEF.Collection):
        referencedEnd = 'fwdRef'

    class backRef(SEF.Reference):
        referencedEnd = 'fwdColl'















class exerciseFeatures(TestCase):

    def setUp(self):
        self.e = anElement1()


    def checkField(self):
        self.e.setField1(5)
        assert self.e.field1==5
        del self.e.field1
        assert self.e.field1==1


    def checkSimpleSeq(self):
        e = self.e

        map(e.addSimpleSeq, range(5))
        assert e.simpleSeq == [0,1,2,3,4]

        e.insertSimpleSeqBefore(1,-1)
        assert e.simpleSeq == [0,-1,1,2,3,4]

        e.removeSimpleSeq(-1)
        assert e.simpleSeq == [0,1,2,3,4]

        e.replaceSimpleSeq(0,-1)
        assert e.simpleSeq == [-1,1,2,3,4]


    def checkFwdRef(self):
        e1=self.e
        e2=anElement2()
        e1.fwdRef = e2
        assert e2.backColl[0] is e1
        assert len(e2.backColl)==1


    def checkSimpleRef(self):
        self.e.simpleRef = 99
        assert self.e.simpleRef == 99

    def checkFwdColl(self):
    
        e = self.e
        e1 = anElement2(); e.addFwdColl(e1)
        e2 = anElement2(); e.addFwdColl(e2)
        e3 = anElement2(); e.addFwdColl(e3)

        assert e.fwdColl == [e1,e2,e3]

        for x,y in zip(e.fwdColl, (e1,e2,e3)):
            assert x is y

        assert e1.backRef is e
        assert e2.backRef is e
        assert e3.backRef is e

        try:
            e.addFwdColl(anElement2())
        except ValueError:
            pass
        else:
            raise AssertionError,"Bounds check failed"


TestClasses = (
    checkExport, exerciseFeatures, UMLTest, QueryTests, XMILoad, XMITests
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))
    return TestSuite(s)


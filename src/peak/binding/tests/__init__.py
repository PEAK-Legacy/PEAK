"""Binding tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *


class baseWithClassAttr(binding.Base):

    myName = binding.classAttr( binding.Once( lambda s,d,a: s.__name__ ) )

class subclassWithClassAttr(baseWithClassAttr):
    pass


class anotherSubclass(baseWithClassAttr):
    pass


class ClassAttrTest(TestCase):

    def checkActivationOrder(self):
        # Note: order is to confirm that the using a once binding on a
        # base class doesn't prevent the subclass' copy of the binding
        # from activating.
        assert subclassWithClassAttr.myName == 'subclassWithClassAttr'
        assert baseWithClassAttr.myName == 'baseWithClassAttr'
        assert anotherSubclass.myName == 'anotherSubclass'

    def checkMetaTypes(self):
        assert anotherSubclass.__class__ is baseWithClassAttr.__class__
        assert anotherSubclass.__class__.__name__ == 'baseWithClassAttrClass'










testList = [1,2,'buckle your shoe']

class DescriptorData(binding.Component):

    thing1 = "this is my thing"
    thing2 = binding.bindTo('thing1')
    thing3 = binding.requireBinding('This is required')
    thing4 = binding.bindSequence('thing1','thing2')

    underflow = binding.bindToParent(50)
    
    class aService(binding.Component):

        thing5 = binding.bindToParent()

        class nestedService(binding.Component):

            thing6 = binding.bindToParent(2)

            deep = binding.bindTo('deep')

            namedThing = binding.New(binding.Component)

            acquired = binding.bindTo('thing1')

            getRoot = binding.bindTo('/')

            getUp = binding.bindTo('..')

        nestedService = binding.New(nestedService)
        
    aService = binding.New(aService)
    newDict  = binding.New(dict)

    listCopy = binding.Copy(testList)

    deep = binding.bindTo('aService/nestedService/thing6/thing1')

    testImport = binding.bindTo('import:unittest:TestCase')


class DescriptorTest(TestCase):

    def setUp(self):
        self.data = DescriptorData(None, 'data')


    def checkNaming(self):
        svc = self.data.aService
        gcn = binding.getComponentName
        assert gcn(svc)=='aService'
        assert gcn(svc.nestedService)=='nestedService'
        assert gcn(svc.nestedService.namedThing)=='namedThing'
        assert gcn(self.data)=='data'


    def checkBinding(self):
        thing2 = self.data.thing2 
        assert (thing2 is self.data.thing1), thing2
        assert self.data.__dict__['thing2'] is thing2


    def checkMulti(self):
        thing4 = self.data.thing4
        assert len(thing4)==2
        assert type(thing4) is tuple
        assert thing4[0] is self.data.thing1
        assert thing4[1] is self.data.thing2


    def checkConstructors(self):
        self.assertRaises(TypeError, DescriptorData, nonExistentKeyword=1)

        td = {}
        assert DescriptorData(newDict = td).newDict is td







    def checkParents(self):

        p1 = self.data.aService.thing5
        p2 = self.data.aService.nestedService.thing6
        p3 = self.data.underflow

        try:
            assert p1 is p2
            assert p1 is self.data
            assert p3 is p2
        finally:
            del self.data.aService.thing5
            del self.data.aService.nestedService.thing6
            del self.data.underflow


    def checkForError(self):
        try:
            self.data.thing3
        except NameError:
            pass
        else:
            raise AssertionError("Didn't get an error retrieving 'thing3'")


    def checkNew(self):
    
        data = self.data
        d = data.newDict
        assert type(d) is dict      # should be dict
        assert data.newDict is d    # only compute once
        
        data = DescriptorData()
        assert d == data.newDict        # should be equal
        assert d is not data.newDict    # but separate!






    def checkCopy(self):

        data = self.data
        l = data.listCopy

        assert type(l) is list      # should be a list
        assert l == testList        # should be equal
        assert l is not testList    # but separate!


    def checkDeep(self):

        data = self.data
        thing = data.thing1
        assert data.deep is thing
        
        nested = data.aService.nestedService

        assert nested.deep is thing
        assert nested.acquired is thing
        assert nested.getRoot is data
        assert nested.getUp is data.aService


    def checkImport(self):
        assert self.data.testImport is TestCase


    def checkPaths(self):
        svc = self.data.aService
        gcp = binding.getComponentPath

        assert str(gcp(svc,self.data))=='aService'
        assert str(gcp(svc.nestedService,self.data))=='aService/nestedService'
        assert str(
            gcp(svc.nestedService.namedThing,self.data)
        )=='aService/nestedService/namedThing'




    def checkAbsPaths(self):
        svc = self.data.aService
        gcp = binding.getComponentPath

        assert str(gcp(svc))=='/aService'
        assert str(gcp(svc.nestedService))=='/aService/nestedService'
        assert str(
            gcp(svc.nestedService.namedThing)
        )=='/aService/nestedService/namedThing'


TestClasses = (
    ClassAttrTest, DescriptorTest,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































"""Module inheritance and metaclass tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from Interface import Interface




































testList = [1,2,'buckle your shoe']
class IS1U(Interface): pass
class IS2U(Interface): pass

class DescriptorData(binding.Component):

    thing1 = "this is my thing"

    thing2 = binding.bindTo('thing1')

    thing3 = binding.requireBinding('This is required')

    thing4 = binding.bindSequence('thing1','thing2')

    underflow = binding.bindToParent(50)

    class aService(binding.AutoCreated):

        thing5 = binding.bindToParent(provides=IS1U)

        class nestedService(binding.AutoCreated):
            _provides = IS2U

            thing6 = binding.bindToParent(2)

            deep = binding.bindTo('deep')

            acquired = binding.bindTo('thing1')

            getRoot = binding.bindTo('/')

            getUp = binding.bindTo('..')

    newDict = binding.New(dict)

    listCopy = binding.Copy(testList)

    deep = binding.bindTo('aService/nestedService/thing6/thing1')

    testImport = binding.bindTo('import:unittest:TestCase')

class ISampleUtility1(Interface): pass
class ISampleUtility2(Interface): pass

def makeAUtility(context):
    u=binding.Component(); u.setParentComponent(context)
    return u


class DescriptorTest(TestCase):

    def setUp(self):

        self.data = DescriptorData()

        self.data.aService.registerProvider(
            ISampleUtility1,
            binding.Provider(makeAUtility)
        )

        self.data.aService.registerProvider(
            ISampleUtility2,
            binding.CachingProvider(makeAUtility)
        )


    def checkUtilityAttrs(self):

        data = self.data
        ns   = data.aService.nestedService

        assert binding.findUtility(ns,IS1U) is data
        assert binding.findUtility(ns,IS2U) is ns









    def checkAcquireInst(self):

        data = self.data
        ob1 = binding.findUtility(data,ISampleUtility1,None)
        ob2 = binding.findUtility(data.aService,ISampleUtility1,None)
        ob3 = binding.findUtility(data.aService.nestedService,ISampleUtility1,
        None)
        assert ob1 is None
        assert ob2 is not None
        assert ob3 is not None
        assert ob3 is not ob2
        assert ob2.getParentComponent() is data.aService
        assert ob3.getParentComponent() is data.aService.nestedService

    def checkAcquireSingleton(self):

        data = self.data
        ob1 = binding.findUtility(data,ISampleUtility2,None)
        ob2 = binding.findUtility(data.aService,ISampleUtility2,None)
        ob3 = binding.findUtility(data.aService.nestedService,ISampleUtility2,
        None)
        ob4 = binding.findUtility(data.aService.nestedService,ISampleUtility2,
        None)

        assert ob1 is None
        assert ob2 is not None
        assert ob3 is not None
        assert ob4 is not None
        assert ob3 is ob2
        assert ob4 is ob2
        assert ob2.getParentComponent() is data.aService
        assert ob3.getParentComponent() is data.aService
        assert ob4.getParentComponent() is data.aService

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



TestClasses = (
    DescriptorTest,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































"""Configuration system tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from protocols import Interface
from peak.config.interfaces import *
from peak.tests import testRoot


class TestRule(object):

    protocols.advise(
        instancesProvide = [ISmartProperty]
    )

    def computeProperty(self, propertyMap, name, prefix, suffix, targetObject):
        return propertyMap, name, prefix, suffix, targetObject
























class PropertyTest(TestCase):

    def checkSetProp(self):
        app = testRoot()
        config.setPropertyFor(app,'peak.config.tests.foo',1)
        assert config.getProperty(app,'peak.config.tests.foo')==1


    def checkEnviron(self):
        from os import environ

        # retry multiple times to verify re-get is safe...
        app = testRoot()
        ps = config.PropertySet(app,'environ.*')

        for r in range(3):
            for k,v in environ.items():
                assert ps[k] is v

    def checkSmartProps(self):

        app = testRoot()
        obj = binding.Component(app)

        config.loadConfigFile(obj,
            config.fileNearModule(__name__,'test_links.ini')
        )

        for k in '.spew,.blue,.knew'.split(','):
            prop = 'foo.bar.rule%s' % k
            suff = k.startswith('.') and k[1:] or k
            assert config.getProperty(obj, prop) == (
                obj.__instance_offers__, prop, 'foo.bar.rule.', suff, obj
            ), config.getProperty(obj, prop)

        assert config.getProperty(obj,'foo.bar.spam') is testRoot
        assert config.getProperty(obj,'foo.bar.baz') is testRoot




class IS1U(Interface):
    pass

class IS2U(Interface):
    pass


class UtilityData(binding.Component):

    class aService(binding.Component):

        thing5 = binding.bindToParent(offerAs=[IS1U])

        class nestedService(binding.Component):
            pass

        nestedService = binding.New(nestedService, offerAs=[IS2U])

    aService = binding.New(aService)

    deep = binding.bindTo('aService/nestedService/thing6/thing1')


class ISampleUtility1(Interface):
    pass


class ISampleUtility2(Interface):
    pass


def makeAUtility(context):
    u=binding.Component(); u.setParentComponent(context)
    return u







class UtilityTest(TestCase):

    def setUp(self):

        self.data = UtilityData(testRoot(), 'data')

        self.data.aService.registerProvider(
            ISampleUtility1,
            config.instancePerComponent(makeAUtility)
        )

        self.data.aService.registerProvider(
            ISampleUtility2,
            config.provideInstance(makeAUtility)
        )


    def checkUtilityAttrs(self):

        data = self.data
        ns   = data.aService.nestedService
        assert config.findUtility(ns,IS1U) is data
        assert config.findUtility(ns,IS2U) is ns


    def checkAcquireInst(self):

        data = self.data
        ob1 = config.findUtility(data,ISampleUtility1,None)
        ob2 = config.findUtility(data.aService,ISampleUtility1,None)
        ob3 = config.findUtility(data.aService.nestedService,ISampleUtility1,
        None)
        assert ob1 is None
        assert ob2 is not None
        assert ob3 is not None
        assert ob3 is not ob2
        assert ob2.getParentComponent() is data.aService
        assert ob3.getParentComponent() is data.aService.nestedService



    def checkAcquireSingleton(self):

        data = self.data
        root = data.getParentComponent()
        ob1 = config.findUtility(data,ISampleUtility2,None)
        ob2 = config.findUtility(data.aService,ISampleUtility2,None)
        ob3 = config.findUtility(data.aService.nestedService,ISampleUtility2,
        None)
        ob4 = config.findUtility(data.aService.nestedService,ISampleUtility2,
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





















class ModuleTest(TestCase):

    def setUp(self):
        import testM1, testM2
        self.M1, self.M2 = testM1, testM2

    def checkBase(self):
        assert self.M1.BaseClass.foo==1
        assert self.M2.BaseClass.foo==2

    def checkSub(self):
        assert self.M1.Subclass.foo==1
        assert self.M2.Subclass.foo==2

    def checkNested(self):
        assert self.M1.Subclass.Nested.bar=='baz'
        assert self.M2.Subclass.Nested.bar=='baz'
        assert self.M1.Subclass.NestedSub.bar == 'baz'
        assert self.M2.Subclass.NestedSub.bar == 'baz'
        assert not hasattr(self.M1.Subclass.NestedSub,'spam')
        assert self.M2.Subclass.NestedSub.spam == 'Nested'

    def checkFuncGlobals(self):
        assert self.M1.aFunc1()=='M1'
        assert self.M2.aFunc1()=='M2'

    def checkWrapping(self):
        assert self.M1.aFunc2('x')=='M1(x)'
        assert self.M2.aFunc2('x')=='after(M1(before(x)))'

    def checkRefBetweenClasses(self):
        assert self.M2.Referencer.containedClass.M1=='M1'

    def checkBaseBinding(self):
        import UserList
        assert self.M2.RebindSub.M1=='M1'
        assert self.M2.RebindSub.M2=='M2'
        assert self.M2.RebindSub.__bases__ == (
            self.M2.UnusedBase, UserList.UserList, object
        ), self.M2.RebindSub.__bases__

    def checkImplements(self):
        m1Foo = self.M1.FooThing()
        m2Foo = self.M2.FooThing()
        assert adapt(m1Foo,IConfigKey) is m1Foo
        assert adapt(m2Foo,IRule) is m2Foo
        assert adapt(m1Foo,IRule, None) is None
        assert adapt(m2Foo,IConfigKey) is m2Foo


class AdviceTest(ModuleTest):

    def setUp(self):
        import testM2a, testM1a, testM1
        self.M1 = testM1
        self.M2 = testM1a


TestClasses = (
    PropertyTest, ModuleTest, AdviceTest, UtilityTest,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)














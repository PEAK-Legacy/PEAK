"""Test configuration keys"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from protocols import Interface
from peak.config.interfaces import *
from peak.tests import testRoot


class I1(Interface):
    pass

class I2(I1):
    pass

class I3(I1,I2):
    pass


class A: pass
class B(A): pass
class C(A,B): pass


class _A(object): pass
class _B(_A): pass
class _C(_A,_B): pass














class BasicKeyTests(TestCase):

    def verifiedKey(self,key):
        # Key must be adaptable to IConfigKey, and hash/compare
        # equal to its unadapted form
        ak = adapt(key,IConfigKey,None)
        self.assertEqual( key, ak )
        self.assertEqual( hash(key), hash(ak) )
        return ak


    def verifyKeygen(self,key):

        # Verify the parent, lookup, and registration keys for 'key'

        for k,d in key.registrationKeys():
            self.verifiedKey(k)

        map(self.verifiedKey, key.lookupKeys())
        map(self.verifiedKey, key.parentKeys())


    def verifySelfReg(self, keys):
        # Verify that 'keys' only use themselves for registration
        for k in keys:
            self.assertEqual( list(k.registrationKeys()), [(k,0)] )


    def verifySelfLookup(self, keys):
        # Verify that 'keys' only use themselves for lookup
        for k in keys:
            self.assertEqual( list(k.lookupKeys()), [k] )









    def testPropertyNameAsKey(self):

        k1 = PropertyName('foo.bar')
        k2 = PropertyName('foo.*')
        k3 = PropertyName('*')
        k4 = PropertyName('foo.bar?')

        # Property names register only as themselves
        all = [k1,k2,k3,k4]

        map(self.verifiedKey, all)
        self.verifySelfReg(all)

        self.assertEqual( list(k1.lookupKeys()), [k1,k2,k3,k1,k4] )
        self.assertEqual( list(k2.lookupKeys()), [k2] )
        self.assertEqual( list(k3.lookupKeys()), [k3] )
        self.assertEqual( list(k4.lookupKeys()), [k4] )

        map(self.verifyKeygen, [k1,k2,k3])


    def testInterfaceAsKey(self):

        all = map(self.verifiedKey, [I1,I2,I3])
        k1,k2,k3 = all

        # Interfaces are registered under everything in their MRO, by
        # "implication distance"

        self.assertEqual( list(k1.registrationKeys()), [(I1,0)] )
        self.assertEqual( list(k2.registrationKeys()), [(I2,0),(I1,1)] )
        self.assertEqual( list(k3.registrationKeys()), [(I3,0),(I1,1),(I2,1)] )

        # Interfaces are looked up using only the interface itself
        self.verifySelfLookup( all )

        map(self.verifyKeygen, all)




    def testClassicClassAsKey(self):

        all = map(self.verifiedKey, [A,B,C])
        k1,k2,k3 = all

        # Classes are registered under themselves only
        self.verifySelfReg(all)

        # Classes are looked up by MRO
        self.assertEqual( list(k1.lookupKeys()), [A] )
        self.assertEqual( list(k2.lookupKeys()), [B,A] )
        self.assertEqual( list(k3.lookupKeys()), [C,A,B,A] )

        map(self.verifyKeygen, all)


    def testTypeAsKey(self):

        all = map(self.verifiedKey, [_A,_B,_C])
        k1,k2,k3 = all

        # Classes are registered under themselves only
        self.verifySelfReg(all)

        # Classes are looked up by MRO
        self.assertEqual( list(k1.lookupKeys()), [_A,object] )
        self.assertEqual( list(k2.lookupKeys()), [_B,_A,object] )
        self.assertEqual( list(k3.lookupKeys()), [_C,_B,_A,object] )

        map(self.verifyKeygen, all)











    def testProducts(self):

        p1 = config.MultiKey(I1,A)
        p2 = config.MultiKey(_C,I2)
        p3 = config.MultiKey(I3,_C,B)

        all = map(self.verifiedKey, [p1,p2,p3])
        k1,k2,k3 = all

        self.assertEqual(
            list(k1.registrationKeys()), [((I1,A),0)]
        )
        self.assertEqual(
            list(k2.registrationKeys()), [((_C,I2),0),((_C,I1),1)]
        )
        self.assertEqual(
            list(k3.registrationKeys()),
            [((I3,_C,B),0), ((I1,_C,B),1), ((I2,_C,B),1)]
        )

        self.assertEqual(
            list(k1.lookupKeys()), [(I1,A)]
        )
        self.assertEqual(
            list(k2.lookupKeys()), [(_C,I2),(_B,I2),(_A,I2),(object,I2)]
        )

        self.assertEqual(
            list(k3.lookupKeys()),
            [
                (I3,_C,B), (I3,_C,A), (I3,_B,B), (I3,_B,A),
                (I3,_A,B), (I3,_A,A), (I3,object,B), (I3,object,A),
            ]
        )

        map(self.verifyKeygen, all)





    def testUnions(self):

        p0 = config.UnionOf()   # empty set
        p1 = config.UnionOf(I1,A)
        p2 = config.UnionOf(_C,I2)
        p3 = config.UnionOf(I3,_C,B)

        all = map(self.verifiedKey, [p0,p1,p2,p3])
        k0, k1,k2,k3 = all

        self.assertEqual(
            list(k0.registrationKeys()), []
        )

        self.assertEqual(
            list(k1.registrationKeys()), [(I1,0),(A,0)]
        )

        self.assertEqual(
            list(k2.registrationKeys()), [(_C,0), (I2,0), (I1,1)]
        )

        self.assertEqual(
            list(k3.registrationKeys()), [(I3,0),(I1,1),(I2,1), (_C,0), (B,0)]
        )

        self.assertEqual( list(k0.lookupKeys()), [] )
        self.assertEqual( list(k1.lookupKeys()), [I1,A] )
        self.assertEqual( list(k2.lookupKeys()), [_C,_B,_A,object,I2] )
        self.assertEqual( list(k3.lookupKeys()), [I3,_C,_B,_A,object,B,A] )

        map(self.verifyKeygen, all)

        # Union of one key should just return the key
        self.assertEqual(config.UnionOf(I1), I1)






class SimpleMapTest(TestCase):

    regKeys = [
        'foo.bar.baz', 'spam.bar.foo', 'foo.bar.qux', 'foo.baz',
        'foo.bar.widget.gizmo', 'foo.bar.baz.spam',
    ]
    regKeys.sort()
    foundKeys = regKeys
    mapType = config.ConfigMap

    def setUp(self):
        self.map = self.mapType()

    def keysFor(self,key):
        keys = list(self.map._configKeysMatching(key)); keys.sort()
        return keys

    def register(self,key):
        self.map.registerProvider(key,config.Value(None))

    def testKeysMatching(self):
        map(self.register, self.regKeys)

        self.assertEqual(
            self.keysFor('foo.bar'),
            [k for k in self.foundKeys
                if k.startswith('foo.bar.') and '.' not in k[8:]
            ]
        )
        self.assertEqual(
            self.keysFor('foo.*'),
            [k for k in self.foundKeys if k.startswith('foo.')]
        )
        self.assertEqual(
            self.keysFor('foo.bar.*'),
            [k for k in self.foundKeys if k.startswith('foo.bar.')]
        )
        self.assertEqual(
            self.keysFor('*'), self.foundKeys
        )

class KeysViaAPI:

    def keysFor(self,key):
        keys = list(config.iterKeys(self.map,key))
        keys.sort()
        return keys


class SimpleMapViaAPI(KeysViaAPI, SimpleMapTest):
    pass


class ComponentMapDirect(SimpleMapTest):

    def setUp(self):
        self.map = binding.Component()


class ComponentMapViaAPI(KeysViaAPI, ComponentMapDirect):
    # Verify iterKeys() on component
    pass


class Case1(binding.Component):

    spam_qux = binding.Require(
        "testing", offerAs=['spam.baz.qux','foo.bar.click']
    )

class ComponentWithBinding(SimpleMapTest):

    foundKeys = SimpleMapTest.foundKeys + ['spam.baz.qux', 'foo.bar.click']
    foundKeys.sort()

    mapType = Case1

class ComponentWithBindingViaAPI(KeysViaAPI, ComponentWithBinding):
    pass



class ParentComponent(ComponentWithBindingViaAPI):

    def setUp(self):
        self.map = self.mapType(binding.Component())

class ChildComponent(ComponentWithBindingViaAPI):

    def setUp(self):
        self.map = binding.Component(self.mapType())


class Case2(Case1):

    other_thing = binding.Require(
        "testing", offerAs=['foo.bar.quack.*']
    )


class InheritedComponent(ComponentWithBinding):

    foundKeys = ComponentWithBinding.foundKeys + ['foo.bar.quack.*']
    foundKeys.sort()
    mapType = Case2


class InheritedComponentAPI(KeysViaAPI, InheritedComponent):
    pass


class InheritedParent(InheritedComponentAPI):
    setUp = ParentComponent.setUp.im_func


class InheritedChild(InheritedComponentAPI):
    setUp = ChildComponent.setUp.im_func






TestClasses = (
    BasicKeyTests, SimpleMapTest, SimpleMapViaAPI, ComponentMapDirect,
    ComponentMapViaAPI, ComponentWithBinding, ComponentWithBindingViaAPI,
    ParentComponent, ChildComponent, InheritedComponent, InheritedComponentAPI,
    InheritedParent, InheritedChild,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)




























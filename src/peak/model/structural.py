"""Basic implementation of a domain metamodel (minus enumerations)

   TODO:

    * Default constructors for 'Immutable' and 'Element'
"""

from peak.api import *
from interfaces import *
from method_exporter import MethodExporter


__all__ = [
    'Immutable', 'Namespace', 'Package', 'Model',
    'StructuralFeature', 'Field', 'Collection', 'Reference', 'Sequence',
    'Classifier','PrimitiveType','DataType',
    'DerivedAssociation', 'HashAndCompare', 'structField',
]


class HashAndCompare(object):

    """Mixin that allows 'hash' and 'cmp' operations on a delegate value"""

    def __hash__(self):
        return hash(self._hashAndCompare)

    def __cmp__(self,other):
        return cmp(self._hashAndCompare,other)












class Namespace(binding.Base):

    def _XMIMap(self,d,a):

        xm = {}

        for m in binding.getInheritedRegistries(self,'_XMIMap'):
            xm.update(m)

        for k,v in self.__class_descriptors__.iteritems():
        
            for n in getattr(v,'_XMINames',()):

                xm[n] = k

                while '.' in n:
                    n = n.split('.',1)[1]
                    xm[n]=k

        return xm

    _XMIMap = binding.classAttr(binding.Once(_XMIMap))


class Package(Namespace):

    """Package of Element Classes"""


class Model(Package):

    """Model or Metamodel containing Packages or Element classes"""









class FeatureClass(HashAndCompare,MethodExporter):

    """Method-exporting Property
    
        This metaclass adds property support to Meta.MethodExporter by adding
        '__get__', '__set__', and '__delete__' methods, which are delegated
        to the method templates for the 'get', 'set' and 'delattr' verbs.

        In other words, if you define a feature 'foo', following standard
        naming patterns for its 'set', 'get' and 'delattr' verbs, and 'bar' is
        an Element whose class includes the 'foo' feature, then 'bar.foo = 1'
        is equivalent to 'bar.setFoo(1)'.  Similarly, referencing 'bar.foo' by
        itself is equivalent to 'bar.getFoo()', and 'del bar.foo' is equivalent
        to 'bar.delattrFoo()'.

        (Note: this is true even if the Element class supplies its own 'setFoo'
        or 'getFoo' implementations, since the 'getMethod()' API is used.)

        Please see the 'TW.API.Meta.MethodExporter' class documentation for
        more detail on how method templates are defined, the use of naming
        conventions, verbs, template variants, etc."""

    __metaclass__ = binding.Activator   # metaclasses can't be components


    def __get__(self, ob, typ=None):

        """Get the feature's value by delegating to 'ob.getX()'"""

        if ob is None: return self
        return self.getMethod(ob,'get')()


    def __set__(self, ob, val):

        """Set the feature's value by delegating to 'ob.setX()'"""

        return self.getMethod(ob,'set')(val)



    def __delete__(self, ob):

        """Delete the feature's value by delegating to 'ob.delattrX()'"""

        return self.getMethod(ob,'unset')()


    def typeObject(self,d,a):
        rt = self.referencedType
        if isinstance(rt,str):
            return binding.lookupComponent(rt,self)
        return rt

    typeObject = binding.Once(typeObject)


    fromString = binding.bindTo('typeObject/fromString')
    fromFields = binding.bindTo('typeObject/fromFields')

    sortPosn   = None

    def _hashAndCompare(self,d,a):
        return self.sortPosn, self.__name__, id(self)
        
    _hashAndCompare = binding.Once(_hashAndCompare)
















    isMany     = binding.Once(lambda s,d,a: s.upperBound<>1)
    isRequired = binding.Once(lambda s,d,a: s.lowerBound >0)

    isChangeable = binding.Once(
        lambda s,d,a: not s.isDerived,
        doc = "Feature is changeable; defaults to 'True' if not 'isDerived'"
    )

    implAttr   = binding.Once(
        lambda s,d,a: s.attrName,
        doc = "The underlying (private) attribute implementing this feature"
    )





























class StructuralFeature(object):

    __metaclass__ = FeatureClass
    __class_implements__ = IFeature, IFeatureSPI

    isDerived     = False
    isComposite   = False
    isOrdered     = False
    isReference   = False

    lowerBound    = 0
    upperBound    = None    # None means unbounded upper end

    referencedEnd  = None    # and without an 'other end'
    referencedType = None
    defaultValue   = NOT_GIVEN

    newVerbs = Items(
        get     = 'get%(initCap)s',
        set     = 'set%(initCap)s',
        unset   = 'unset%(initCap)s',
    )

    def get(feature, element):
        value = element._getBinding(feature.implAttr, feature.defaultValue)
        if value is NOT_GIVEN:
            raise AttributeError,feature.attrName
        return value

    def _assertChangeable(feature):
        if not feature.isChangeable:
            raise AttributeError("Unchangeable feature", feature.attrName)

    def set(feature, element, val):
        feature._assertChangeable()
        element._setBinding(feature.implAttr,val)

    def unset(feature, element):
        feature._assertChangeable()
        element._delBinding(feature.implAttr)

class Field(StructuralFeature):

    upperBound = 1

    def _getList(feature, element):
        return [feature.get(element)]



class structField(Field):

    """An unchangeable field; used for immutables"""

    isChangeable = binding.classAttr( binding.Constant(None, False) )



























class Collection(StructuralFeature):

    __class_implements__ = IReference, IReferenceSPI

    isReference = True

    newVerbs = Items(
        add     = 'add%(initCap)s',
        remove  = 'remove%(initCap)s',
        replace = 'replace%(initCap)s',
        insertBefore = 'insert%(initCap)sBefore',
    )

    def _getList(feature, element):
        return element._getBinding(feature.implAttr, [])
        
    def get(feature, element):
        return feature._getList(element)

    def set(feature, element, val):
        feature.__delete__(element)
        map(feature.getMethod(element,'add'),val)


    def add(feature, element, item):
        """Add the item to the collection/relationship"""      

        ub = feature.upperBound

        if not ub or len(feature._getList(element))<ub:
            feature._notifyLink(element,item)
        else:
            raise ValueError("Too many items")


    def remove(feature, element, item):
        """Remove the item from the collection/relationship, if present"""
        feature._notifyUnlink(element,item)



    def replace(feature, element, oldItem, newItem):

        d = feature._getList(element)
        p = d.index(oldItem)

        if p!=-1:
            feature._notifyUnlink(element,oldItem,p)
            feature._notifyLink(element,newItem,p)
        else:
            raise ValueError(oldItem,"not found")


    def unset(feature, element):

        """Unset the value of the feature (like __delattr__)"""

        d = feature._getList(element)

        items = zip(range(len(d)),d)
        items.reverse()

        unlink = feature._notifyUnlink

        # remove items in reverse order, to simplify deletion and
        # to preserve any invariant that was relevant for addition
        # order...
        
        for posn,item in items:
            unlink(element,item,posn)
            
        element._delBinding(feature.implAttr)










    def _notifyLink(feature, element, item, posn=None):

        feature._link(element,item,posn)
        referencedEnd = feature.referencedEnd

        if referencedEnd:
            otherEnd = getattr(item.__class__,referencedEnd)
            otherEnd._link(item,element)

    def _notifyUnlink(feature, element, item, posn=None):

        feature._unlink(element,item,posn)
        referencedEnd = feature.referencedEnd

        if referencedEnd:
            otherEnd = getattr(item.__class__,referencedEnd)
            otherEnd._unlink(item,element)


    def _link(feature,element,item,posn=None):

        feature._assertChangeable()
        d=feature._getList(element)
        element._setBinding(feature.implAttr, d)

        if posn is None:
            d.append(item)
        else:
            d.insert(posn,item)

    def _unlink(feature,element,item,posn=None):

        feature._assertChangeable()
        d=feature._getList(element)
        element._setBinding(feature.implAttr, d)

        if posn is None:
            d.remove(item)
        else:
            del d[posn]

    def insertBefore(feature, element, oldItem, newItem):

        if not feature.isOrdered:
            raise TypeError("Unordered feature", feature)

        d = feature._getList(element)
        
        ub = feature.upperBound
        if ub and len(d)>=ub:
            raise ValueError("Too many items")

        i = -1

        if d:
            i = d.index(oldItem)

        if i!=-1:
            feature._notifyLink(element,newItem,i)
        else:
            raise ValueError(oldItem,"not found")





















class Reference(Collection):

    upperBound = 1

    def get(feature, element):

        vals = feature._getList(element)

        if vals:
            return vals[0]

        val = feature.defaultValue

        if val is NOT_GIVEN:
            raise AttributeError,feature.attrName

        return val

    def set(feature, element, val):
        feature.__delete__(element)
        feature.getMethod(element,'add')(val)



class DerivedAssociation(Collection):

    isDerived = True

    def _getList(feature, element):
        """This must be defined in subclass"""
        raise NotImplementedError
        
    def get(feature, element):
        return feature._getList(element)
        

class Sequence(Collection):

    isOrdered = True


class ClassifierClass(Namespace.__class__):

    """Basis for all flavors"""

    def mdl_featuresDefined(self,d,a):

        """Sorted tuple of feature objects defined/overridden by this class"""

        isFeature = IFeature.isImplementedBy
        mine = [v for (k,v) in d.items() if isFeature(v)]
        mine.sort()
        return tuple(mine)

    mdl_featuresDefined = binding.Once(mdl_featuresDefined)


    def mdl_featureNames(self,d,a):
        """Names of all features, in monotonic order (see 'mdl_features')"""
        return tuple([f.attrName for f in self.mdl_features])

    mdl_featureNames = binding.Once(mdl_featureNames)


    mdl_isAbstract = binding.Constant(
        None, False, doc = 
        """Is this an abstract class?  Defaults to 'False'.

            To make a 'model.Classifier' subclass abstract, set this
            to 'True' in the class definition.  Note that you don't
            ever need to set this to 'False', since it will default
            to that value in every new subclass, even the subclasses of
            abstract classes.
        """
    )







    def mdl_features(self,d,a):
        """All feature objects of this classifier, in monotonic order

        The monotonic order of features is equivalent to the concatenation of
        'mdl_featuresDefined' for all classes in the classifier's MRO, in
        reverse MRO order, with duplicates (i.e. overridden features)
        eliminated.  That is, if a feature named 'x' exists in more than one
        class in the MRO, the most specific definition of 'x' will be used
        (i.e. the first definition in MRO order), but it will be placed in the
        *position* reserved by the *less specific* definition.  The idea is
        that, once a position has been defined for a feature name, it will
        continue to be used by all subclasses, if possible.  For example::

            class A(model.Classifier):
                class foo(model.Field): pass
                
            class B(A):
                class foo(model.Field): pass
                class bar(model.Field): pass

        would result in 'B' having a 'mdl_features' order of '(foo,bar)',
        even though its 'mdl_featuresDefined' would be '(bar,foo)' (because
        features without a sort priority define are ordered by name).

        The purpose of using a monotonic ordering like this is that it allows
        subtypes to use a serialized format that is a linear extension of
        their supertype, at least in the case of single inheritance.  It may
        also be useful for GUI layouts, where it's also desirable to have a
        subtype's display look "the same" as a base type's display, except for
        those features that it adds to the supertype."""
        
        out  = []
        posn = {}
        add  = out.append
        get  = posn.get

        all  = list(
            binding.getInheritedRegistries(self,'mdl_features')
        )
        all.append(self.mdl_featuresDefined)
      
        for nf in all:
            for f in nf:
                n = f.attrName
                p = get(n)
                if p is None:
                    posn[n] = len(out)
                    add(f)
                else:
                    out[p] = f
                    
        return tuple(out)

    mdl_features = binding.Once(mdl_features)


    def mdl_sortedFeatures(self,d,a):

        """All feature objects of this classifier, in sorted order"""

        fl = list(self.mdl_features)
        fl.sort
        return tuple(fl)

    mdl_sortedFeatures = binding.Once(mdl_sortedFeatures)


    mdl_compositeFeatures = binding.Once(
        lambda s,d,a: tuple([f for f in s.mdl_features if f.isComposite]),
        doc="""Ordered subset of 'mdl_features' that are composite"""
    )











class Classifier(Namespace):

    __metaclass__ = ClassifierClass

    __class_implements__ = IClassifier

    mdl_isAbstract = True   # Classifier itself is abstract

    def __new__(klass,*__args,**__kw):

        """Don't allow instantiation if this is an abstract class"""

        if klass.mdl_isAbstract:
            raise TypeError, "Can't instantiate an abstract class!"
        return super(Classifier,klass).__new__(klass,*__args,**__kw)


    def fromFields(klass,fieldSeq):
        """Return a new instance from a sequence of fields"""
        return klass(**dict(zip(klass.mdl_featureNames,fieldSeq)))

    fromFields = classmethod(fromFields)


    def fromString(klass, value):
        raise NotImplementedError

    fromString = classmethod(fromString)













class ImmutableClass(ClassifierClass):

    def __init__(klass,name,bases,dict):
        for f in klass.mdl_features:
            if f.isChangeable:
                raise TypeError(
                    "Immutable class with changeable feature",
                    klass, f
                )
        super(ImmutableClass,klass).__init__(name,bases,dict)


class Immutable(Classifier, HashAndCompare):

    __metaclass__  = ImmutableClass
    __implements__ = binding.IBindingAPI
    mdl_isAbstract     = True   # Immutable itself is abstract

    def _hashAndCompare(s,d,a):
        return tuple([
            getattr(s,n,None) for n in s.__class__.mdl_featureNames
        ])

    _hashAndCompare = binding.Once(_hashAndCompare)

    def setParentComponent(self, parentComponent, componentName=None):
        if parentComponent is not None or componentName is not None:
            raise TypeError("Data values are not components")
    
    def getParentComponent(self):
        return None

    def getComponentName(self):
        return None

    def _setBinding(self,attr,value):
        raise TypeError("Immutable object", self)

    def __setattr__(self,attr,value):
        raise TypeError("Immutable object", self)

class PrimitiveTypeClass(ClassifierClass):

    def __init__(klass,name,bases,cDict):

        super(PrimitiveTypeClass,klass).__init__(name,bases,cDict)

        if klass.mdl_features:
            raise TypeError(
                "Primitive types can't have features", klass
            )

    # Primitive types are not instantiable; they stand in for
    # a type that isn't a model.Classifier

    mdl_isAbstract = binding.Constant(None, True)


class PrimitiveType(Classifier):

    """A primitive type (e.g. Boolean, String, etc.)"""

    __metaclass__ = PrimitiveTypeClass


class DataType(Immutable):

    """An immutable data structure type"""


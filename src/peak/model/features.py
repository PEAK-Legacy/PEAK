"""Basic implementation of a domain metamodel (minus enumerations)

    This module implements base classes for "Features" in the sense of
    the "Service-Element-Feature" pattern.  By subclassing from them,
    you get a wide variety of services automatically provided, ranging
    from automatic generation of getter/setter/mutator methods,
    metadata such as ordered lists of features provided by a class,
    well-defined hookpoints for "event" trapping, persistence support,
    and more.
"""

from peak.api import *
from interfaces import *
from method_exporter import MethodExporter
from peak.util.hashcmp import HashAndCompare


__all__ = [
    'StructuralFeature',  'Collection', 'Sequence',
    'DerivedFeature', 'structField', 'Attribute',

    'DerivedAssociation', 'Field', 'Reference', # deprecated names
]


installIfChangeable = lambda f,m: f.isChangeable















class FeatureClass(HashAndCompare,MethodExporter):

    """Method-exporting Property (metaclass for StructuralFeature)
    
        This metaclass adds property support to 'MethodExporter' by adding
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

        Please see the 'peak.model.method_exporter.MethodExporter' class
        documentation for more detail on how method templates are defined,
        the use of naming conventions, verbs, template variants, etc."""

    __metaclass__ = binding.Activator   # metaclasses can't be components


    def __get__(self, ob, typ=None):

        """Get the feature's value by delegating to 'ob.getX()'"""

        if ob is None: return self
        return self.getMethod(ob,'get')()


    def __set__(self, ob, val):
        """Set the feature's value by delegating to 'ob.setX()'"""

        if self.isChangeable:
            self.getMethod(ob,'set')(val)
        else:
            raise AttributeError("Unchangeable feature",self.attrName)

    def __delete__(self, ob):
        """Delete the feature's value by delegating to 'ob.delattrX()'"""

        if self.isChangeable:
            self.getMethod(ob,'unset')()
        else:
            raise AttributeError("Unchangeable feature",self.attrName)


    def typeObject(self,d,a):
        """The actual type referred to by 'referencedType'

            Since a feature's 'referencedType' can be either a string or
            a type, the actual type object is cached in the 'typeObject'
            attribute.  If you need to get the type of feature 'aFeature',
            just refer to 'aFeature.typeObject'.  This will of course fail
            if the 'referencedType' attribute is invalid.
        """
        rt = self.referencedType
        if isinstance(rt,str):
            return binding.lookupComponent(rt,self)
        return rt

    typeObject = binding.Once(typeObject)
    fromString = binding.bindTo('typeObject/mdl_fromString')
    fromFields = binding.bindTo('typeObject/mdl_fromFields')
    normalize  = binding.bindTo('typeObject/mdl_normalize')

    sortPosn   = None

    def _hashAndCompare(self,d,a):

        """Features hash and compare based on position, name, and identity

        Specifically, a feature is hashed and compared as though it were
        a tuple of its 'sortPosn', '__name__', and 'id()'."""

        return self.sortPosn, self.__name__, id(self)
        
    _hashAndCompare = binding.Once(_hashAndCompare)

    isMany     = binding.Once(lambda s,d,a: s.upperBound<>1)
    isRequired = binding.Once(lambda s,d,a: s.lowerBound >0)

    isChangeable = binding.Once(
        lambda s,d,a: not s.isDerived,
        doc = "Feature is changeable; defaults to 'True' if not 'isDerived'"
    )


    implAttr   = binding.Once(
        lambda s,d,a: (s.useSlot and '_f_'+s.attrName or s.attrName),
        doc = "The underlying (private) attribute implementing this feature"
    )

    def isReference(self,d,a):
        """Does the feature refer to a non-primitive/non-struct type?"""
        from datatypes import TCKind
        return self.typeObject.mdl_typeCode.unaliased().kind==TCKind.tk_objref

    isReference = binding.Once(isReference)


    def _defaultValue(self,d,a):
        try:
            return self.defaultValue
        except AttributeError:
            return self.typeObject.mdl_defaultValue

    _defaultValue = binding.Once(_defaultValue)












class StructuralFeature(object):

    __metaclass__ = FeatureClass

    __class_implements__ = IFeature, IFeatureSPI

    isDerived     = False
    isComposite   = False
    isOrdered     = False

    useSlot       = False

    lowerBound    = 0
    upperBound    = None    # None means unbounded upper end

    referencedEnd  = None
    referencedType = None

    newVerbs = Items(
        get     = 'get%(initCap)s',
        set     = 'set%(initCap)s',
        unset   = 'unset%(initCap)s',
        add     = 'add%(initCap)s',
        remove  = 'remove%(initCap)s',
        replace = 'replace%(initCap)s',
        insertBefore = 'insert%(initCap)sBefore',
    )


    def _get_many(feature, element):
        return feature._getList(element)

    _get_many.installIf = lambda f,m: f.isMany
    _get_many.verb      = 'get'







    def _get_one(feature, element):

        l = feature._getList(element)

        if not l:
            value = feature._defaultValue
            if value is NOT_GIVEN:
                raise AttributeError,feature.attrName
            return value

        return l[0]


    _get_one.installIf = lambda f, m: not f.isMany
    _get_one.verb      = 'get'



    def _set_one(feature, element, val):
        feature.__delete__(element)
        feature._notifyLink(element,val)

    _set_one.installIf = lambda f,m: f.isChangeable and not f.isMany
    _set_one.verb      = 'set'



    def _unset_one(feature, element):
        l = feature._getList(element)
        if l:
            feature._notifyUnlink(element,l[0])

    _unset_one.installIf = lambda f,m: f.isChangeable and not f.isMany
    _unset_one.verb      = 'unset'







    def _getList_many(feature, element):
        return element._getBinding(feature.implAttr, [], feature.useSlot)

    _getList_many.installIf = lambda f,m: f.isMany and not f.isDerived
    _getList_many.verb      = '_getList'


    def _getList_one(feature, element):
    
        value = element._getBinding(
            feature.implAttr, NOT_FOUND, feature.useSlot
        )

        if value is NOT_FOUND:
            return []

        return [value]

    _getList_one.installIf = lambda f, m: not f.isMany and not f.isDerived
    _getList_one.verb      = '_getList'


    def _getList(feature, element):
        """This must be defined in subclass"""
        raise NotImplementedError

    _getList.installIf = lambda f, m: f.isDerived














    def _set_many(feature, element, val):

        feature.__delete__(element)
        add = feature._notifyLink

        for v in val:
            add(element,v)

    _set_many.installIf = lambda f,m: f.isChangeable and f.isMany
    _set_many.verb      = 'set'


    def replace(feature, element, oldItem, newItem):

        d = feature._getList(element)

        if oldItem in d:
            p = d.index(oldItem)
            feature._notifyUnlink(element,oldItem,p)
            feature._notifyLink(element,newItem,p)

        else:
            raise ValueError("Can't replace missing item", oldItem)

    replace.installIf = lambda f,m: f.isChangeable and f.isMany
















    def _unset_many(feature, element):

        """Unset the value of the feature (like __delattr__)"""

        d = feature._getList(element)

        items = zip(range(len(d)),d)
        items.reverse()

        remove = feature._notifyUnlink

        # remove items in reverse order, to simplify deletion and
        # to preserve any invariant that was relevant for addition
        # order...
        
        for posn,item in items:
            remove(element,item,posn)
            
        element._delBinding(feature.implAttr,feature.useSlot)


    _unset_many.installIf = lambda f,m: f.isChangeable and f.isMany
    _unset_many.verb      = 'unset'


















    def add(feature, element, item, posn=None):

        """Add the item to the collection/relationship"""      

        feature._notifyLink(element,item,posn)

    add.installIf = lambda f,m: f.isChangeable and f.isMany


    def _notifyLink(feature, element, item, posn=None):

        item = feature._link(element,item,posn)
        referencedEnd = feature.referencedEnd

        if referencedEnd:
            otherEnd = getattr(item.__class__,referencedEnd)
            otherEnd._link(item,element)

    _notifyLink.installIf = installIfChangeable


    def remove(feature, element, item, posn=None):

        """Remove the item from the collection/relationship, if present"""

        feature._notifyUnlink(element,item,posn)

    remove.installIf = lambda f,m: f.isChangeable and f.isMany


    def _notifyUnlink(feature, element, item, posn=None):

        feature._unlink(element,item,posn)
        referencedEnd = feature.referencedEnd

        if referencedEnd:
            otherEnd = getattr(item.__class__,referencedEnd)
            otherEnd._unlink(item,element)

    _notifyUnlink.installIf = installIfChangeable

    def _link(feature,element,item,posn=None):

        ub = feature.upperBound
        d=feature._getList(element)

        if ub and len(d)>=ub:
            raise ValueError("Too many items")

        item = feature.normalize(item)
        feature._onLink(element,item,posn)

        if ub==1:
            element._setBinding(feature.implAttr, item, feature.useSlot)
            return item

        element._setBinding(feature.implAttr, d, feature.useSlot)

        if posn is None:
            d.append(item)
        else:
            d.insert(posn,item)
        return item

    _link.installIf = installIfChangeable
    _link.verb      = '_link'
















    def _unlink(feature,element,item,posn=None):

        feature._onUnlink(element,item,posn)
        if not feature.isMany:
            return element._delBinding(feature.implAttr)

        d=feature._getList(element)
        element._setBinding(feature.implAttr, d, feature.useSlot)

        if posn is None:
            d.remove(item)
        else:
            del d[posn]

    _unlink.installIf = installIfChangeable
    _unlink.verb      = '_unlink'


    def _onLink(feature,element,item,posn):
        pass


    def _onUnlink(feature,element,item,posn):
        pass

















    def _setup(feature,element,value):

        if feature.isChangeable:
            return feature.set(element,value)

        doLink = feature._onLink
        normalize = feature.normalize
        
        if feature.isMany:
            p = 0
            value = tuple(map(normalize,value))

            for v in value:
                doLink(element,value,p)
                p+=1

        else:
            doLink(element,normalize(value),0)

        element._setBinding(feature.implAttr,value,feature.useSlot)





















    def insertBefore(feature, element, oldItem, newItem):

        d = feature._getList(element)

        if oldItem in d:
            feature._notifyLink(element,newItem,d.index(oldItem))
        else:
            raise ValueError("Can't insert before missing item", oldItem)

    insertBefore.installIf = lambda f,m: f.isOrdered and f.isChangeable































class Collection(StructuralFeature):
    pass



class Attribute(StructuralFeature):

    upperBound = 1



class structField(StructuralFeature):

    """An unchangeable attribute; used for immutables"""

    upperBound = 1

    isChangeable = binding.classAttr( binding.Constant(None, False) )



class DerivedFeature(StructuralFeature):

    isDerived = True



class Sequence(StructuralFeature):

    isOrdered = True




Reference = Attribute               # XXX backward compatibility...  deprecated
Field = Attribute                   # XXX backward compatibility...  deprecated
DerivedAssociation = DerivedFeature # XXX backward compatibility...  deprecated






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
]




















class FeatureClass(HashAndCompare,MethodExporter):

    """Method-exporting Property (metaclass for StructuralFeature)
    
        This metaclass adds property support to 'MethodExporter' by adding
        '__get__', '__set__', and '__delete__' methods, which are delegated
        to the method templates for the 'get', 'set' and 'unset' verbs.

        In other words, if you define a feature 'foo', following standard
        naming patterns for its 'set', 'get' and 'unset' verbs, and 'bar' is
        an Element whose class includes the 'foo' feature, then 'bar.foo = 1'
        is equivalent to 'bar.setFoo(1)'.  Similarly, referencing 'bar.foo' by
        itself is equivalent to 'bar.getFoo()', and 'del bar.foo' is equivalent
        to 'bar.unsetFoo()'.

        Please see the 'peak.model.method_exporter.MethodExporter' class
        documentation for more detail on how method templates are defined,
        the use of naming conventions, verbs, template variants, etc."""

    __metaclass__ = binding.Activator   # metaclasses can't be components


    def __get__(self, ob, typ=None):

        """Get the feature's value by delegating to 'ob.getX()'"""

        if ob is None: return self
        return self.get(ob)


    def __set__(self, ob, val):
        """Set the feature's value by delegating to 'ob.setX()'"""

        if self.isChangeable:
            self.set(ob,val)
        else:
            raise AttributeError("Unchangeable feature",self.attrName)




    def __delete__(self, ob):
        """Delete the feature's value by delegating to 'ob.unsetX()'"""

        if self.isChangeable:
            self.unset(ob)
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

    _bindFuncs = binding.Once(
        lambda s,d,a:
            s.getParentComponent()._getBindingFuncs(s.implAttr,s.useSlot)
    )

    _doGet = binding.Once(lambda s,d,a: s._bindFuncs[0])
    _doSet = binding.Once(lambda s,d,a: s._bindFuncs[1])
    _doDel = binding.Once(lambda s,d,a: s._bindFuncs[2])

    singularName = binding.bindTo('./attrName')



    rawTypeCode = binding.bindTo('typeObject/mdl_typeCode')
    typeKind    = binding.bindTo('typeCode/kind')
    typeCode    = binding.Once(lambda s,d,a: s.rawTypeCode.unaliased() )






































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
        add     = 'add%(singularName.initCap)s',
        remove  = 'remove%(singularName.initCap)s',
        replace = 'replace%(singularName.initCap)s',
        insertBefore = 'insert%(singularName.initCap)sBefore',
    )














    def get(f):

        if f.isDerived:

            def get(feature,element):
                raise NotImplementedError

        elif f.isMany:

            def get(feature,element):
                try:
                    return feature._doGet(element)
                except AttributeError:
                    return []
            
        else:

            def get(feature,element):
                try:
                    return feature._doGet(element)
                except AttributeError:
                    value = feature._defaultValue
                    if value is NOT_GIVEN:
                        raise AttributeError,feature.attrName
                    return value
            
        return get


    get.isTemplate = True











    def set(f):

        if not f.isChangeable:
            set = None

        elif f.isMany:
        
            def set(feature, element, val):

                feature.unset(element)
                add = feature._notifyLink

                for v in val:
                    add(element,v)

        else:
        
            def set(feature, element, val):
                feature.unset(element)
                feature._notifyLink(element,val)

        return set

    set.isTemplate = True

















    def unset(f):

        if not f.isChangeable:
            unset = None

        elif f.isMany:

            def unset(feature, element):

                d = feature.get(element)

                items = zip(range(len(d)),d)
                items.reverse()

                remove = feature._notifyUnlink

                # remove items in reverse order, to simplify deletion and
                # to preserve any invariant that was relevant for addition
                # order...
        
                for posn,item in items:
                    remove(element,item,posn)
            
                feature._doDel(element)

        else:

            def unset(feature, element):
                try:
                    item = feature._doGet(element)
                except AttributeError:
                    pass
                else:
                    feature._notifyUnlink(element,item)

        return unset


    unset.isTemplate = True


    def replace(feature, element, oldItem, newItem):

        d = feature.get(element)

        if oldItem in d:
            p = d.index(oldItem)
            feature._notifyUnlink(element,oldItem,p)
            feature._notifyLink(element,newItem,p)

        else:
            raise ValueError("Can't replace missing item", oldItem)

    replace.installIf = lambda f,m: f.isChangeable and f.isMany



    def add(f):
        # Hardwire straight to _notifyLink(feature,element,item,posn=None)
        return f.methodTemplates['_notifyLink'](f)

    add.installIf  = lambda f,m: f.isChangeable and f.isMany
    add.isTemplate = True


    def remove(f):
        # Hardwire straight to _notifyUnlink(feature,element,item,posn=None)
        return f.methodTemplates['_notifyUnlink'](f)

    remove.installIf  = lambda f,m: f.isChangeable and f.isMany
    remove.isTemplate = True











    def _notifyLink(f):

        _link = f.methodTemplates['_link'](f)
        refEnd = f.referencedEnd

        if not f.isChangeable:
            _notifyLink = None

        elif refEnd:

            def _notifyLink(feature, element, item, posn=None):
                item     = _link(feature,element,item,posn)
                otherEnd = getattr(item.__class__, refEnd)
                otherEnd._link(item,element)

        else:
            # Return the _link method "in line"; _notify isn't needed
            _notifyLink = _link

        return _notifyLink


    _notifyLink.verb       = '_notifyLink'
    _notifyLink.isTemplate = True

















    def _notifyUnlink(f):

        _unlink = f.methodTemplates['_unlink'](f)
        refEnd = f.referencedEnd

        if not f.isChangeable:
            _notifyUnlink = None

        elif refEnd:

            def _notifyUnlink(feature, element, item, posn=None):
                _unlink(feature,element,item,posn)
                otherEnd = getattr(item.__class__, refEnd)
                otherEnd._unlink(item,element)

        else:
            # Return the _link method "in line"; _notify isn't needed
            _notifyUnlink = _unlink

        return _notifyUnlink


    _notifyUnlink.verb       = '_notifyUnlink'
    _notifyUnlink.isTemplate = True

















    def _link(f):

        if not f.isChangeable:
            _link = None

        elif f.isMany:

            def _link(feature,element,item,posn=None):

                ub = feature.upperBound
                d=feature.get(element)

                if ub and len(d)>=ub:
                    raise ValueError("Too many items")

                item = feature.normalize(item)
                feature._onLink(element,item,posn)

                feature._doSet(element,d)

                if posn is None:
                    d.append(item)
                else:
                    d.insert(posn,item)
                return item

        else:

            def _link(feature,element,item,posn=None):

                item = feature.normalize(item)
                feature._onLink(element,item,posn)
                feature._doSet(element,item)
                return item

        return _link

    _link.verb       = '_link'
    _link.isTemplate = True


    def _unlink(f):

        if not f.isChangeable:
            _unlink = None

        elif f.isMany:

            def _unlink(feature,element,item,posn=None):

                feature._onUnlink(element,item,posn)
                d=feature.get(element)
                feature._doSet(element,d)

                if posn is None:
                    d.remove(item)
                else:
                    del d[posn]

        else:

            def _unlink(feature,element,item,posn=None):
                feature._onUnlink(element,item,posn)
                feature._doDel(element)

        return _unlink


    _unlink.verb       = '_unlink'
    _unlink.isTemplate = True



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

        feature._doSet(element,value)





















    def insertBefore(feature, element, oldItem, newItem):

        d = feature.get(element)

        if oldItem in d:
            feature._notifyLink(element,newItem,d.index(oldItem))
        else:
            raise ValueError("Can't insert before missing item", oldItem)

    insertBefore.installIf = lambda f,m: (
        f.isOrdered and f.isMany and f.isChangeable
    )





























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













"""peak.model Interfaces"""

from Interface import Interface
from Interface.Attribute import Attribute

__all__ = [
    'IFeature','IFeatureSPI',
    'IClassifier',
    'IEnumClass', 'IEnumValue',
]































class IClassifier(Interface):

    """A model type"""


    def mdl_fromString(aString):
        """Return an instance of type created based on 'aString'"""
    
    def mdl_fromFields(fieldSequence):
        """Return an instance of type created based on 'fieldSequence'

        'fieldSequence' must be an iterable object whose contents
        are the values of the features named by 'mdl_featureNames',
        in that order."""



    mdl_isAbstract = Attribute(
        """Is this an abstract class?  If so, instances can't be created."""
    )

    mdl_featuresDefined = Attribute(
        """Sorted tuple of feature objects defined/overridden by this class"""
    )

    mdl_featureNames = Attribute(
        """Names of all features, in monotonic order (see 'mdl_features')"""
    )

    mdl_sortedFeatures = Attribute(
        """All feature objects of this classifier, in sorted order"""
    )

    mdl_compositeFeatures = Attribute(
        """Ordered subset of 'mdl_features' that are composite"""
    )





    mdl_features = Attribute(
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
                class foo(model.Attribute): pass
                
            class B(A):
                class foo(model.Attribute): pass
                class bar(model.Attribute): pass

        would result in 'B' having a 'mdl_features' order of '(foo,bar)',
        even though its 'mdl_featuresDefined' would be '(bar,foo)' (because
        features without a sort priority define are ordered by name).

        The purpose of using a monotonic ordering like this is that it allows
        subtypes to use a serialized format that is a linear extension of
        their supertype, at least in the case of single inheritance.  It may
        also be useful for GUI layouts, where it's also desirable to have a
        subtype's display look "the same" as a base type's display, except for
        those features that it adds to the supertype."""
    )










class IEnumClass(IClassifier):

    """An enumerated type"""

    def __getitem__(nameOrValue):
        """Return the enumeration value for the name or value 'nameOrValue'
        
            Raises 'exceptions.EnumerationError' if not found
        """
        
    def get(nameOrValue, default=None):
        """Return the enumeration value for the name or value 'nameOrValue'

            Returns 'default' if not found
        """

    def __contains__(value):
        """Return true if 'value' is a valid enumeration name or value"""

    def __iter__():
        """Iterator over the sorted sequence of all of this enum's instances"""


class IEnumValue(Interface):

    """An enumeration instance"""

    name = Attribute("""The name of this enumeration value""")

    def __hash__():
        """Hash of the enumeration instance's value"""

    def __cmp__():
        """Enumeration instances compare equal to their value"""







class IFeature(Interface):

    lowerBound   = Attribute(
        """Lower bound of multiplicity"""
    )

    upperBound   = Attribute(
        """Upper bound of multiplicity; 'None' means "unbounded"""
    )

    isRequired   = Attribute(
        """True if 'lowerBound' is greater than zero"""
    )

    isOrdered    = Attribute(
        "True means the feature is an ordered sequence"
    )

    isChangeable = Attribute(
        "True means feature is changeable"
    )

    isDerived    = Attribute(
        """True means feature is derived (implies 'not isChangeable')"""
    )

    isMany       = Attribute(
        """True means 'upperBound > 1'; i.e., this is a "plural" feature"""
    )

    isReference  = Attribute(
        """True if feature references a non-primitive/non-struct object type"""
    )

    attrName     = Attribute(
        """Name of the attribute the feature implements"""
    )




    typeObject   = Attribute(
        """'IClassifier' instance representing the type of the feature"""
    )

    def fromString(aString):
        """See 'IClassifier.mdl_fromString()'"""
        
    def fromFields(fieldSequence):
        """See 'IClassifier.mdl_fromFields()'"""

    def __get__(element,type=None):
        """Retrieve value of the feature for 'element'"""

    def __set__(element,value):
        """Set 'value' as the value of the feature for 'element'"""

    def __delete__(element):
        """Unset the feature for 'element' (works like __delattr__)"""

    def add(element,item):
        """Add the item to the collection/relationship, reject if multiplicity
        exceeded"""

    def remove(element,item):
        """Remove the item from the collection/relationship, if present"""

    def replace(element,oldItem,newItem):
        """Replace oldItem with newItem in the collection; raises ValueError
        if oldItem is missing"""

    def insertBefore(element,oldItem,newItem):
        """Insert newItem before oldItem in the collection; raises ValueError
        if oldItem is missing, TypeError if feature is not ordered"""

    referencedEnd = Attribute(
        """Name of the inverse feature on the target class

        'None' means this is a unidirectional reference."""
    )


class IFeatureSPI(Interface):

    # SPI calls used for feature-to-feature collaboration and internal
    # implementation

    implAttr = Attribute(
        """Name of the actual attribute used to store the feature

        (Defaults to the same as 'attrName')"""
    )

    referencedType = Attribute(
        """The 'IClassifier' for 'typeObject', or a name to find it by"""
    )

    def get(element):
        """Return the value of the feature for 'element'"""

    def set(element,value):
        """Set the value of the feature for 'element'"""

    def _getList(element):
        """Return the value(s) of the feature for 'element' as a sequence"""

    def _notifyLink(element,posn=None):
        """Link to element, inserting it at 'posn' in our value"""
        
    def _notifyUnlink(element,posn=None):
        """Unlink from element, removing it from 'posn' in our value"""

    def _link(element,posn=None):
        """Link to element without notifying the inverse feature"""
        
    def _unlink(element,posn=None):
        """Unlink from element without notifying the inverse feature"""


    


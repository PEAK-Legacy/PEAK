"""TransWarp Service-Element-Feature Interfaces

  Some of these interfaces are applicable only to the older form of the SEF
  framework which uses the 'element.feature.verb()' style, instead of the
  newer 'element.verbFeature()' style.  Specifically, 'IFeature' and its
  derivative interfaces are not correctly defined relative to the new-style
  API.  I can't get rid of these in the 0.2 release cycle, however, because
  all the UML model stuff still uses the old-style API, and I won't be
  refactoring them for 0.2.
"""

import Interface

__all__ = [
    'ISEF','IService','ISpecialist','IElement','IFeature','IQuerying',
    'IClassifier','IDataType','IPrimitiveType', 'IEnumeration',
    'IValue','ICollection','IReference','ISequence',
]























class ISEF(Interface.Base):

    """Basic interface supplied by all StructuralModel objects"""

    def lookupComponent(name):
        """Look up a name in context - see 'binding.lookupComponent()'"""

    def getParentComponent():
        """Return the parent component of this object

            If this is a feature, returns the element.  If this is an element,
            return the controlling service.  If this is a service, return the
            containing service (or 'None' if this is the root service).
        """


class IService(ISEF):
    """A component instance compatible with the S-E-F framework"""























class IQuerying(Interface.Base):

    def Get(name,recurse=None):
        """Return a sequence representing SEF child 'name', w/optional recursion

            If this is a service, return elements of type name 'name'.  If this
            is an element, return the 'values()' of the feature named 'name'.
            If this is a feature, return the concatenation of applying 'Get(name)'
            to 'self.values()'.

            If the 'recurse' flag is true, or 'name' ends in an asterisk
            ('"*"'), then reapply 'Get(name,recurse)' recursively to the
            resulting sequence and append the results until no more reuslts are
            obtained.

            The returned sequence *must* be an object which implements the
            IQuerying interface by (effectively) mapping its 'Get()' and
            'Where()' methods over its contents.
        """
            
    def Where(criteria=None):
        """Filter contents by 'criteria' predicate

            If this is a service, return elements meeting 'criteria'.  If this
            is an element, return a sequence which is either empty or contains
            self if self meets 'criteria'.  If this is a feature, return those
            elements of 'self.values()' which meet 'criteria'.
            
            'criteria' must be a callable object taking one parameter and
            returning a true or false value, indicating whether the passed item
            is acceptable.

            The returned sequence *must* be an object which implements the
            IQuerying interface by (effectively) mapping its 'Get()' and
            'Where()' methods over its contents.
        """





class ISpecialist(IService):

    """A service responsible for a (possibly abstract) datatype

       TODO:
       
        Over time, this interface should evolve to include metadata about the
        type...  marshalling support...  ???
        
    """
    
    def newItem(key=None):
        """Create a new Element of the type managed by the service"""
        
    def getItem(key, default=None):
        """Retrieve an existing Element; return 'default' if not found"""

    def __getitem__(key):
        """Retrieve an existing element; raise KeyError if not found"""






















class IClassifier(ISEF):
    """Basis for all flavors"""

class IPrimitiveType(IClassifier):
    """A primitive type (e.g. Boolean, String, etc.)"""

class IEnumeration(IClassifier):
    """An enumerated type"""

class IDataType(IClassifier):
    """A complex datatype"""
        
class IElement(IDataType):        
    """An instance of an application-domain object"""



























class IFeature(ISEF):

    lowerBound = Interface.Attribute(
        """Lower bound of multiplicity; 0 unless overridden in class definition
        or by isRequired"""
    )

    upperBound = Interface.Attribute(
        "Upper bound of multiplicity; None=unbounded"
    )

    isRequired = Interface.Attribute(
        "May be set to true in class definition to force lowerBound=1"
    )

    isOrdered     = Interface.Attribute(
        "Flag for whether feature is ordered sequence"
    )

    isChangeable  = Interface.Attribute(
        "Flag for whether feature is changeable"
    )

    def getElement():
        """Retrieve the Element to which this Feature belongs"""

    def getReferencedType():
        """Retrieve the Service representing the type this Feature references"""

    def __call__():
        """Return the value of the feature"""

    def values():
        """Return the value(s) of the feature as a sequence, even if it's a single value"""

    def set(value):
        """Set the value of the feature to value"""

    def clear():
        """Unset the value of the feature, like del or set(empty/None)"""

    # SPI calls used for feature-to-feature collaboration
    
    def _link(element):
        """Link to element without notifying other end"""
        
    def _unlink(element):
        """Unlink from element without notifying other end"""


































class IValue(IFeature):

    def marshal(*args,**kw):
        """Convert args[0] or kwargs into an 'item' suitable for use with the other methods.
           Raises ValueError if invalid format."""


class ICollection(IFeature):
    """A feature which is a collection of items which may be added or removed."""

    def isEmpty():
        """Return true if the value is not set or collection is empty"""

    def isReferenced(item):
        """Return true if the item is a member of the set/sequence"""

    def addItem(item):
        """Add the item to the collection/relationship, reject if multiplicity
        exceeded"""

    def removeItem(item):
        """Remove the item from the collection/relationship, if present"""

    def replaceItem(oldItem,newItem):
        """Replace oldItem with newItem in the collection; raises ValueError
        if oldItem is missing"""


class IReference(ICollection):
    """A single-valued collection; upperBound==1"""


class ISequence(ICollection):

    """An ordered collection; isOrdered==1"""
    
    def insertBefore(oldItem,newItem):
        """Insert newItem before oldItem in the collection; raises ValueError
        if oldItem is missing, TypeError if feature is not ordered"""


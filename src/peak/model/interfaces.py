"""TransWarp Service-Element-Feature Interfaces

  Note that these interfaces do not comprise the entire Service-Element-Feature
  pattern, but only its *structural* aspect.  Other interfaces can and should
  be implemented to represent other aspects in the appropiate horizontal
  frameworks.  For example, a Zope/ZPublisher framework would probably want
  to have its own ITypeService, IElement, and IFeature interfaces that included
  an 'index_html' method with the appropriate meaning for each type of object.
  (i.e., a "Find/add objects of type foo", "View this instance of type foo",
  and "a management screen of instances of type foo", respectively.)

  (Note: the above was obviously written pre-Zope 3 component architecture, but
  I'm going to leave it alone for this documentation pass, which is to clean up
  the major atrocities, not to pick nits with the examples. ;-)
"""

import Interface

__all__ = [
    'ISEF','IService','ITypeService','IElement','IFeature','IQuerying',
    'IClassifier','IDataType','IPrimitiveType', 'IEnumeration',
    'IValue','ICollection','IReference','ISequence'
]


















class ISEF(Interface.Base):

    """Basic interface supplied by all StructuralModel objects"""

    _componentName = Interface.Attribute(
        """Name of this component in its immediate context"""
    )

    def getService(self,name=None):
        """Locate a service in context

            If 'name' is not supplied, return the Service object which is
            responsible for the object this method is called on.  (Aka
            "the responsible Service".) In the case of a Feature, that
            would be the Service responsible for the Feature's Element.

            If 'name' is supplied, it must be a string containing a dotted
            name, or a sequence of path components (e.g. '"foo.bar"' or
            '("foo","bar")' are valid names).  The contextually closest
            Service to the "responsible Service" which matches the name
            will be returned.  An exception may result if the named Service
            does not exist.
        """

    def getSEFparent(self):
        """Return the parent of this object (in S-E-F terms)

            If this is a feature, returns the element.  If this is an element,
            return the controlling service.  If this is a service, return the
            containing service (or self if none).
        """


class IService(ISEF):
    """A component instance compatible with the S-E-F framework"""






class IQuerying(Interface.Base):

    def Get(self,name,recurse=None):
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
            
    def Where(self,criteria=None):
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





class ITypeService(IService):

    """A component instance responsible for a (possibly abstract) datatype

       TODO:
       
        Over time, this interface should evolve to include metadata about the
        type...  marshalling support...  ???
        
    """
    
    def newItem(self,*args,**kw):
        """Create a new Element of the type managed by the service"""
        
    def getItem(self,*args,**kw):
        """Retrieve an existing Element of the type managed by the service"""

























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

    def getElement(self):
        """Retrieve the Element to which this Feature belongs"""
        
    def getReferencedType(self):
        """Retrieve the Service representing the type this Feature references"""

    def __call__(self):
        """Return the value of the feature"""

    def values(self):
        """Return the value(s) of the feature as a sequence, even if it's a single value"""

    def set(self,value):
        """Set the value of the feature to value"""

    def clear(self):
        """Unset the value of the feature, like del or set(empty/None)"""

    # SPI calls used for feature-to-feature collaboration
    
    def _link(self,element):
        """Link to element without notifying other end"""
        
    def _unlink(self,element):
        """Unlink from element without notifying other end"""


































class IValue(IFeature):

    def marshal(self,*args,**kw):
        """Convert args[0] or kwargs into an 'item' suitable for use with the other methods.
           Raises ValueError if invalid format."""


class ICollection(IFeature):
    """A feature which is a collection of items which may be added or removed."""

    def isEmpty(self):
        """Return true if the value is not set or collection is empty"""

    def isReferenced(self,item):
        """Return true if the item is a member of the set/sequence"""

    def addItem(self,item):
        """Add the item to the collection/relationship, reject if multiplicity
        exceeded"""

    def removeItem(self,item):
        """Remove the item from the collection/relationship, if present"""

    def replaceItem(self,oldItem,newItem):
        """Replace oldItem with newItem in the collection; raises ValueError
        if oldItem is missing"""


class IReference(ICollection):
    """A single-valued collection; upperBound==1"""


class ISequence(ICollection):

    """An ordered collection; isOrdered==1"""
    
    def insertBefore(self,oldItem,newItem):
        """Insert newItem before oldItem in the collection; raises ValueError
        if oldItem is missing, TypeError if feature is not ordered"""


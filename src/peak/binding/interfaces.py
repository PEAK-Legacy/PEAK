"""PEAK Component Binding Interfaces"""

from peak.interface import Interface, Attribute
from peak.config.interfaces import IConfigurable, IConfigSource

__all__ = [
    'IBindingFactory', 'IBindingSPI', 'IBindingAPI', 'IComponent',
]


class IBindingFactory(Interface):

    """Class interface for creating bindable components"""

    def __call__(parentComponent=None, componentName=None, **attrVals):
        """Create a new component

        The default constructor signature of a binding component is
        to receive an optional parent to be bound to, an optional name
        relative to the parent, and keyword arguments which will be
        placed in the new object's dictionary, to override the specified
        bindings."""


class IBindingSPI(IConfigSource):

    """Minimum requirements to join a component hierarchy"""

    def getParentComponent():
        """Return the parent component of this object, or 'None'"""

    def getComponentName():
        """Return this component's name relative to its parent, or 'None'"""








class IBindingAPI(IBindingSPI):

    """API supplied by binding.Base and its subclasses

    peak.model's 'StructuralFeature' classes rely on this interface."""

    def lookupComponent(name):
        """Look up a name in context - see 'binding.lookupComponent()'"""


    def setParentComponent(parentComponent,componentName=None,suggest=False):
        """Set the object's parent to 'parentComponent' (or suggest it)

        If 'suggest' is true, this should not change an already-specified
        parent.  If 'suggest' is false, and the current parent has already been
        used by the component for any purpose, this method raises an
        'AlreadyRead' exception.

        The component's 'componentName' will only be set if the parent is
        successfully set."""


    def _hasBinding(attr,useSlot=False):
        """Return true if binding named 'attr' has been activated"""

    def _getBinding(attr,default=None,useSlot=False):
        """Return binding named 'attr' if activated, else return 'default'"""

    def _setBinding(attr,value,useSlot=False):
        """Set binding 'attr' to 'value'"""

    def _delBinding(attr,useSlot=False):
        """Ensure that no binding for 'attr' is active"""



class IComponent(IBindingAPI, IConfigurable):

    """API supplied by binding.Components"""



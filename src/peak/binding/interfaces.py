"""PEAK Component Binding Interfaces"""

from peak.interface import Interface, Attribute
from peak.config.interfaces import IConfigurable, IConfigSource
from peak.api import NOT_GIVEN

__all__ = [
    'IComponentFactory', 'IBindingNode', 'IComponent',
    'IBindableAttrs',
]


class IComponentFactory(Interface):

    """Class interface for creating bindable components"""

    def __call__(parentComponent, componentName=None, **attrVals):
        """Create a new component

        The default constructor signature of a binding component is
        to receive an parent component to be bound to, an optional name
        relative to the parent, and keyword arguments which will be
        placed in the new object's dictionary, to override the specified
        bindings.

        Note that some component factories (such as 'binding.Component')
        may be more lenient than this interface requires, by allowing you to
        omit the 'parentComponent' argument.  But if you do not know this is
        true for the object you are calling, you should assume the parent
        component is required."""











class IBindingNode(IConfigSource):

    """Minimum requirements to join a component hierarchy"""

    def getParentComponent():
        """Return the parent component of this object, or 'None'"""

    def getComponentName():
        """Return this component's name relative to its parent, or 'None'"""

    def notifyUponAssembly(child):
        """Call 'child.uponAssembly()' when component knows its root"""



class IBindableAttrs(Interface):

    """Support for manipulating bindable attributes

    (peak.model's 'StructuralFeature' classes rely on this interface.)"""

    def _getBindingFuncs(attrName, useSlot=False):
        """XXX"""

    def _hasBinding(attr,useSlot=False):
        """Return true if binding named 'attr' has been activated"""

    def _getBinding(attr,default=None,useSlot=False):
        """Return binding named 'attr' if activated, else return 'default'"""

    def _setBinding(attr,value,useSlot=False):
        """Set binding 'attr' to 'value'"""

    def _delBinding(attr,useSlot=False):
        """Ensure that no binding for 'attr' is active"""






class IComponent(IBindingNode, IBindableAttrs, IConfigurable):

    """API supplied by binding.Component and its subclasses"""

    def lookupComponent(name, default=NOT_GIVEN, creationName=None):
        """Look up 'name' in context - see 'binding.lookupComponent()'"""


    def setParentComponent(parentComponent,componentName=None,suggest=False):
        """Set the object's parent to 'parentComponent' (or suggest it)

        If 'suggest' is true, this should not change an already-specified
        parent.  If 'suggest' is false, and the current parent has already been
        used by the component for any purpose, this method raises an
        'AlreadyRead' exception.

        The component's 'componentName' will only be set if the parent is
        successfully set."""


    def uponAssembly():
        """Notify the component that its parents and root are known+fixed"""




















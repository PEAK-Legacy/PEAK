"""PEAK Component Binding Interfaces"""

from Interface import Interface
from Interface.Attribute import Attribute

__all__ = [
    'IBindingSPI', 'IBindingAPI',
]

































class IBindingSPI(Interface):

    """Minimum requirements to join a component hierarchy"""

    def lookupComponent(name):
        """Look up a name in context - see 'binding.lookupComponent()'"""

    def getParentComponent():
        """Return the parent component of this object, or 'None'"""


    def _getConfigData(configKey, forObj):

        """Return a value of 'configKey' for 'forObj' or 'NOT_FOUND'

        Note that 'configKey' is an IConfigKey instance and may therefore be
        a 'naming.PropertyName' or an 'Interface' object.  'binding.Base'
        implements this method by simply returning 'NOT_FOUND', and that is
        a perfectly acceptable implementation for many purposes."""






















class IBindingAPI(IBindingSPI):

    """API supplied by binding.Base and its subclasses

    peak.model's 'StructuralFeature' classes rely on this interface."""


    def __init__(parent=None, **kw):
        """The default constructor signature of a binding component is
        to receive an optional parent to be bound to, and keyword arguments
        which will be placed in the new object's dictionary, to override
        the specified bindings."""


    def setParentComponent(parent):
        """Set the object's parent to 'parent'; raises 'AlreadyRead' if
        the parent has already been used by the component for any purpose."""
        

    def _hasBinding(attr):
        """Return true if binding named 'attr' has been activated"""

    def _getBinding(attr,default=None):
        """Return binding named 'attr' if activated, else return 'default'"""

    def _setBinding(attr,value):
        """Set binding 'attr' to 'value'"""

    def _delBinding(attr):
        """Ensure that no binding for 'attr' is active"""














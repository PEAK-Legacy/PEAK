"""Service Provider Interface

    Core functions for implementing naming services.  These are
    Pythonic equivalents to some of the static methods provided by
    'NamingManager' and 'DirectoryManager' in the JNDI 'javax.naming.spi'
    package.  For Python, it makes more sense to have these as
    module-level functions than as static methods of classes.

    Note that if you just want to *use* naming services, you don't need
    to worry about this.  These are just a few simple "policy" methods
    that control how initial context and URL context objects are created,
    based on component properties.  They simplify the implementation of
    context objects by allowing them to focus on their own issues instead
    of on framework-oriented concerns.
"""

from peak.util.imports import importObject

from interfaces import *
from names import NNS_Reference

from peak.binding.interfaces import IComponentFactory

__all__ = [
    'getInitialContext', 'getURLContext',
]


__implements__ = (
    IURLContextFactory, IInitialContextFactory, IObjectFactory
)










def getInitialContext(parentComponent, componentName=None, **options):

    """Create initial context for parent, w/component name and options

    The type of initial context created is determined by asking the supplied
    'parentComponent' for its 'peak.naming.initialContextFactory' property,
    which will be treated as an import string if it is of string type.
    (Note: the property name used is available as the constant
    'naming.INIT_CTX_FACTORY', if you want to provide an attribute binding
    for it.)

    Keyword options and the component name desired for the initial context
    are passed through to the actual factory, along with the parent component
    and component name.  If a 'creationParent' argument is not supplied,
    it will be defaulted to 'parentComponent', in order to establish the
    parent component for any newly created objects retrieved from the
    resulting context object.
    """

    factory = importObject( INIT_CTX_FACTORY(parentComponent) )
    options.setdefault('creationParent',parentComponent)
    return factory(parentComponent, componentName, **options)


getInitialContext.__implements__ = IComponentFactory
















def getURLContext(parent, scheme, iface, componentName=None, **options):

    """Return a context object for the given URL scheme and interface

        This is done by looking up 'scheme' in the 'peak.naming.schemes.*'
        property namespace.  (That is, the '"ldap:"' URL scheme is retrieved
        from the 'peak.naming.schemes.ldap' property.  Per RFC 1738, the
        lowercase form of the scheme name is always used; note that the '":"'
        should not be included in the scheme name.)  The property value
        found, if a string, will be treated as an import specification, and
        the relevant object imported.

        The property value or imported object must do one of the following:

        * Implement 'naming.IURLContextFactory', in which case its
          'getURLContext()' method will be called with the same arguments
          as supplied to this function.

        * Be a class whose instances implement the requested context interface
          (e.g. 'naming.IBasicContext'), in which case an instance will be
          constructed and returned, using 'parent' as its parent component,
          and 'componentName' as its name.  (Note that the class must also
          implement the 'binding.IComponentFactory' constructor signature for
          this to work.)

        * Be a class whose instances implement 'naming.IAddress', in which case
          a generic 'AddressContext' will be returned, with its 'schemeParser'
          set to the appropriate address class.

        If none of these conditions apply, or the property isn't found in the
        first place, this function returns 'None', as per the
        'naming.IURLContextFactory' interface.
    """

    factory = SCHEMES_PREFIX.of(parent).get(scheme.lower())

    if factory is not None:

        factory = importObject(factory)


        if IURLContextFactory.isImplementedBy(factory):

            return factory.getURLContext(
                parent, scheme, iface, componentName, **options
            )

        elif iface.isImplementedByInstancesOf(factory):

            return factory(
                parent, componentName, **options
            )

        elif isAddressClass(factory):

            from contexts import AddressContext

            return AddressContext(
                parent, componentName, schemeParser=factory, **options
            )

    return None




















def getObjectInstance(context, refInfo, name, attrs=None):

    """Default rules for loading objects from state

    If 'refInfo' implements 'naming.IAddress', this will return the
    result of invoking its 'retrieve()' method with the supplied
    parameters.

    Otherwise, if 'refInfo' is an instance of 'naming.NNS_Reference',
    the reference will be unwrapped and the contained object returned.
    This ensures that if no object factories are available that interpret
    NNS references, name resolution will be able to continue in the same
    naming system.  That is, this is a cushion to support "weak" naming
    system boundaries.

    Otherwise, 'None' is returned, allowing object factory lookups to
    continue.

    It is not recommended that you call this function directly.  It is
    intended to be used by registering the 'peak.naming.spi' module as a
    utility for the 'naming.IObjectFactory' interface, so that it will
    be found by context objects searching for their object factories.
    It is also intended to be found *last*, so that any more-specific
    handlers will be tried first.
    """

    if isAddress(refInfo):
        return refInfo.retrieve(refInfo, name, context, attrs)

    elif isinstance(refInfo, NNS_Reference):
        # default is to treat the object as its own NNS
        return refInfo.relativeTo










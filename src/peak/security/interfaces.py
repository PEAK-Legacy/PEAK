from peak.api import NOT_GIVEN, protocols
from protocols import Interface, Attribute
from peak.util.imports import whenImported
from types import FunctionType

__all__ = [
    'IAuthorizedPrincipal', 'IInteraction', 'IAccessAttempt',
    'IAbstractPermission', 'IAbstractPermission', 'IPermissionChecker',
    'IGuardedObject', 'IGuardedClass', 'IGuardedDescriptor',
]

class IAccessAttempt(Interface):

    """An attempt to access a protected object"""

    user = Attribute("""Application user object""")

    principal = Attribute("""IAuthorizedPrincipal for the attempt""")

    interaction = Attribute("""IInteraction for the attempt""")

    permission = Attribute(
        """Concrete permission type to be checked"""
    )

    subject = Attribute("""The object to which access is desired""")

    def allows(subject=NOT_GIVEN, name=NOT_GIVEN, permissionNeeded=NOT_GIVEN,
        user=NOT_GIVEN
    ):
        """True if 'user' has 'permissionNeeded' for 'subject', or Denial()"""










class IAuthorizedPrincipal(Interface):

    def checkGlobalPermission(attempt):
        """Does principal have a global grant or deny of 'attempt.permission'?

        Return NOT_FOUND if there is no knowledge of a global grant or denial
        of 'permType'.  Otherwise return truth to grant permission, or
        a false value to deny it.

        Note that principals are not responsible for local grants/denials."""


class IInteraction(Interface):

    """Component representing a security-controlled user/app interaction"""

    user = Attribute("""The IPrincipal responsible for the interaction""")

    permissionProtocol = Attribute(
        """The protocol to which permissions should be adapted for checking"""
    )

    def allows(subject,name=None,permissionNeeded=NOT_GIVEN,user=NOT_GIVEN):
        """Return true if 'user' has 'permissionNeeded' for 'subject'

        If 'user' is not supplied, the interaction's user should be used.  If
        the permission is not supplied, 'subject' should be adapted to
        'IGuardedObject' in order to obtain the required permission.

        Note that if 'subject' does not support 'IGuardedObject', and the
        required permission is not specified, then this method should always
        return true when the 'name' is 'None', and false otherwise.  That is,
        an unguarded object is accessible, but none of its attributes are.
        (This is so that value objects such as numbers and strings don't need
        permissions.)

        This method should return a true value, or a 'security.Denial()' with
        an appropriate 'message' value."""



class IPermissionChecker(Interface):

    """An object that can verify the presence of a permission"""

    def checkPermission(attempt):
        """Does the principal for 'attempt' have permission 'permType'?

        This method may return any false value to indicate failure, but
        returning a 'security.Denial()' is preferred."""


class IConcretePermission(Interface):

    def getAbstract():
        """Return an IAbstractPermission for this permission"""

    def addRule(rule,protocol=IPermissionChecker):
        """Declare 'rule' an adapter factory from permission to 'protocol'"""

    __mro__ = Attribute(
        """Sequence of this type's supertypes, itself included, in MRO order"""
    )

    def defaultDenial():
        """Return a default security.Denial() to be used when a check fails"""


class IAbstractPermission(IConcretePermission):

    def of(protectedObjectType):
        """Return a subclass IConcretePermission for 'protectedObjectType'"""










class IGuardedObject(Interface):

    """Object that knows permissions needed to access subobjects by name"""

    def getPermissionForName(name):
        """Return (abstract) permission needed to access 'name', or 'None'"""


class IGuardedClass(Interface):

    """Class that can accept permission declarations for its attributes"""

    def declarePermissions(objectPerm=None, **namePerms):
        """Declare permissions for named attributes"""

    def getAttributePermission(name):
        """Return (abstract) permission needed to access 'name', or 'None'"""


class IGuardedDescriptor(Interface):

    """Descriptor that knows the permission required to access it"""

    permissionNeeded = Attribute(
        "Sequence of abstract permissions needed, or 'None' to keep default"
    )















whenImported(
    'peak.binding.once',
    lambda once:
        protocols.declareAdapter(
            protocols.NO_ADAPTER_NEEDED,
            provides = [IGuardedDescriptor],
            forTypes = [once.Descriptor, once.Attribute]
        )
)

whenImported(
    'peak.model.features',
    lambda features:
        protocols.declareAdapter(
            protocols.NO_ADAPTER_NEEDED,
            provides = [IGuardedDescriptor],
            forTypes = [features.FeatureClass]
        )
)

protocols.declareAdapter(
    # Functions can be guarded descriptors if they define 'permissionsNeeded'
    lambda o,p: (getattr(o,'permissionNeeded',None) is not None) and o or None,
    provides = [IGuardedDescriptor],
    forTypes = [FunctionType]
)
















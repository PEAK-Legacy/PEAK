from peak.api import NOT_GIVEN
from protocols import Interface, Attribute

__all__ = [
    'IAuthorizedPrincipal', 'IInteraction', 'IAccessAttempt',
    'IPermissionType', 'IPermissionChecker', 'IGuardedObject',
]

class IAccessAttempt(Interface):

    """An attempt to access a protected object"""

    user = Attribute("""Application user object""")

    principal = Attribute("""IAuthorizedPrincipal for the attempt""")

    interaction = Attribute("""IInteraction for the attempt""")

    permissionsNeeded = Attribute(
        """Sequence of concrete permission types; if any one is allowed,
        the access is allowed."""
    )

    subject = Attribute("""The object to which access is desired""")

    def isAllowed():
        """Return true if access should be allowed"""














class IAuthorizedPrincipal(Interface):

    def checkGlobalPermission(permType, attempt):
        """Does principal have a global grant or deny of 'permType'?

        Return NOT_FOUND if there is no knowledge of a global grant or denial
        of 'permType'.  Otherwise return truth to grant permission, or
        a false value to deny it.

        Note that principals are not responsible for local grants/denials."""
        



class IInteraction(Interface):

    """Component representing a security-controlled user/app interaction"""

    user = Attribute("""The IPrincipal responsible for the interaction""")
    
    def checkAccess(attempt):
        """Return true if 'IAccessAttempt' 'attempt' should be allowed"""

    permissionProtocol = Attribute(
        """The protocol to which permissions should be adapted for checking"""
    )

    def allows(subject, permissionsNeeded=NOT_GIVEN, user=NOT_GIVEN):
        """Return true if 'user' has 'permisisonsNeeded' for 'subject'

        If 'user' is not supplied, the interaction's user should be used.  If
        the permissions are not supplied, 'subject' should be adapted to
        'IGuardedObject' in order to obtain the required permissions."""
        







class IPermissionChecker(Interface):

    """An object that can verify the presence of a permission"""

    def checkPermission(permType, attempt):
        """Does the principal for 'attempt' have permission 'permType'?"""


class IPermissionType(Interface):

    def of(protectedObjectType):
        """Return a subclass IPermissionType for 'protectedObjectType'"""

    def addRule(rule,protocol=IPermissionChecker):
        """Declare 'rule' an adapter factory from permission to 'protocol'"""

    __mro__ = Attribute(
        """Sequence of this type's supertypes, itself included, in MRO order"""
    )


class IGuardedObject(Interface):

    """An object that knows what permissions are needed for access"""

    def getRequiredPermissions(attempt):
        """Return (abstract) permission types needed for 'attempt'"""


    

"""Permissions, Rules, and Interactions"""

from peak.api import *
from interfaces import *

from weakref import WeakKeyDictionary

__all__ = [
    'AccessAttempt', 'PermissionType', 'Permission', 'RuleSet',
    'Anybody', 'Nobody', 'Interaction',
]






























class AccessAttempt(object):

    """An attempt to access a protected object"""

    __slots__ = [
        'interaction', 'user', 'subject', 'permissionsNeeded', 'principal',
    ]
    
    def __init__(self,
        subject, interaction=NOT_GIVEN, user=NOT_GIVEN, 
        permissionsNeeded=NOT_GIVEN
    ):

        self.subject = subject
        interaction = adapt(interaction,IInteraction,None)

        if interaction is None:
            if user is not NOT_GIVEN:
                interaction = Interaction(user, user=user)
            else:
                interaction = Interaction()

        self.interaction = interaction

        if user is NOT_GIVEN:
            if interaction is not None:
                user = interaction.user
            else:
                user = None

        self.user = user
        self.principal = adapt(user, IAuthorizedPrincipal, None)

        if permissionsNeeded is NOT_GIVEN:
            subject = adapt(subject,IGuardedObject,None)
            if subject is not None:
                permissionsNeeded = subject.getRequiredPermissions(self)
            else:
                permissionsNeeded = ()


        # Set up permissions to be of the right subtype for their subject
        
        try:
            klass = subject.__class__
        except AttributeError:
            klass = type(subject)

        self.permissionsNeeded = [p.of(klass) for p in permissionsNeeded]


    def isAllowed(self):
        """Return true if access permitted"""
        return self.interaction.checkAccess(self)
                        



























class Interaction(binding.Component):

    """Context for an access-controlled interaction (abstract base)"""

    protocols.advise(
        instancesProvide = [IInteraction]
    )

    user = binding.requireBinding(
        "The principal responsible for this interaction"
    )

    accessType         = AccessAttempt
    permissionProtocol = IPermissionChecker     # XXX


    def checkAccess(self, attempt):

        protocol = self.permissionProtocol

        for permType in attempt.permissionsNeeded:
            ok = adapt(permType, protocol).checkPermission(permType, attempt)
            if ok:
                return ok

        return False

    def allows(self, subject, permissionsNeeded=NOT_GIVEN, user=NOT_GIVEN):
        return self.checkAccess(
            self.accessType(subject, self, user, permissionsNeeded)
        )






        



class PermissionType(binding.ActiveClass):

    """A permission type"""

    protocols.advise(
        instancesProvide = [IPermissionType]
    )

    __cache = binding.New(WeakKeyDictionary, attrName='_PermissionType__cache')

    def of(self,protectedObjectType):
        try:
            return self.__cache[protectedObjectType]
        except KeyError:
            pass

        bases = protectedObjectType.__bases__
        if not bases:
            bases = self,
        else:
            bases = tuple([self.of(b) for b in bases])

        subtype = self.__class__(
            self.__name__, bases, {}
        )

        self.__cache[protectedObjectType] = subtype
        return subtype

    def addRule(self, rule, protocol=IPermissionChecker):
        protocols.declareAdapter(
            rule, provides=[protocol], forObjects=[self]
        )


class Permission:
    """Base class for permissions"""
    __metaclass__ = PermissionType



class RuleSet(binding.Singleton):

    def checkPermission(klass, permissionType, attempt):

        if attempt.principal is not None:

            check = attempt.principal.checkGlobalPermission(
                permissionType, attempt
            )

            if check is not NOT_FOUND:
                return check

        # Lookup the right method to call

        reg = klass.__methodNames

        for key in permissionType.__mro__:
            if key in reg:
                return getattr(klass,reg[key])(permissionType, attempt)

        raise NotImplementedError(
            "No rule method found", permissionType
        )


    def asAdapter(klass, permType, protocol):
        return klass


    def declareRulesFor(klass, protocol):
        factory = klass.asAdapter
        for permType in klass.__methodNames:
            permType.addRule(factory, protocol)

                





    def __methodNames(klass,d,a):

        newMethods = {}

        for k,v in klass.rules:

            for permType in v:

                if permType not in newMethods:
                    newMethods[permType] = k
                    continue

                raise TypeError(
                    "Permission checked by two methods in class:",
                    permType, newMethods[permType], k
                )

        methodNames = {}
        for reg in binding.getInheritedRegistries(
            klass,'_RuleSet__methodNames'
        ):
            methodNames.update(reg)

        methodNames.update(newMethods)
        return methodNames

    __methodNames = binding.Once(__methodNames)














class Anybody(Permission):

    """Allow anybody access"""


class Nobody(Permission):

    """Deny everyone access"""


class Universals(RuleSet):

    rules = Items(
        allowAnybody = [Anybody],
        denyEverybody = [Nobody],
    )
    
    def allowAnybody(klass, permType, attempt):
        return True

    def denyEverybody(klass, permType, attempt):
        return False

Universals.declareRulesFor(IPermissionChecker)


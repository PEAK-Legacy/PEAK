"""Permissions, Rules, and Interactions"""

from peak.api import *
from interfaces import *

from weakref import WeakKeyDictionary
from protocols.advice import getFrameInfo, addClassAdvisor

__all__ = [
    'AccessAttempt', 'PermissionType', 'Permission', 'RuleSet',
    'Anybody', 'Nobody', 'Interaction', 'allow'
]





























class NamePermissionsAdapter(object):
    __slots__ = 'perms'

    protocols.advise(
        instancesProvide = [INamePermissions]
    )

    def __init__(self,ob,proto):
        self.perms = ob.__class__._peak_nameToPermissions_map

    def getPermissionsForName(self,name):
        return self.perms.get(name,())


def allow(**namesToPermLists):

    """Use in the body of a class to declare permissions for attributes"""

    def callback(klass):

        if '_peak_nameToPermissions_map' not in klass.__dict__:
            m = klass._peak_nameToPermissions_map = {}
            map(m.update,
                binding.getInheritedRegistries(
                    klass,'_peak_nameToPermissions_map'
                )
            )
        else:
            # XXX check accidental overrides??
            m = klass._peak_nameToPermissions_map

        m.update(namesToPermLists)

        protocols.declareAdapter(
            NamePermissionsAdapter, provides = [INamePermissions],
            forTypes = [klass],
        )
        return klass

    addClassAdvisor(callback)

class AccessAttempt(object):

    """An attempt to access a protected object"""

    __slots__ = [
        'interaction', 'user', 'subject', 'permissionsNeeded',
        'originalPermissions', 'principal', 'name',
    ]

    def __init__(self,
        subject, interaction=NOT_GIVEN, user=NOT_GIVEN,
        permissionsNeeded=NOT_GIVEN, name=None,
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
        self.name = name







        if permissionsNeeded is NOT_GIVEN:

            if name is None:

                subject = adapt(subject,IGuardedObject,None)

                if subject is not None:
                    permissionsNeeded = subject.getRequiredPermissions(self)
                else:
                    permissionsNeeded = ()

            else:
                subject = adapt(subject,INamePermissions,None)

                if subject is not None:
                    permissionsNeeded = subject.getPermissionsForName(name)
                else:
                    permissionsNeeded = ()

        # Set up permissions to be of the right subtype for their subject

        self.originalPermissions = permissionsNeeded

        try:
            klass = self.subject.__class__
        except AttributeError:
            klass = type(self.subject)

        self.permissionsNeeded = [p.of(klass) for p in permissionsNeeded]


    def isAllowed(self):
        """Return true if access permitted"""
        return self.interaction.checkAccess(self)







    def new(self, subject=NOT_GIVEN, interaction=NOT_GIVEN, user=NOT_GIVEN,
        permissionsNeeded=NOT_GIVEN, name=NOT_GIVEN
    ):
        if subject is NOT_GIVEN:
            subject=self.subject
        if interaction is NOT_GIVEN:
            interaction=self.interaction
        if user is NOT_GIVEN:
            user=self.user
        if name is NOT_GIVEN:
            name=self.name
        if permissionsNeeded is NOT_GIVEN:
            permissionsNeeded=self.originalPermissions

        return self.__class__(subject,interaction,user,permissionsNeeded,name)


























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

    def allows(self, subject,
        name=NOT_GIVEN, permissionsNeeded=NOT_GIVEN, user=NOT_GIVEN
    ):
        return self.checkAccess(
            self.accessType(subject, self, user, permissionsNeeded, name)
        )








class PermissionType(binding.ActiveClass):

    """A permission type (abstract and/or concrete)"""

    protocols.advise(
        instancesProvide = [IAbstractPermission]
    )

    abstractBase = None

    __cache = binding.New(WeakKeyDictionary, attrName='_PermissionType__cache')

    def of(self,protectedObjectType):
        if self.abstractBase is not None:
            return self.abstractBase.of(protectedObjectType)

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
            '%s_of_%s' % (self.__name__,protectedObjectType.__name__),
            bases, {'__module__': self.__module__, 'abstractBase': self}
        )

        self.__cache[protectedObjectType] = subtype
        return subtype


    def addRule(self, rule, protocol=IPermissionChecker):
        protocols.declareAdapter(
            rule, provides=[protocol], forObjects=[self]
        )

    def getAbstract(self):
        if self.abstractBase is None:
            return self
        else:
            return self.abstractBase



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

        # XXX check completeness/correctness of coverage?

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


















"""Permission tests

TODO

 - Simple permission checks

 - Delegated permission

 - Varying algorithm by subject class

 - Global permission grant overrides local

"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

class ITestPermissionChecker(protocols.Interface):

    """Permission protocol for the tests"""

    protocols.advise(
        protocolIsSubsetOf = [security.IPermissionChecker]
    )


class ManageAsset(security.Permission): pass
class ManageBatch(security.Permission): pass

class Worker(security.Permission): pass
class Manager(security.Permission): pass
class Shipper(security.Permission): pass
class Receiver(security.Permission): pass







class SimpleTests(TestCase):

    def setUp(self):
        self.interaction = security.Interaction(
            user=None, permissionProtocol = ITestPermissionChecker
        )

    def checkUniversals(self):
        assert self.interaction.allows(None, [security.Anybody])
        assert not self.interaction.allows(None, [security.Nobody])


TestClasses = (
    SimpleTests,
)


def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])

































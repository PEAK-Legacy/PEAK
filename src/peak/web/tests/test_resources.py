from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

from test_templates import TestApp, BasicTest

class ResourceApp(TestApp):

    # This makes all 'peak.*' package resources available for testing;
    # Ordinarily, you'd do this via a config file, but this is quick and easy

    __makePkgAvailable = binding.Constant(True,
        offerAs = ['peak.web.resource_packages.peak.*']
    )

    show = web.bindResource('template1')


class MethodTest(BasicTest):

    def setUp(self):
        r = testRoot()
        self.interaction = web.TestInteraction(ResourceApp(r))

TestClasses = (
    MethodTest,
)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])

"""Unit tests for relational algebra"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from peak.query.api import *

TestClasses = (
    # XXX
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))
    return TestSuite(s)


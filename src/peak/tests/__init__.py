"""
PEAK master test suite package.  Use with unittest.py to run all tests,
or use the 'test_suite()' function in an individual module to get just those
tests.
"""

allSuites = [
    'peak.api.tests:test_suite',
    'peak.binding.tests:test_suite',
    'peak.metamodels.tests:test_suite',
    'peak.util.tests:test_suite',
]

def test_suite():

    from unittest import TestSuite
    from peak.binding.imports import importSequence

    return TestSuite(
        [t() for t in importSequence(allSuites,globals())]
    )


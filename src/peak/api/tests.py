"""PEAK API test suite package.  This only tests packages with an active
and current test suite.
"""

allSuites = [
    'peak.binding.tests:test_suite',
    'peak.config.tests:test_suite',
]

def test_suite():

    from unittest import TestSuite
    from peak.binding.imports import importSequence

    return TestSuite(
        [t() for t in importSequence(allSuites,globals())]
    )


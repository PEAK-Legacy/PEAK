"""
PEAK utility modules test suite package.  Use with unittest.py to run all
tests, or use the 'test_suite()' function in an individual module to get just
those tests.
"""

allSuites = [
    'SOX:test_suite',
    'EigenData:test_suite',
    'uuid:test_suite',
]

def test_suite():

    from unittest import TestSuite
    from peak.binding.imports import importSequence

    return TestSuite(
        [t() for t in importSequence(allSuites, globals())]
    )


"""
Service-Element-Feature test suite package.  Use with unittest.py to run all
tests, or use the 'test_suite()' function in an individual module to get just
those tests.
"""

allSuites = [
    'TW.SEF.tests.General:test_suite',
]

def test_suite():

    from unittest import TestSuite
    from TW.Utils.Import import importString

    return TestSuite(
        [importString(t)() for t in allSuites]
    )


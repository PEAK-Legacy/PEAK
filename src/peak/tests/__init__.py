"""PEAK master test suite package.

Use with unittest.py to run all tests, or use the 'test_suite()' function
in an individual module to get just those tests."""


allSuites = [
    'peak.api.tests:test_suite',
    'peak.metamodels.tests:test_suite',
    'peak.util.tests:test_suite',
]


def test_suite():
    from peak.util.imports import importSuite
    return importSuite(allSuites)


# config.Application for testing
_app = None

def testApp():

    global _app

    if _app is None:
        from peak.api import config
        _app = config.Application()

    return _app

"""PEAK API test suite package.

    This only tests packages with an active and current test suite.
"""

allSuites = [
    'peak.naming.tests:test_suite',
    'peak.binding.tests:test_suite',
    'peak.config.tests:test_suite',
    'peak.storage.tests:test_suite',
]


def test_suite():
    from peak.util.imports import importSuite
    return importSuite(allSuites)


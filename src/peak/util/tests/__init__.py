"""PEAK utility modules test suite package

Use with unittest.py to run all tests, or use the 'test_suite()' function in
an individual module to get just those tests."""


allSuites = [
    'EigenData:test_suite',
    'FileParsing:test_suite',
    'SOX:test_suite',
    'uuid:test_suite',
]


def test_suite():
    from peak.util.imports import importSuite
    return importSuite(allSuites, globals())


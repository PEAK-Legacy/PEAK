"""
TransWarp master test suite package.  Use with unittest.py to run all
tests, or use the suite() function in an individual module to run just
those tests.
"""

def suite():

    from unittest import TestSuite
    s = []
    
    import Aspects, SOX
    
    for t in Aspects, SOX:
        s.append(t.suite())

    return TestSuite(s)


"""
TransWarp master test suite package.  Use with unittest.py to run all
tests, or use the suite() function in an individual module to run just
those tests.
"""

def suite():

    from unittest import TestSuite
    s = []
    
    import Components, Callbacks, SOX, StructuralModel
    
    for t in Components, Callbacks, SOX, StructuralModel:
        s.append(t.suite())

    return TestSuite(s)


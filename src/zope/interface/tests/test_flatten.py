##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test flattenInterfaces 

$Id: test_flatten.py,v 1.1 2003/01/07 12:14:56 pje Exp $
"""
from unittest import TestCase, TestSuite, makeSuite
from zope.interface import Interface
from zope.interface.implements import flattenInterfaces

class I1(Interface):
    pass

class I2(Interface):
    pass

class I3(Interface):
    pass

class I4(Interface):
    pass

class I5(I1, I2):
    pass

class I6(I3, I4):
    pass

class I7(I2, I3):
    pass


class TestFlattenInterface(TestCase):

    def testSingleInterface(self):
        self.assertEqual(flattenInterfaces(I1), [I1, Interface])
        self.assertEqual(flattenInterfaces(I2), [I2, Interface])
        self.assertEqual(flattenInterfaces(I3), [I3, Interface])
        self.assertEqual(flattenInterfaces(I4), [I4, Interface])

    def testSimpleTuple(self):
        flat = list(flattenInterfaces((I1, I2, I3)))
        flat.sort()
        res = [I1, I2, I3, Interface]
        res.sort()
        self.assertEqual(flat, res)
        flat = list(flattenInterfaces((I3, I1, I2)))
        flat.sort()
        self.assertEqual(flat, res)
    
    def testNestedTuple(self):
        flat = list(flattenInterfaces((I1, I2, I6)))
        flat.sort()
        self.assertEqual(flat, [I1, I2, I3, I4, I6, Interface])
        flat = list(flattenInterfaces((I1, I7)))
        flat.sort()
        self.assertEqual(flat, [I1, I2, I3, I7, Interface])

    def testRemoveDuplicates(self):
        flat = list(flattenInterfaces((I1, I2, I5)))
        flat.sort()
        self.assertEqual(flat, [I1, I2, I5, Interface])
        flat = list(flattenInterfaces((I5, I6, I7)))
        flat.sort()
        self.assertEqual(flat, [I1, I2, I3, I4, I5, I6, I7, Interface])

    def testNotRemoveDuplicates(self):
        flat = list(flattenInterfaces((I1, I2, I5), False))
        flat.sort()
        self.assertEqual(flat, [I1, I1, I2, I2, I5, Interface,
                                Interface, Interface, Interface])
        

def test_suite():
    return TestSuite((
        makeSuite(TestFlattenInterface),
        ))

"""Tests for EigenData"""

from unittest import TestCase, makeSuite, TestSuite
from peak.util.EigenData import *


class CheckEmpty(TestCase):

    emptyCell = CollapsedCell
    
    def checkExistence(self):

        cell = self.emptyCell

        assert not cell.exists()
        cell.unset()

        try:
            cell.get()
        except AttributeError:
            pass
        else:
            raise AssertionError("Empty cell should not have value")


class CheckEmpty2(CheckEmpty):

    emptyCell = EigenCell()


class CheckUnset(CheckEmpty):

    def setUp(self):
        self.emptyCell = cell = EigenCell()
        for i in range(5):
            cell.set(i)
        cell.unset()




class CheckFull(TestCase):

    def setUp(self):
        self.cell = EigenCell()

    def checkSet(self):
        cell = self.cell
        for i in range(50):
            cell.set(i)

    def checkGet(self):
        cell = self.cell

        for i in range(10):
            cell.set(i)

        assert cell.get()==9
        assert cell.exists()

        try:
            cell.set(10)
        except AlreadyRead:
            pass
        else:
            raise AssertionError("Should not be able to set read cell")
















dictData = { 'a':1, 'b':2, 'c':3 }
multData = { 'a':9, 'b':18, 'c': 27 }

class CheckDict(TestCase):

    def setUp(self):
        self.ed = ed = EigenDict()

        for i in range(10):
            for k,v in dictData.items():
                ed[k]=v*i

    def checkCopyAndClear(self):

        assert self.ed.copy() == multData

        try:
            self.ed.clear()
        except AlreadyRead:
            pass
        else:
            raise AssertionError("Shouldn't be able to clear copy'd EigenDict")


    def checkClearUnlocked(self):
        # should work, because no cells have been read
        self.ed.clear()


    def checkDelAfterContains(self):
        assert 'a' in self.ed
        del self.ed['b']
        del self.ed['b']

        try:
            del self.ed['a']
        except AlreadyRead:
            pass
        else:
            raise AssertionError("Shouldn't be able to delete read key")

from Interface import Interface

#   IA
#    |
#   IB
#   /\
# IC  ID


class IA(Interface): pass
class IB(IA): pass
class IC(IB): pass
class ID(IB): pass


class PA(object): __implements__ = IA
class PB(object): __implements__ = IB
class PC(object): __implements__ = IC
class PD(object): __implements__ = ID
class PE(object): __implements__ = IC, ID


pA = PA()
pB = PB()
pC = PC()
pD = PD()
pE = PE()


class RegistryBase(TestCase):

    obs = pA, pB, pC, pD, pE
    
    def setUp(self):

        reg = self.reg = EigenRegistry()

        for ob in self.obs:
            reg.register(ob.__implements__, ob)


class RegForward(RegistryBase):

    def checkSimple(self):

        reg = self.reg

        assert reg[IA] is pA
        assert reg[IB] is pB
        assert reg[IC] is pC
        assert reg[ID] is pD


class RegBackward(RegForward):
    obs = pD, pC, pE, pB, pA


class RegMixed(RegForward):
    obs = pD, pB, pA, pC, pE


class RegUpdate(TestCase):

    def checkUpdate(self):

        reg1 = EigenRegistry()
        reg2 = EigenRegistry()

        reg1.register(IA,pA)
        reg2.register(IB,pB)

        assert reg1[IA] is pA
        assert reg2[IA] is pB

        reg1.update(reg2)

        assert reg1[IA] is pA
        assert reg1[IB] is pB




TestClasses = (
    CheckEmpty, CheckEmpty2, CheckUnset, CheckFull, CheckDict,
    RegForward, RegBackward, RegUpdate
)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])


"""Relational Algebra"""

from peak.api import *
from peak.util.hashcmp import HashAndCompare
import interfaces
from interfaces import *

__all__ = ['And', 'Or',]

class _expr:

    protocols.advise(
        instancesProvide = [IBooleanExpression],
    )

    def conjuncts(self):
        return [self]

    def disjuncts(self):
        return [self]

    def __invert__(self):
        return Not(self)

    def __and__(self,other):
        return And(self,other)

    def __or__(self,other):
        return Or(self,other)












class _compound(_expr,HashAndCompare):

    def __init__(self,*args):
        operands = []
        for op in args:
            operands.extend(self._getPromotable(op))
        operands.sort()
        self.operands = tuple(operands)
        self._hashAndCompare = self.__class__.__name__, self.operands

    def __repr__(self):
        return '%s%r' % self._hashAndCompare





























class And(_compound):

    def _getPromotable(self,op):
        return adapt(op,IBooleanExpression).conjuncts()

    def conjuncts(self):
        return self.operands

    def __invert__(self):
        return Or(*tuple([~op for op in self.operands]))


class Or(_compound):

    def _getPromotable(self,op):
        return adapt(op,IBooleanExpression).disjuncts()

    def disjuncts(self):
        return self.operands

    def __invert__(self):
        return And(*tuple([~op for op in self.operands]))


class Not(_compound):

    def _getPromotable(self,op):
        return [op]

    def __invert__(self):
        return self.operands[0]










class ExpressionWrapper(protocols.Adapter, _expr, HashAndCompare):

    protocols.advise(
        instancesProvide = [IBooleanExpression],
        asAdapterForTypes = [object],
    )

    def __init__(self,subject,protocol):
        self.subject = self._hashAndCompare = subject

    def __repr__(self):
        return `self.subject`






























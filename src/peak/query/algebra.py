"""Relational Algebra"""

from peak.api import *
from peak.util.hashcmp import HashAndCompare
import interfaces
from interfaces import *
from kjbuckets import kjSet, kjGraph

__all__ = []

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
        if self==other or other is None:
            return self
        return And(self,other)

    def __or__(self,other):
        if self==other or other is None:
            return self
        return Or(self,other)







class PhysicalDB(binding.Component):

    tables = binding.Make(list)

    tableMap = binding.Make(
        lambda self: dict(
            [(name,Table(name,cols,self)) for (name,cols) in self.tables]
        )
    )

    def table(self,name):
        return self.tableMap[name]


def getColumns(base,relvars):
    cols = kjGraph(base)
    for rv in relvars:
        cols += rv.attributes()
    return cols #tuple(cols)






















class Table:

    protocols.advise(
        instancesProvide = [IRelationVariable],
    )
    condition = None
    outers = ()

    def __init__(self,name,columns,db=None):
        self.name = name
        self.columns = kjGraph(zip(columns,range(len(columns))))
        self.db = db

    def attributes(self):
        return self.columns

    def thetaJoin(self,condition,*relvars):
        return BasicJoin(
            condition & self.condition, (self,)+relvars, (),
            getColumns(self.columns,relvars)
        )

    def starJoin(self,condition,*relvars):
        return BasicJoin(
            condition & self.condition, (self,), relvars,
            getColumns(self.columns,relvars)
        )

    select = thetaJoin      # XXX

    def __repr__(self):
        return self.name

    def project(self,columns):
        return BasicJoin(self.condition, (self,), (), kjSet(columns)*self.columns)

    def getDB(self):
        return self.db



class BasicJoin(Table, HashAndCompare):

    def __init__(self,condition,relvars,outers=(),columns=()):
        myrels = []; outers=list(outers)
        for rv in relvars:
            if isinstance(rv,self.__class__):   # XXX
                myrels.extend(rv.relvars)
                outers.extend(rv.outers)
                condition = condition & rv.condition
            else:
                myrels.append(rv)
        myrels.sort()
        if len(myrels)<1:
            raise TypeError(
                "%s requires at least %s relvar(s)" %
                (self.__class__.__name__, self.minRV)
            )
        self.relvars = tuple(myrels)
        outers.sort()
        self.outers = tuple(outers)
        self.condition = condition
        self.columns = kjGraph(columns)
        self._hashAndCompare = (
            self.__class__.__name__, condition, self.relvars, self.outers, self.columns
        )

    def __repr__(self):
        parms=(
            self.condition, list(self.relvars), list(self.outers),
            list(self.columns.items())
        )
        return '%s%r' % (self._hashAndCompare[0], parms)

    def getDB(self):
        db = self.relvars[0].getDB()
        for rv in self.relvars[1:]:
            if rv.getDB() is not db:
                return None
        return db


class _compound(_expr,HashAndCompare):

    def __init__(self,*args):

        operands = {}

        for op in args:
            for item in self._getPromotable(op):
                operands[item]=1

        operands = list(operands)
        operands.sort()
        self.operands = tuple(operands)

        if len(operands)<2:
            raise TypeError,"Compounds require more than one operand"

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

    def __init__(self,operand):
        self.operands = operand,
        self._hashAndCompare = self.__class__.__name__, self.operands

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






























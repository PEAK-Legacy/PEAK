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
        if self==other or other is EMPTY:
            return self
        return And(self,other)

    def __or__(self,other):
        if self==other or other is EMPTY:
            return self
        return Or(self,other)







class EMPTY(binding.Singleton):

    protocols.advise(
        classProvides = [IBooleanExpression],
    )

    def conjuncts(self):
        return ()

    def disjuncts(self):
        return ()

    def __invert__(self):
        return self

    def __and__(self,other):
        return other

    def __or__(self,other):
        return other

    def simpleSQL(self,driver):
        return ''


class PhysicalDB(binding.Component):

    tables = binding.Make(list)

    tableMap = binding.Make(
        lambda self: dict(self.tables)
    )

    def __getitem__(self,name):
        return Table(name,self.tableMap[name],self)






class SQLDriver:

    def __init__(self,query):
        d = {}; ct=1
        rvs = [(rv.asFromClause(),rv) for rv in query.getInnerRVs()]  # XXX outer, nested
        rvs.sort()
        for name,rv in rvs:
            if name[0].isalpha():
                ltr = name[0].upper()
            else:
                ltr="x"
            d[rv] = "%s%d" % (ltr,ct)
            ct+=1
        self.aliases = d

    def getAlias(self,RV):
        return self.aliases[RV]

    def getFromDef(self,RV):
        # XXX should handle RV being non-table
        return "%s AS %s" % (RV.asFromClause(),self.getAlias(RV))

    def sqlize(self,arg):
        v = adapt(arg,IDomainVariable,None)

        if v is not None:
            return v.simpleSQL(self)

        return `arg`












class AbstractRV(object):

    protocols.advise(
        instancesProvide = [IRelationVariable]
    )

    condition = EMPTY
    outers = ()

    def __call__(self,
        where=None,join=(),outer=(),rename=(),keep=None,calc=(),groupBy=()
    ):
        cols = kjGraph(self.columns)
        rename = ~kjGraph(rename)
        groupBy = kjSet(groupBy)

        for rv in tuple(join)+tuple(outer):
            cols = cols + rv.attributes()

        if keep:
            kjSet(~(rename * groupBy))
            cols = (kjSet(keep)+kjSet(~rename)+groupBy) * cols

        if rename:
            cols = rename * cols + (cols-cols.restrict(~rename))

        if where is None:
            where = EMPTY

        rv = BasicJoin(
            self.condition & where, (self,)+tuple(join), tuple(outer),
            cols+kjGraph(calc)
        )

        if groupBy:
            return GroupBy(rv, groupBy.items())
        return rv

    def attributes(self):
        return self.columns

    def getInnerRVs(self):
        return (self,)

    def getOuterRVs(self):
        return self.outers

    def getCondition(self):
        return self.condition

    def getReferencedRVs(self):
        all = kjSet([self])
        for rv in self.getInnerRVs()+self.getOuterRVs():
            if not all.has_key(rv):
                all += kjSet(rv.getReferencedRVs())
        return all.items()

    def __getitem__(self,key):
        return self.columns[key]

    def keys(self):
        return self.columns.keys()




















class Table(AbstractRV):

    def __init__(self,name,columns,db=None):
        self.name = name
        self.columns = kjGraph([(c,Column(c,self)) for c in columns])
        self.db = db

    def __repr__(self):
        return self.name

    def getDB(self):
        return self.db

    def simpleSQL(self,driver=None):
        return "SELECT * FROM %s" % self.name

    def asFromClause(self):
        return self.name























class GroupBy(AbstractRV):

    def __init__(self,rv,groupBy,cond=EMPTY):
        self.condition = cond
        groupBy = list(groupBy); groupBy.sort()
        self.rv = rv
        self.groupBy = groupBy
        self.columns = kjGraph([(c,Column(c,self)) for c in rv.keys()])
        for k in rv.keys():
            if k not in groupBy and not rv[k].isAggregate():
                raise TypeError("Non-aggregate column in groupBy",k,rv[k])

    def getDB(self):
        return self.rv.getDB()

    def simpleSQL(self,driver=None):
        if driver is None:
            driver = SQLDriver(self.rv)
        groupBys = [self.rv[col].simpleSQL(driver) for col in self.groupBy]
        sql = self.rv.simpleSQL(driver) + " GROUP BY "+ ", ".join(groupBys)

        condSQL = self.condition.simpleSQL(driver)
        if condSQL:
            sql += " HAVING " + condSQL

        return sql

    def __call__(self, where=None,**kw):
        if kw:
            kw['where']=where
            return super(GroupBy,self).__call__(**kw)
        if where is not None:
            return GroupBy(self.rv,self.groupBy,self.condition&where)
        return self

    def asFromClause(self):
        return "(%s)" % self.simpleSQL()




class AbstractDV:

    protocols.advise(
        instancesProvide = [IDomainVariable]
    )

    _agg = False

    def eq(self,dv):
        return Cmp(self,'=',dv)

    def ne(self,dv):
        return Cmp(self,'<>',dv)

    def lt(self,dv):
        return Cmp(self,'<',dv)

    def ge(self,dv):
        return Cmp(self,'>=',dv)

    def gt(self,dv):
        return Cmp(self,'>',dv)

    def le(self,dv):
        return Cmp(self,'<=',dv)

    def isAggregate(self):
        return self._agg













class Column(AbstractDV):

    protocols.advise(
        instancesProvide = [IRelationAttribute]
    )

    def __init__(self,name,table):
        self.name, self.table = name, table

    def getRV(self):
        return self.table

    def getDB(self):
        return self.table.getDB()

    def simpleSQL(self,driver):
        return driver.getAlias(self.table)+'.'+self.name
























class Func(AbstractDV):

    isAggFunc = False

    def __init__(self,name,*args):

        self.fname = name
        self.args = args
        agg = None

        for arg in args:
            arg = adapt(arg,IDomainVariable,None)
            if arg is not None:
                if agg is None:
                    agg = arg.isAggregate()
                elif agg<>arg.isAggregate():
                    raise TypeError(
                        "Mixed aggregate/non-aggregate arguments",args
                    )

        if agg and self.isAggFunc:
            raise TypeError("Can't aggregate an aggregate",args)

        self._agg = agg or self.isAggFunc


    def simpleSQL(self,driver):
        return "%s(%s)" % (
            self.fname, ",".join([driver.sqlize(arg) for arg in self.args])
        )

class Aggregate(Func):
    isAggFunc = True

def function(name):
    return lambda *args: Func(name,*args)

def aggregate(name):
    return lambda *args: Aggregate(name,*args)


class BasicJoin(Table, HashAndCompare):

    def __init__(self,condition,relvars,outers=(),columns=()):
        myrels = []
        outers=list(outers)
        relUsage = {}

        for rv in relvars:
            myrels.extend(rv.getInnerRVs())
            outers.extend(rv.getOuterRVs())
            condition = condition & rv.getCondition()

        for rv in myrels+outers:
            for r in rv.getReferencedRVs():
                relUsage[r] = relUsage.setdefault(r,0)+1

        if len(myrels)<1:
            raise TypeError("BasicJoin requires at least 1 relvar")

        for k,v in relUsage.items():
            if v>1:
                raise ValueError("Relvar used more than once",k)

        myrels.sort()
        outers.sort()
        self.relvars = tuple(myrels)
        self.outers = tuple(outers)
        self.condition = condition
        self.columns = kjGraph(columns)

        self._hashAndCompare = (
            self.__class__.__name__, condition,
            self.relvars, self.outers, self.columns
        )







    def __repr__(self):
        parms=(
            self.condition, list(self.relvars), list(self.outers),
            list(self.columns.items())
        )
        return '%s%r' % (self._hashAndCompare[0], parms)


    def getInnerRVs(self):
        return self.relvars


    def getDB(self):
        db = self.relvars[0].getDB()
        for rv in self.relvars[1:]:
            if rv.getDB() is not db:
                return None
        return db























    def simpleSQL(self,driver=None):
        if driver is None:
            driver = SQLDriver(self)
        columnNames = []
        remainingColumns = self.columns

        for tbl in self.relvars:

            tblCols = tbl.attributes()
            outputSubset = remainingColumns * kjSet(tblCols.values())
            remainingColumns = remainingColumns - outputSubset

            if outputSubset==tblCols:
                # All names in table are kept as-is, so just use '*'
                columnNames.append(driver.getAlias(tbl)+".*")
                continue

            # For all output columns that are in this table...
            for name,col in outputSubset.items():
                sql = col.simpleSQL(driver)
                if name<>col.name:
                    sql='%s AS %s' % (sql,name)
                columnNames.append(sql)

        for name,col in remainingColumns.items():
            columnNames.append('%s AS %s' % (col.simpleSQL(driver),name))

        tablenames = [driver.getFromDef(tbl) for tbl in self.relvars]
        tablenames.sort()

        columnNames.sort()
        sql = "SELECT "+", ".join(columnNames)+" FROM "+", ".join(tablenames)

        condSQL = self.condition.simpleSQL(driver)
        if condSQL:
            sql += " WHERE " + condSQL

        return sql



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

    def simpleSQL(self,driver):
        return ' AND '.join([op.simpleSQL(driver) for op in self.operands])

class Or(_compound):

    def _getPromotable(self,op):
        return adapt(op,IBooleanExpression).disjuncts()

    def disjuncts(self):
        return self.operands

    def __invert__(self):
        return And(*tuple([~op for op in self.operands]))

    def simpleSQL(self,driver):
        return '('+' OR '.join([op.simpleSQL(driver) for op in self.operands])+')'

class Not(_compound):

    def __init__(self,operand):
        self.operands = operand,
        self._hashAndCompare = self.__class__.__name__, self.operands

    def __invert__(self):
        return self.operands[0]

    def simpleSQL(self,driver):
        return 'NOT (%s)' % self.operands[0].simpleSQL(driver)


class Cmp(_expr, HashAndCompare):

    invOps = {'=':'<>', '<':'>=', '>':'<='}
    invOps = kjGraph(invOps.items())
    invOps = invOps + ~invOps

    def __init__(self,arg1,op,arg2):
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2
        self._hashAndCompare = op,arg1,arg2

    def __invert__(self):
        try:
            revOp = self.invOps[self.op]
        except KeyError:
            return Not(self)
        else:
            return self.__class__(self.arg1,revOp,self.arg2)

    def __repr__(self):
        return 'Cmp%r' % ((self.arg1,self.op,self.arg2),)

    def simpleSQL(self,driver):
        return '%s%s%s' % (
            driver.sqlize(self.arg1),self.op,driver.sqlize(self.arg2)
        )















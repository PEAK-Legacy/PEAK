"""Query Interfaces"""

from protocols import Interface

__all__ = [
    'IRelationVariable', 'IRelationCondition', 'IBooleanExpression',
    'IRelationAttribute', 'IRelationComparison', 'ISQLDriver',
    'IDomainVariable',
]

class IBooleanExpression(Interface):

    def conjuncts():
        """Return the sequence of conjuncts of this expression

        For an 'and' operation, this should return the and-ed expressions.
        For most other operations, this should return a one-element sequence
        containing the expression object itself."""

    def disjuncts():
        """Return the sequence of disjuncts of this expression

        For an 'or' operation, this should return the or-ed expressions.
        For most other operations, this should return a one-element sequence
        containing the expression object itself."""

    def __cmp__(other):
        """Boolean expressions must be comparable to each other"""

    def __hash__(other):
        """Boolean expressions must be hashable"""

    def __invert__():
        """Return the inverse ("not") of this expression"""

    def __and__(expr):
        """Return the conjunction ("and") of this expression with 'expr'"""

    def __or__(expr):
        """Return the disjunction ("or") of this expression with 'expr'"""

class IRelationCondition(IBooleanExpression):

    """A boolean condition in relational algebra"""

    def appliesTo(attrNames):
        """Does condition depend on any of the named columns?"""

    def rejectsNullsFor(attrNames):
        """Does condition require a non-null value for any named column?

        This method is used to determine whether an outer join can be reduced
        to a regular join, due to a requirement that an outer-joined column be
        non-null.  (Note that for 'rejectsNullsFor()' to be true for an 'or'
        condition, it must be true for *all* the 'or'-ed subconditions.)"""

    # XXX need some way to return renamed version

class IDomainVariable(Interface):
    """A domain variable in relational algebra"""

    def isAggregate():
        """Return true if DV represents an aggregate function"""

class IRelationAttribute(IDomainVariable):
    """A domain variable that's a simple column reference"""

    def getName():
        """Return this column's original name in its containing table"""

    def getRV():
        """Return the relvar representing this column's containing table"""

    def getDB(self):
        """Return the database this column belongs to"""


class IRelationComparison(IRelationCondition):
    """A comparison operator in relational algebra"""
    # XXX Don't know what we need here yet


class IRelationVariable(Interface):

    """A relation variable (RV) in relational algebra"""

    def __call__(where=None,join=(),outer=(),rename=(),keep=(),calc=(),groupBy=()):
        """Return a new RV based on select/project/join operations as follows:

        'where' -- specify a condition that all rows of the new RV must meet
        (equivalent to the relational algebra 'select' operation).

        'join' -- an iterable of RV's that will be inner-joined with this RV
        (if no 'where' is supplied, this is a cartesian product.)

        'outer' -- an iterable of RV's that will be outer-joined with this RV's
        inner-joined portions.

        'keep' -- a sequence of the names of the columns that should be kept in
        the new RV.  Supplying a non-empty value here is equivalent to the
        relational algebra 'project' operation.

        'rename' -- a sequence of '(oldName,newName)' tuples specifying columns
        to be renamed.  The old columns are automatically "kept", so if you
        mix 'rename' and 'keep', you do not need to list renamed columns in the
        'keep' argument.

        'calc' -- a sequence of '(name,DV)' pairs specifying computed columns
        to include in the new RV.  These columns are always added under the
        given names, so 'keep' and 'rename' have no effect on the new columns.

        'groupBy' -- a sequence of the names of the columns that the resulting
        RV should be summarized on.  These columns will be automatically
        "kept", so if you mix 'groupBy' and 'keep', you do not need to list
        group-by columns in the 'keep' argument.  Note that when using
        'groupBy', you should only keep or calculate columns that represent
        aggregates, or else an error will occur.
        """

    def clone():
        """Return a deepcopy()-like clone of the RV"""


    def keys():
        """Return a sequence of column names"""

    def __getitem__(columnName):
        """Return the IRelationAttribute for the named column"""

    def attributes():
        """Return a kjGraph mapping names->relation attributes"""

    def getDB():
        """Return an object indicating the responsible DB, or None if mixed"""

    def getInnerRVs():
        """Return sequence of inner-join RV's, or (self,) if not a join"""

    def getOuterRVs():
        """Return sequence of outer-join RV's, or () if not outer join"""

    def getCondition():
        """Return any select() or join condition applying to this RV"""

    def getReferencedRVs():
        """Return sequence of all RVs used in this RV (eg: joins,subqueries)"""

    def __cmp__(other):
        """Relation variables must be comparable to each other"""

    def __hash__(other):
        """Relation variables must be hashable"""


class ISQLDriver(Interface):
    """Helper object for SQL generation"""

    def getAlias(RV):
        """Get an alias name for the specified RV"""






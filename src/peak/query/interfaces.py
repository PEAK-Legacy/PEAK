"""Query Interfaces"""

from protocols import Interface

__all__ = [
    'IRelationVariable', 'IRelationCondition', 'IBooleanExpression',
    'IRelationAttribute', 'IRelationComparison',
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


class IRelationAttribute(Interface):
    """A column variable in relational algebra"""
    # XXX Don't know what we need here yet


class IRelationComparison(IRelationCondition):
    """A comparison operator in relational algebra"""
    # XXX Don't know what we need here yet















class IRelationVariable(Interface):
    """A relation variable (RV) in relational algebra"""

    def select(condition):
        """Return RV representing this RV filtered by 'condition'"""

    def project(attrNames):
        """Return RV representing the 'attrNames' subset of columns of this RV

        This is shorthand for 'remap(name1="name1", name2="name2",...)' for
        the named attributes."""

    def remap(__keep__=False, **newFromOld):
        """Return RV with name changes

        Keyword arguments are used to name new columns, with the old column
        they are derived from, e.g.::

            anRV.rename(newCol='oldCol', copyOfOld='oldCol', ...)

        The positional argument '__keep__', if supplied, indicates that any
        columns not mentioned in the keyword arguments should be kept.
        Otherwise, unmentioned columns should be dropped."""

    def thetaJoin(condition,*relvars):
        """Return the theta-join of this RV with 'relvars' on 'condition'"""

    def starJoin(condition,relvar):
        """Outer join of this RV's "base" with 'relvar' on 'condition'

        An RV's "base" is defined as the portion of the RV that does *not*
        include any existing star joins.  Note: "star join" is a made-up term
        here, intended to apply to the subset of outer joins that's needed to
        implement conceptual queries."""

    def attributes():
        """Return a sequence of names of the relvar's columns (attributes)"""

    def getDB():
        """Return an object indicating the responsible DB, or None if mixed"""

    def __cmp__(other):
        """Relation variables must be comparable to each other"""

    def __hash__(other):
        """Relation variables must be hashable"""





































"""Query Interfaces"""

from protocols import Interface

__all__ = [
    'IRelationVariable', 'IRelationCondition',
    'IRelationAttribute', 'IRelationComparison',
]

class IRelationCondition(Interface):

    """A boolean condition in relational algebra"""

    def conjuncts():
        """Return the sequence of conjuncts of this condition

        For an 'and' operation, this should return the and-ed conditions.
        For most other operations, this should return a one-element sequence
        containing the condition object itself."""

    def appliesTo(attrNames):
        """Does condition depend on any of the named columns?"""

    def rejectsNullsFor(attrNames):
        """Does condition require a non-null value for any named column?

        This method is used to determine whether an outer join can be reduced
        to a regular join, due to a requirement that an outer-joined column be
        non-null.  (Note that for 'rejectsNullsFor()' to be true for an 'or'
        condition, it must be true for *all* the 'or'-ed subconditions.)"""

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

    def outerJoin(condition,relvar):
        """Return the outer join of this RV with 'relvar' on 'condition'"""

    def attributes():
        """Return a sequence of names of the relvar's columns (attributes)"""









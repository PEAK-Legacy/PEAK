# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Foundation.Data_Types
# File:    peak\metamodels\UML13\model\Foundation\Data_Types.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
_config              = _lazy('peak.config.api')


# ------------------------------------------------------------------------------


class Multiplicity(_model.Element):

    class range(_model.StructuralFeature):
        referencedType = 'MultiplicityRange'
        referencedEnd = 'multiplicity'
        isComposite = True
        lowerBound = 1
        sortPosn = 0


class MultiplicityRange(_model.Element):

    class lower(_model.StructuralFeature):
        referencedType = 'Integer'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class upper(_model.StructuralFeature):
        referencedType = 'UnlimitedInteger'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class multiplicity(_model.StructuralFeature):
        referencedType = 'Multiplicity'
        referencedEnd = 'range'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2


class Expression(_model.Element):

    class language(_model.StructuralFeature):
        referencedType = 'Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class body(_model.StructuralFeature):
        referencedType = 'String'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1


class ObjectSetExpression(Expression):
    pass


class TimeExpression(Expression):
    pass


class BooleanExpression(Expression):
    pass


class ActionExpression(Expression):
    pass


class IterationExpression(Expression):
    pass


class TypeExpression(Expression):
    pass


class ArgListsExpression(Expression):
    pass


class MappingExpression(Expression):
    pass


class ProcedureExpression(Expression):
    pass


class Integer(_model.Long):
    pass


class UnlimitedInteger(_model.Long):
    pass


class String(_model.String):
    length = 0


class Time(_model.Float):
    pass


class AggregationKind(_model.Enumeration):
    ak_none = _model.enum(u'none')
    ak_aggregate = _model.enum(u'aggregate')
    ak_composite = _model.enum(u'composite')


class Boolean(_model.Boolean):
    pass


class CallConcurrencyKind(_model.Enumeration):
    cck_sequential = _model.enum(u'sequential')
    cck_guarded = _model.enum(u'guarded')
    cck_concurrent = _model.enum(u'concurrent')


class ChangeableKind(_model.Enumeration):
    ck_changeable = _model.enum(u'changeable')
    ck_frozen = _model.enum(u'frozen')
    ck_addOnly = _model.enum(u'addOnly')


class MessageDirectionKind(_model.Enumeration):
    mdk_activation = _model.enum(u'activation')
    mdk_return = _model.enum(u'return')


class OrderingKind(_model.Enumeration):
    ok_unordered = _model.enum(u'unordered')
    ok_ordered = _model.enum(u'ordered')
    ok_sorted = _model.enum(u'sorted')


class ParameterDirectionKind(_model.Enumeration):
    pdk_in = _model.enum(u'in')
    pdk_inout = _model.enum(u'inout')
    pdk_out = _model.enum(u'out')
    pdk_return = _model.enum(u'return')


class PseudostateKind(_model.Enumeration):
    pk_initial = _model.enum(u'initial')
    pk_deepHistory = _model.enum(u'deepHistory')
    pk_shallowHistory = _model.enum(u'shallowHistory')
    pk_join = _model.enum(u'join')
    pk_fork = _model.enum(u'fork')
    pk_branch = _model.enum(u'branch')
    pk_junction = _model.enum(u'junction')
    pk_final = _model.enum(u'final')


class ScopeKind(_model.Enumeration):
    sk_instance = _model.enum(u'instance')
    sk_classifier = _model.enum(u'classifier')


class VisibilityKind(_model.Enumeration):
    vk_public = _model.enum(u'public')
    vk_protected = _model.enum(u'protected')
    vk_private = _model.enum(u'private')


class Mapping(_model.String):
    length = 0


class Name(_model.String):
    length = 0


class LocationReference(_model.String):
    length = 0


class Geometry(_model.String):
    length = 0

# ------------------------------------------------------------------------------

_config.setupModule()



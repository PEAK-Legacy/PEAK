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
    ak_none = _model.enum()
    ak_aggregate = _model.enum()
    ak_composite = _model.enum()
    

class Boolean(_model.Boolean):
    pass
    

class CallConcurrencyKind(_model.Enumeration):
    cck_sequential = _model.enum()
    cck_guarded = _model.enum()
    cck_concurrent = _model.enum()
    

class ChangeableKind(_model.Enumeration):
    ck_changeable = _model.enum()
    ck_frozen = _model.enum()
    ck_addOnly = _model.enum()
    

class MessageDirectionKind(_model.Enumeration):
    mdk_activation = _model.enum()
    mdk_return = _model.enum()
    

class OrderingKind(_model.Enumeration):
    ok_unordered = _model.enum()
    ok_ordered = _model.enum()
    ok_sorted = _model.enum()
    

class ParameterDirectionKind(_model.Enumeration):
    pdk_in = _model.enum()
    pdk_inout = _model.enum()
    pdk_out = _model.enum()
    pdk_return = _model.enum()
    

class PseudostateKind(_model.Enumeration):
    pk_initial = _model.enum()
    pk_deepHistory = _model.enum()
    pk_shallowHistory = _model.enum()
    pk_join = _model.enum()
    pk_fork = _model.enum()
    pk_branch = _model.enum()
    pk_junction = _model.enum()
    pk_final = _model.enum()
    

class ScopeKind(_model.Enumeration):
    sk_instance = _model.enum()
    sk_classifier = _model.enum()
    

class VisibilityKind(_model.Enumeration):
    vk_public = _model.enum()
    vk_protected = _model.enum()
    vk_private = _model.enum()
    

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



# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Behavioral_Elements.Common_Behavior
# File:    peak\metamodels\UML13\model\Behavioral_Elements\Common_Behavior.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
_config              = _lazy('peak.config.api')
_datatypes           = _lazy('peak.model.datatypes')

Core                 = _lazy(__name__, '../../Foundation/Core')

# ------------------------------------------------------------------------------


class Instance(Core.ModelElement):
    
    class classifier(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        isReference = True
        lowerBound = 1
        sortPosn = 0
    
    class attributeLink(_model.StructuralFeature):
        referencedType = 'AttributeLink'
        referencedEnd = 'value'
        isReference = True
        sortPosn = 1
    
    class linkEnd(_model.StructuralFeature):
        referencedType = 'LinkEnd'
        referencedEnd = 'instance'
        isReference = True
        sortPosn = 2
    
    class slot(_model.StructuralFeature):
        referencedType = 'AttributeLink'
        referencedEnd = 'instance'
        isReference = True
        sortPosn = 3
    
    class stimulus1(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'argument'
        isReference = True
        sortPosn = 4
    
    class stimulus3(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'sender'
        isReference = True
        sortPosn = 5
    
    class componentInstance(_model.StructuralFeature):
        referencedType = 'ComponentInstance'
        referencedEnd = 'resident'
        isReference = True
        upperBound = 1
        sortPosn = 6
    
    class stimulus2(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'receiver'
        isReference = True
        sortPosn = 7
    

class Signal(Core.Classifier):
    
    class reception(_model.StructuralFeature):
        referencedType = 'Reception'
        referencedEnd = 'signal'
        isReference = True
        sortPosn = 0
    
    class context(_model.StructuralFeature):
        referencedType = 'Foundation/Core/BehavioralFeature'
        isReference = True
        sortPosn = 1
    
    class sendAction(_model.StructuralFeature):
        referencedType = 'SendAction'
        referencedEnd = 'signal'
        isReference = True
        sortPosn = 2
    

class Action(Core.ModelElement):
    
    mdl_isAbstract = True
    
    class actualArgument(_model.StructuralFeature):
        referencedType = 'Argument'
        referencedEnd = 'action'
        isReference = True
        sortPosn = 0
    
    class actionSequence(_model.StructuralFeature):
        referencedType = 'ActionSequence'
        referencedEnd = 'action'
        isReference = True
        upperBound = 1
        sortPosn = 1
    
    class stimulus(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'dispatchAction'
        isReference = True
        sortPosn = 2
    
    class recurrence(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/IterationExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    
    class target(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/ObjectSetExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4
    
    class isAsynchronous(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 5
    
    class script(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/ActionExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 6
    

class CreateAction(Action):
    
    class instantiation(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    

class DestroyAction(Action):
    pass
    

class UninterpretedAction(Action):
    pass
    

class AttributeLink(Core.ModelElement):
    
    class attribute(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Attribute'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class value(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'attributeLink'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class instance(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'slot'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class linkEnd(_model.StructuralFeature):
        referencedType = 'LinkEnd'
        referencedEnd = 'qualifiedValue'
        isReference = True
        upperBound = 1
        sortPosn = 3
    

class Object(Instance):
    pass
    

class Link(Core.ModelElement):
    
    class association(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Association'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class connection(_model.StructuralFeature):
        referencedType = 'LinkEnd'
        referencedEnd = 'link'
        isReference = True
        lowerBound = 2
        sortPosn = 1
    
    class stimulus(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'communicationLink'
        isReference = True
        sortPosn = 2
    

class LinkObject(Object, Link):
    pass
    

class DataValue(Instance):
    pass
    

class CallAction(Action):
    
    class operation(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Operation'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    

class SendAction(Action):
    
    class signal(_model.StructuralFeature):
        referencedType = 'Signal'
        referencedEnd = 'sendAction'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    

class ActionSequence(Action):
    
    class action(_model.StructuralFeature):
        referencedType = 'Action'
        referencedEnd = 'actionSequence'
        isReference = True
        sortPosn = 0
    

class Argument(Core.ModelElement):
    
    class action(_model.StructuralFeature):
        referencedType = 'Action'
        referencedEnd = 'actualArgument'
        isReference = True
        upperBound = 1
        sortPosn = 0
    
    class value(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Expression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    

class Reception(Core.BehavioralFeature):
    
    class signal(_model.StructuralFeature):
        referencedType = 'Signal'
        referencedEnd = 'reception'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class specification(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/String'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class isRoot(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class isLeaf(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    
    class isAbstract(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4
    

class LinkEnd(Core.ModelElement):
    
    class instance(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'linkEnd'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class link(_model.StructuralFeature):
        referencedType = 'Link'
        referencedEnd = 'connection'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class associationEnd(_model.StructuralFeature):
        referencedType = 'Foundation/Core/AssociationEnd'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class qualifiedValue(_model.StructuralFeature):
        referencedType = 'AttributeLink'
        referencedEnd = 'linkEnd'
        isReference = True
        sortPosn = 3
    

class ReturnAction(Action):
    pass
    

class TerminateAction(Action):
    pass
    

class Stimulus(Core.ModelElement):
    
    class argument(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'stimulus1'
        isReference = True
        sortPosn = 0
    
    class sender(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'stimulus3'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class receiver(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'stimulus2'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class communicationLink(_model.StructuralFeature):
        referencedType = 'Link'
        referencedEnd = 'stimulus'
        isReference = True
        upperBound = 1
        sortPosn = 3
    
    class dispatchAction(_model.StructuralFeature):
        referencedType = 'Action'
        referencedEnd = 'stimulus'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 4
    

class Exception(Signal):
    pass
    

class ComponentInstance(Instance):
    
    class nodeInstance(_model.StructuralFeature):
        referencedType = 'NodeInstance'
        referencedEnd = 'resident'
        isReference = True
        upperBound = 1
        sortPosn = 0
    
    class resident(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'componentInstance'
        isReference = True
        sortPosn = 1
    

class NodeInstance(Instance):
    
    class resident(_model.StructuralFeature):
        referencedType = 'ComponentInstance'
        referencedEnd = 'nodeInstance'
        isReference = True
        sortPosn = 0
    
# ------------------------------------------------------------------------------

_config.setupModule()



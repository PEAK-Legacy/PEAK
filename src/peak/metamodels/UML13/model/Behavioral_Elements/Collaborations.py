# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Behavioral_Elements.Collaborations
# File:    peak\metamodels\UML13\model\Behavioral_Elements\Collaborations.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
_config              = _lazy('peak.config.api')
_datatypes           = _lazy('peak.model.datatypes')

Core                 = _lazy(__name__, '../../Foundation/Core')

# ------------------------------------------------------------------------------


class Collaboration(Core.GeneralizableElement, Core.Namespace):
    
    class interaction(_model.StructuralFeature):
        referencedType = 'Interaction'
        referencedEnd = 'context'
        isReference = True
        sortPosn = 0
    
    class representedClassifier(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        isReference = True
        upperBound = 1
        sortPosn = 1
    
    class representedOperation(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Operation'
        isReference = True
        upperBound = 1
        sortPosn = 2
    
    class constrainingElement(_model.StructuralFeature):
        referencedType = 'Foundation/Core/ModelElement'
        isReference = True
        sortPosn = 3
    

class ClassifierRole(Core.Classifier):
    
    class multiplicity(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class base(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        isReference = True
        lowerBound = 1
        sortPosn = 1
    
    class availableFeature(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Feature'
        isReference = True
        sortPosn = 2
    
    class message1(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'receiver'
        isReference = True
        sortPosn = 3
    
    class message2(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'sender'
        isReference = True
        sortPosn = 4
    
    class availableContents(_model.StructuralFeature):
        referencedType = 'Foundation/Core/ModelElement'
        isReference = True
        sortPosn = 5
    

class AssociationRole(Core.Association):
    
    class multiplicity(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class base(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Association'
        isReference = True
        upperBound = 1
        sortPosn = 1
    
    class message(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'communicationConnection'
        isReference = True
        sortPosn = 2
    

class AssociationEndRole(Core.AssociationEnd):
    
    class collaborationMultiplicity(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class base(_model.StructuralFeature):
        referencedType = 'Foundation/Core/AssociationEnd'
        isReference = True
        upperBound = 1
        sortPosn = 1
    
    class availableQualifier(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Attribute'
        isReference = True
        sortPosn = 2
    

class Message(Core.ModelElement):
    
    class interaction(_model.StructuralFeature):
        referencedType = 'Interaction'
        referencedEnd = 'message'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class activator(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'message4'
        isReference = True
        upperBound = 1
        sortPosn = 1
    
    class sender(_model.StructuralFeature):
        referencedType = 'ClassifierRole'
        referencedEnd = 'message2'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class receiver(_model.StructuralFeature):
        referencedType = 'ClassifierRole'
        referencedEnd = 'message1'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    
    class predecessor(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'message3'
        isReference = True
        sortPosn = 4
    
    class communicationConnection(_model.StructuralFeature):
        referencedType = 'AssociationRole'
        referencedEnd = 'message'
        isReference = True
        upperBound = 1
        sortPosn = 5
    
    class action(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Action'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 6
    
    class message3(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'predecessor'
        isReference = True
        sortPosn = 7
    
    class message4(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'activator'
        isReference = True
        sortPosn = 8
    

class Interaction(Core.ModelElement):
    
    class message(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'interaction'
        isReference = True
        lowerBound = 1
        sortPosn = 0
    
    class context(_model.StructuralFeature):
        referencedType = 'Collaboration'
        referencedEnd = 'interaction'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
# ------------------------------------------------------------------------------

_config.setupModule()



# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Foundation.Extension_Mechanisms
# File:    peak\metamodels\UML13\model\Foundation\Extension_Mechanisms.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
_config              = _lazy('peak.config.api')
_datatypes           = _lazy('peak.model.datatypes')

Core                 = _lazy(__name__, '../Core')

# ------------------------------------------------------------------------------


class Stereotype(Core.GeneralizableElement):
    
    class requiredTag(_model.StructuralFeature):
        referencedType = 'TaggedValue'
        referencedEnd = 'stereotype'
        isReference = True
        sortPosn = 0
    
    class extendedElement(_model.StructuralFeature):
        referencedType = 'Core/ModelElement'
        isReference = True
        sortPosn = 1
    
    class stereotypeConstraint(_model.StructuralFeature):
        referencedType = 'Core/Constraint'
        isReference = True
        sortPosn = 2
    
    class icon(_model.StructuralFeature):
        referencedType = 'Data_Types/Geometry'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    
    class baseClass(_model.StructuralFeature):
        referencedType = 'Data_Types/Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4
    

class TaggedValue(_model.Element):
    
    class stereotype(_model.StructuralFeature):
        referencedType = 'Stereotype'
        referencedEnd = 'requiredTag'
        isReference = True
        upperBound = 1
        sortPosn = 0
    
    class modelElement(_model.StructuralFeature):
        referencedType = 'Core/ModelElement'
        isReference = True
        upperBound = 1
        sortPosn = 1
    
    class tag(_model.StructuralFeature):
        referencedType = 'Data_Types/Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class value(_model.StructuralFeature):
        referencedType = 'Data_Types/String'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    
# ------------------------------------------------------------------------------

_config.setupModule()



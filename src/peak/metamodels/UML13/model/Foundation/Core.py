# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Foundation.Core
# File:    peak\metamodels\UML13\model\Foundation\Core.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
_config              = _lazy('peak.config.api')
_datatypes           = _lazy('peak.model.datatypes')


# ------------------------------------------------------------------------------


class Element(_model.Element):
    
    mdl_isAbstract = True
    

class ModelElement(Element):
    
    mdl_isAbstract = True
    
    class namespace(_model.StructuralFeature):
        referencedType = 'Namespace'
        referencedEnd = 'ownedElement'
        isReference = True
        upperBound = 1
        sortPosn = 0
    
    class clientDependency(_model.StructuralFeature):
        referencedType = 'Dependency'
        referencedEnd = 'client'
        isReference = True
        sortPosn = 1
    
    class constraint(_model.StructuralFeature):
        referencedType = 'Constraint'
        referencedEnd = 'constrainedElement'
        isReference = True
        sortPosn = 2
    
    class supplierDependency(_model.StructuralFeature):
        referencedType = 'Dependency'
        referencedEnd = 'supplier'
        isReference = True
        sortPosn = 3
    
    class presentation(_model.StructuralFeature):
        referencedType = 'PresentationElement'
        referencedEnd = 'subject'
        isReference = True
        sortPosn = 4
    
    class targetFlow(_model.StructuralFeature):
        referencedType = 'Flow'
        referencedEnd = 'target'
        isReference = True
        sortPosn = 5
    
    class sourceFlow(_model.StructuralFeature):
        referencedType = 'Flow'
        referencedEnd = 'source'
        isReference = True
        sortPosn = 6
    
    class templateParameter3(_model.StructuralFeature):
        referencedType = 'TemplateParameter'
        referencedEnd = 'defaultElement'
        isReference = True
        sortPosn = 7
    
    class binding(_model.StructuralFeature):
        referencedType = 'Binding'
        referencedEnd = 'argument'
        isReference = True
        upperBound = 1
        sortPosn = 8
    
    class comment(_model.StructuralFeature):
        referencedType = 'Comment'
        referencedEnd = 'annotatedElement'
        isReference = True
        sortPosn = 9
    
    class elementResidence(_model.StructuralFeature):
        referencedType = 'ElementResidence'
        referencedEnd = 'resident'
        isReference = True
        sortPosn = 10
    
    class templateParameter(_model.StructuralFeature):
        referencedType = 'TemplateParameter'
        referencedEnd = 'modelElement'
        isReference = True
        sortPosn = 11
    
    class templateParameter2(_model.StructuralFeature):
        referencedType = 'TemplateParameter'
        referencedEnd = 'modelElement2'
        isReference = True
        sortPosn = 12
    
    class name(_model.StructuralFeature):
        referencedType = 'Data_Types/Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 13
    
    class visibility(_model.StructuralFeature):
        referencedType = 'Data_Types/VisibilityKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 14
    
    class isSpecification(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 15
    

class GeneralizableElement(ModelElement):
    
    mdl_isAbstract = True
    
    class generalization(_model.StructuralFeature):
        referencedType = 'Generalization'
        referencedEnd = 'child'
        isReference = True
        sortPosn = 0
    
    class specialization(_model.StructuralFeature):
        referencedType = 'Generalization'
        referencedEnd = 'parent'
        isReference = True
        sortPosn = 1
    
    class isRoot(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class isLeaf(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    
    class isAbstract(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4
    

class Namespace(ModelElement):
    
    mdl_isAbstract = True
    
    class ownedElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'namespace'
        isReference = True
        sortPosn = 0
    

class Classifier(GeneralizableElement, Namespace):
    
    mdl_isAbstract = True
    
    class feature(_model.StructuralFeature):
        referencedType = 'Feature'
        referencedEnd = 'owner'
        isReference = True
        sortPosn = 0
    
    class participant(_model.StructuralFeature):
        referencedType = 'AssociationEnd'
        referencedEnd = 'specification'
        isReference = True
        sortPosn = 1
    
    class powertypeRange(_model.StructuralFeature):
        referencedType = 'Generalization'
        referencedEnd = 'powertype'
        isReference = True
        sortPosn = 2
    

class Class(Classifier):
    
    class isActive(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    

class DataType(Classifier):
    pass
    

class Feature(ModelElement):
    
    mdl_isAbstract = True
    
    class owner(_model.StructuralFeature):
        referencedType = 'Classifier'
        referencedEnd = 'feature'
        isReference = True
        upperBound = 1
        sortPosn = 0
    
    class ownerScope(_model.StructuralFeature):
        referencedType = 'Data_Types/ScopeKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    

class StructuralFeature(Feature):
    
    mdl_isAbstract = True
    
    class type(_model.StructuralFeature):
        referencedType = 'Classifier'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class multiplicity(_model.StructuralFeature):
        referencedType = 'Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class changeability(_model.StructuralFeature):
        referencedType = 'Data_Types/ChangeableKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class targetScope(_model.StructuralFeature):
        referencedType = 'Data_Types/ScopeKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    

class AssociationEnd(ModelElement):
    
    class association(_model.StructuralFeature):
        referencedType = 'Association'
        referencedEnd = 'connection'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class qualifier(_model.StructuralFeature):
        referencedType = 'Attribute'
        referencedEnd = 'associationEnd'
        isReference = True
        sortPosn = 1
    
    class type(_model.StructuralFeature):
        referencedType = 'Classifier'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class specification(_model.StructuralFeature):
        referencedType = 'Classifier'
        referencedEnd = 'participant'
        isReference = True
        sortPosn = 3
    
    class isNavigable(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4
    
    class ordering(_model.StructuralFeature):
        referencedType = 'Data_Types/OrderingKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 5
    
    class aggregation(_model.StructuralFeature):
        referencedType = 'Data_Types/AggregationKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 6
    
    class targetScope(_model.StructuralFeature):
        referencedType = 'Data_Types/ScopeKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 7
    
    class multiplicity(_model.StructuralFeature):
        referencedType = 'Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 8
    
    class changeability(_model.StructuralFeature):
        referencedType = 'Data_Types/ChangeableKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 9
    

class Interface(Classifier):
    pass
    

class Constraint(ModelElement):
    
    class constrainedElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'constraint'
        isReference = True
        sortPosn = 0
    
    class body(_model.StructuralFeature):
        referencedType = 'Data_Types/BooleanExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    

class Relationship(ModelElement):
    
    mdl_isAbstract = True
    

class Association(GeneralizableElement, Relationship):
    
    class connection(_model.StructuralFeature):
        referencedType = 'AssociationEnd'
        referencedEnd = 'association'
        isReference = True
        lowerBound = 2
        sortPosn = 0
    

class Attribute(StructuralFeature):
    
    class associationEnd(_model.StructuralFeature):
        referencedType = 'AssociationEnd'
        referencedEnd = 'qualifier'
        isReference = True
        upperBound = 1
        sortPosn = 0
    
    class initialValue(_model.StructuralFeature):
        referencedType = 'Data_Types/Expression'
        upperBound = 1
        sortPosn = 1
    

class BehavioralFeature(Feature):
    
    mdl_isAbstract = True
    
    class parameter(_model.StructuralFeature):
        referencedType = 'Parameter'
        referencedEnd = 'behavioralFeature'
        isReference = True
        sortPosn = 0
    
    class isQuery(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    

class Operation(BehavioralFeature):
    
    class method(_model.StructuralFeature):
        referencedType = 'Method'
        referencedEnd = 'specification'
        isReference = True
        sortPosn = 0
    
    class concurrency(_model.StructuralFeature):
        referencedType = 'Data_Types/CallConcurrencyKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class isRoot(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
    class isLeaf(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    
    class isAbstract(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4
    
    class specification(_model.StructuralFeature):
        referencedType = 'Data_Types/String'
        upperBound = 1
        lowerBound = 1
        sortPosn = 5
    

class Parameter(ModelElement):
    
    class behavioralFeature(_model.StructuralFeature):
        referencedType = 'BehavioralFeature'
        referencedEnd = 'parameter'
        isReference = True
        upperBound = 1
        sortPosn = 0
    
    class type(_model.StructuralFeature):
        referencedType = 'Classifier'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class defaultValue(_model.StructuralFeature):
        referencedType = 'Data_Types/Expression'
        upperBound = 1
        sortPosn = 2
    
    class kind(_model.StructuralFeature):
        referencedType = 'Data_Types/ParameterDirectionKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    

class Method(BehavioralFeature):
    
    class specification(_model.StructuralFeature):
        referencedType = 'Operation'
        referencedEnd = 'method'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class body(_model.StructuralFeature):
        referencedType = 'Data_Types/ProcedureExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    

class Generalization(Relationship):
    
    class child(_model.StructuralFeature):
        referencedType = 'GeneralizableElement'
        referencedEnd = 'generalization'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class parent(_model.StructuralFeature):
        referencedType = 'GeneralizableElement'
        referencedEnd = 'specialization'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class powertype(_model.StructuralFeature):
        referencedType = 'Classifier'
        referencedEnd = 'powertypeRange'
        isReference = True
        upperBound = 1
        sortPosn = 2
    
    class discriminator(_model.StructuralFeature):
        referencedType = 'Data_Types/Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3
    

class AssociationClass(Association, Class):
    pass
    

class Dependency(Relationship):
    
    class client(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'clientDependency'
        isReference = True
        lowerBound = 1
        sortPosn = 0
    
    class supplier(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'supplierDependency'
        isReference = True
        lowerBound = 1
        sortPosn = 1
    

class Abstraction(Dependency):
    
    class mapping(_model.StructuralFeature):
        referencedType = 'Data_Types/MappingExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    

class PresentationElement(Element):
    
    mdl_isAbstract = True
    
    class subject(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'presentation'
        isReference = True
        sortPosn = 0
    

class Usage(Dependency):
    pass
    

class Binding(Dependency):
    
    class argument(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'binding'
        isReference = True
        lowerBound = 1
        sortPosn = 0
    

class Component(Classifier):
    
    class deploymentLocation(_model.StructuralFeature):
        referencedType = 'Node'
        referencedEnd = 'resident'
        isReference = True
        sortPosn = 0
    
    class residentElement(_model.StructuralFeature):
        referencedType = 'ElementResidence'
        referencedEnd = 'implementationLocation'
        isReference = True
        sortPosn = 1
    

class Node(Classifier):
    
    class resident(_model.StructuralFeature):
        referencedType = 'Component'
        referencedEnd = 'deploymentLocation'
        isReference = True
        sortPosn = 0
    

class Permission(Dependency):
    pass
    

class Comment(ModelElement):
    
    class annotatedElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'comment'
        isReference = True
        sortPosn = 0
    

class Flow(Relationship):
    
    class target(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'targetFlow'
        isReference = True
        sortPosn = 0
    
    class source(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'sourceFlow'
        isReference = True
        sortPosn = 1
    

class ElementResidence(_model.Element):
    
    class resident(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'elementResidence'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 0
    
    class implementationLocation(_model.StructuralFeature):
        referencedType = 'Component'
        referencedEnd = 'residentElement'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 1
    
    class visibility(_model.StructuralFeature):
        referencedType = 'Data_Types/VisibilityKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    

class TemplateParameter(_model.Element):
    
    class defaultElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'templateParameter3'
        isReference = True
        upperBound = 1
        sortPosn = 0
    
    class modelElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'templateParameter'
        isReference = True
        upperBound = 1
        sortPosn = 1
    
    class modelElement2(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'templateParameter2'
        isReference = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 2
    
# ------------------------------------------------------------------------------

_config.setupModule()



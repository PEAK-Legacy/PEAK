"""The UML 1.3 Metamodel, expressed as a Structural Aspect

    This module's code was originally generated from a non-normative XML
    representation of the UML 1.3 Metamodel, supplied as part of the
    Novosoft UML (nsuml) toolkit.  Previous versions of TransWarp used
    the XML representation directly, and only generated the class structure
    in memory, without actually creating any Python source code.  However,
    with the advent of TransWarp's relatively new "module inheritance"
    capability, it is now computationally cheaper by at least an order or
    two of magnitude to convert such metamodels to Python source code, and
    then inherit from the module, rather than computationally combine class
    definitions.  It's also somewhat more flexible, in that it allows you
    to make use of any technique you like to generate Python source code
    for metamodels!

    There is little of direct interest for the human reader in this module's
    source; a brief, one-time survey will probably suffice if you wish to get
    the picture of how a metamodel can be represented in code for use with
    PEAK.
"""

from peak.api import *


# XXX The generator rewrite really should sort simple attributes to be defined
# XXX before nested classes; the code will be much more readable that way.















class UMLClass(model.Model, storage.xmi.Loader):

    class LocationReference(model.PrimitiveType):
        pass


    class Time(model.PrimitiveType):
        pass


    class Mapping(model.PrimitiveType):
        pass


    class Geometry(model.PrimitiveType):
        pass


    class OrderingKind(model.Enumeration):
        sorted = 'sorted'
        ordered = 'ordered'
        unordered = 'unordered'


    class VisibilityKind(model.Enumeration):
        protected = 'protected'
        public = 'public'
        private = 'private'


    class PseudostateKind(model.Enumeration):
        fork = 'fork'
        shallowHistory = 'shallowHistory'
        junction = 'junction'
        branch = 'branch'
        deepHistory = 'deepHistory'
        initial = 'initial'
        final = 'final'
        join = 'join'


    class CallConcurrencyKind(model.Enumeration):
        concurrent = 'concurrent'
        guarded = 'guarded'
        sequential = 'sequential'


    class AggregationKind(model.Enumeration):
        aggregate = 'aggregate'
        composite = 'composite'
        none = 'none'


    class ParameterDirectionKind(model.Enumeration):

        __values__ = dict([
            ('in',     1),
            ('out',    2),
            ('inout',  3),
            ('return', 4),
        ])


    class ScopeKind(model.Enumeration):
        instance = 'instance'
        classifier = 'classifier'


    class ChangeableKind(model.Enumeration):
        frozen = 'frozen'
        addOnly = 'addOnly'
        changeable = 'changeable'


    class MessageDirectionKind(model.Enumeration):
        __values__ = dict([
            ('activation', 1),
            ('return',     2),
        ])



    class OperationDirectionKind(model.Enumeration):
        provide = 'provide'
        require = 'require'

    class UnlimitedInteger(model.PrimitiveType):

        def fromString(klass, value):
            if value=='*': return '*'
            return int(value)

        fromString = classmethod(fromString)


    class Integer(model.PrimitiveType):
        fromString = int

    class Boolean(model.Enumeration):
        true = 1; false = 0

    class String(model.PrimitiveType):
        pass

    class Name(model.PrimitiveType):
        pass


    class Multiplicity(model.DataType):

        class ranges(model.Sequence):
            _XMINames = ('Foundation.Data_Types.Multiplicity.range',)
            referencedType = 'MultiplicityRange'
            referencedEnd = 'multiplicity'
            isChangeable = False

        _XMINames = ('Foundation.Data_Types.Multiplicity',)



    class MultiplicityRange(model.DataType):

        class upper(model.Field):
            _XMINames = ('Foundation.Data_Types.MultiplicityRange.upper',)
            referencedType = 'UnlimitedInteger'
            isChangeable = False

        class lower(model.Field):
            _XMINames = ('Foundation.Data_Types.MultiplicityRange.lower',)
            referencedType = 'Integer'
            isChangeable = False

        _XMINames = ('Foundation.Data_Types.MultiplicityRange',)

        class multiplicity(model.Reference):
            _XMINames = ('Foundation.Data_Types.MultiplicityRange.multiplicity',)
            referencedType = 'Multiplicity'
            referencedEnd = 'ranges'
            isChangeable = False















    class Expression(model.DataType):

        class body(model.Field):
            _XMINames = ('Foundation.Data_Types.Expression.body',)
            referencedType = 'String'
            isChangeable = False

        _XMINames = ('Foundation.Data_Types.Expression',)

        class language(model.Field):
            _XMINames = ('Foundation.Data_Types.Expression.language',)
            referencedType = 'Name'
            isChangeable = False

    class TimeExpression(Expression):
        _XMINames = ('Foundation.Data_Types.TimeExpression',)

    class MappingExpression(Expression):
        _XMINames = ('Foundation.Data_Types.MappingExpression',)

    class ProcedureExpression(Expression):
        _XMINames = ('Foundation.Data_Types.ProcedureExpression',)

    class BooleanExpression(Expression):
        _XMINames = ('Foundation.Data_Types.BooleanExpression',)

    class ActionExpression(Expression):
        _XMINames = ('Foundation.Data_Types.ActionExpression',)

    class ObjectSetExpression(Expression):
        _XMINames = ('Foundation.Data_Types.ObjectSetExpression',)

    class ArgListsExpression(Expression):
        _XMINames = ('Foundation.Data_Types.ArgListsExpression',)



    class TypeExpression(Expression):
        _XMINames = ('Foundation.Data_Types.TypeExpression',)

    class IterationExpression(Expression):
        _XMINames = ('Foundation.Data_Types.IterationExpression',)




































    class Base(model.Element):
        _isAbstract = 1
    
        class extensions(model.Collection):
            _XMINames = ('Base.extension',)
            referencedType = 'Extension'
            referencedEnd = 'baseElement'
    
        _XMINames = ('Base',)


    class Element(Base):
        _isAbstract = 1
        _XMINames = ('Foundation.Core.Element',)


    class ModelElement(Element):
    
        class isSpecification(model.Field):
            _XMINames = ('Foundation.Core.ModelElement.isSpecification',)
            referencedType = 'Boolean'
    
        _isAbstract = 1
    
        class elementResidences(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.elementResidence',)
            referencedType = 'ElementResidence'
            referencedEnd = 'resident'
    
    
        class stereotype(model.Reference):
            isNavigable = False
            _XMINames = ('Foundation.Core.ModelElement.stereotype',)
            referencedType = 'Stereotype'
            referencedEnd = 'extendedElements'
    
    
        class targetFlows(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.targetFlow',)
            referencedType = 'Flow'
            referencedEnd = 'targets'
    
    
        class taggedValues(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.taggedValue',)
            referencedType = 'TaggedValue'
            referencedEnd = 'modelElement'
    
    
        class templateParameters2(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.templateParameter2',)
            referencedType = 'TemplateParameter'
            referencedEnd = 'modelElement2'
    


        class visibility(model.Field):
            _XMINames = ('Foundation.Core.ModelElement.visibility',)
            referencedType = 'VisibilityKind'
    
        _XMINames = ('Foundation.Core.ModelElement',)
    
        class presentations(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.presentation',)
            referencedType = 'PresentationElement'
            referencedEnd = 'subjects'
    
    
        class bindings(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.binding',)
            referencedType = 'Binding'
            referencedEnd = 'arguments'
    
    
        class templateParameters(model.Sequence):
            _XMINames = ('Foundation.Core.ModelElement.templateParameter',)
            referencedType = 'TemplateParameter'
            referencedEnd = 'modelElement'
    



        class partitions(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.ModelElement.partition',)
            referencedType = 'Partition'
            referencedEnd = 'contents'
    
    
        class sourceFlows(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.sourceFlow',)
            referencedType = 'Flow'
            referencedEnd = 'sources'
    
    
        class behaviors(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.ModelElement.behavior',)
            referencedType = 'StateMachine'
            referencedEnd = 'context'
    
    
        class classifierRoles(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.ModelElement.classifierRole',)
            referencedType = 'ClassifierRole'
            referencedEnd = 'availableContents'
    


        class collaborations(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.ModelElement.collaboration',)
            referencedType = 'Collaboration'
            referencedEnd = 'constrainingElements'
    
    
        class namespace(model.Reference):
            _XMINames = ('Foundation.Core.ModelElement.namespace',)
            referencedType = 'Namespace'
            referencedEnd = 'ownedElements'
    
    
        class comments(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.comment',)
            referencedType = 'Comment'
            referencedEnd = 'annotatedElements'
    
    
        class name(model.Field):
            _XMINames = ('Foundation.Core.ModelElement.name',)
            referencedType = 'Name'
    




        class elementImports(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.elementImport',)
            referencedType = 'ElementImport'
            referencedEnd = 'modelElement'
    
    
        class supplierDependencies(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.supplierDependency',)
            referencedType = 'Dependency'
            referencedEnd = 'suppliers'
    
    
        class clientDependencies(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.clientDependency',)
            referencedType = 'Dependency'
            referencedEnd = 'clients'
    
    
        class templateParameters3(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.templateParameter3',)
            referencedType = 'TemplateParameter'
            referencedEnd = 'defaultElement'
    


        class constraints(model.Collection):
            _XMINames = ('Foundation.Core.ModelElement.constraint',)
            referencedType = 'Constraint'
            referencedEnd = 'constrainedElements'
    

    class Action(ModelElement):

        _isAbstract = 0
    
        class state3(model.Reference):
            isNavigable = False
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.state3',)
            referencedType = 'State'
            referencedEnd = 'doActivity'
    
    
        class target(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.target',)
            referencedType = 'ObjectSetExpression'
    
    
        class script(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.script',)
            referencedType = 'ActionExpression'
    


        class stimuli(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.stimulus',)
            referencedType = 'Stimulus'
            referencedEnd = 'dispatchAction'
    
    
        class transition(model.Reference):
            isNavigable = False
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.transition',)
            referencedType = 'Transition'
            referencedEnd = 'effect'
    
    
        class messages(model.Collection):
            isNavigable = False
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.message',)
            referencedType = 'Message'
            referencedEnd = 'action'
    
    
        class isAsynchronous(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.isAsynchronous',)
            referencedType = 'Boolean'
    




        class actionSequence(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.actionSequence',)
            referencedType = 'ActionSequence'
            referencedEnd = 'actions'
    
    
        class recurrence(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.recurrence',)
            referencedType = 'IterationExpression'
    
    
        class state2(model.Reference):
            isNavigable = False
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.state2',)
            referencedType = 'State'
            referencedEnd = 'exit'
    
    
        class state1(model.Reference):
            isNavigable = False
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.state1',)
            referencedType = 'State'
            referencedEnd = 'entry'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Action',)



        class actualArguments(model.Sequence):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.actualArgument',)
            referencedType = 'Argument'
            referencedEnd = 'action'
    

    class ReturnAction(Action):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.ReturnAction',)


    class PresentationElement(Element):
        _isAbstract = 1
    
        class subjects(model.Collection):
            _XMINames = ('Foundation.Core.PresentationElement.subject',)
            referencedType = 'ModelElement'
            referencedEnd = 'presentations'
    
        _XMINames = ('Foundation.Core.PresentationElement',)


    class AssociationEnd(ModelElement):
    
        class isNavigable(model.Field):
            _XMINames = ('Foundation.Core.AssociationEnd.isNavigable',)
            referencedType = 'Boolean'
    
        _isAbstract = 0
    
        class changeability(model.Field):
            _XMINames = ('Foundation.Core.AssociationEnd.changeability',)
            referencedType = 'ChangeableKind'
    
    
        class specifications(model.Collection):
            _XMINames = ('Foundation.Core.AssociationEnd.specification',)
            referencedType = 'Classifier'
            referencedEnd = 'participants'
    
    
        class multiplicity(model.Field):
            _XMINames = ('Foundation.Core.AssociationEnd.multiplicity',)
            referencedType = 'Multiplicity'
    
    
        class aggregation(model.Field):
            _XMINames = ('Foundation.Core.AssociationEnd.aggregation',)
            referencedType = 'AggregationKind'
    
    
        class ordering(model.Field):
            _XMINames = ('Foundation.Core.AssociationEnd.ordering',)
            referencedType = 'OrderingKind'
    
        class associationEndRoles(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.AssociationEnd.associationEndRole',)
            referencedType = 'AssociationEndRole'
            referencedEnd = 'base'
    
    
        class linkEnds(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.AssociationEnd.linkEnd',)
            referencedType = 'LinkEnd'
            referencedEnd = 'associationEnd'
    
    
        class targetScope(model.Field):
            _XMINames = ('Foundation.Core.AssociationEnd.targetScope',)
            referencedType = 'ScopeKind'
    
        _XMINames = ('Foundation.Core.AssociationEnd',)
    
        class type(model.Reference):
            _XMINames = ('Foundation.Core.AssociationEnd.type',)
            referencedType = 'Classifier'
            referencedEnd = 'associationEnds'
    



        class qualifiers(model.Sequence):
            _XMINames = ('Foundation.Core.AssociationEnd.qualifier',)
            referencedType = 'Attribute'
            referencedEnd = 'associationEnd'
    
    
        class association(model.Reference):
            _XMINames = ('Foundation.Core.AssociationEnd.association',)
            referencedType = 'Association'
            referencedEnd = 'connections'
    






















    class Instance(ModelElement):
    
        _isAbstract = 0
    
        class stimuli1(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.stimulus1',)
            referencedType = 'Stimulus'
            referencedEnd = 'arguments'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Instance',)
    
        class componentInstance(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.componentInstance',)
            referencedType = 'ComponentInstance'
            referencedEnd = 'residents'
    
    
        class classifiers(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.classifier',)
            referencedType = 'Classifier'
            referencedEnd = 'instances'







    
        class slots(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.slot',)
            referencedType = 'AttributeLink'
            referencedEnd = 'instance'
    
    
        class stimuli3(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.stimulus3',)
            referencedType = 'Stimulus'
            referencedEnd = 'sender'
    
    
        class attributeLinks(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.attributeLink',)
            referencedType = 'AttributeLink'
            referencedEnd = 'value'
    
    
        class linkEnds(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.linkEnd',)
            referencedType = 'LinkEnd'
            referencedEnd = 'instance'
    


        class stimuli2(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.stimulus2',)
            referencedType = 'Stimulus'
            referencedEnd = 'receiver'
    

    class UseCaseInstance(Instance):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Use_Cases.UseCaseInstance',)


    class StateVertex(ModelElement):
        _isAbstract = 1
        _XMINames = ('Behavioral_Elements.State_Machines.StateVertex',)
    
        class container(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.StateVertex.container',)
            referencedType = 'CompositeState'
            referencedEnd = 'subvertices'
    
    
        class outgoings(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.StateVertex.outgoing',)
            referencedType = 'Transition'
            referencedEnd = 'source'
    



        class incomings(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.StateVertex.incoming',)
            referencedType = 'Transition'
            referencedEnd = 'target'


    class State(StateVertex):

        _isAbstract = 0
    
        class doActivity(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.State.doActivity',)
            referencedType = 'Action'
            referencedEnd = 'state3'
    
    
        class exit(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.State.exit',)
            referencedType = 'Action'
            referencedEnd = 'state2'









        class internalTransitions(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.State.internalTransition',)
            referencedType = 'Transition'
            referencedEnd = 'state'
    
    
        class stateMachine(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.State.stateMachine',)
            referencedType = 'StateMachine'
            referencedEnd = 'top'
    
    
        class deferrableEvents(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.State.deferrableEvent',)
            referencedType = 'Event'
            referencedEnd = 'states'
    
    
        class classifiersInState(model.Collection):
            isNavigable = False
            _XMINames = ('Behavioral_Elements.State_Machines.State.classifierInState',)
            referencedType = 'ClassifierInState'
            referencedEnd = 'inStates'
    


        class entry(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.State.entry',)
            referencedType = 'Action'
            referencedEnd = 'state1'
    
        _XMINames = ('Behavioral_Elements.State_Machines.State',)


    class CompositeState(State):
        _isAbstract = 0
    
        class subvertices(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.CompositeState.subvertex',)
            referencedType = 'StateVertex'
            referencedEnd = 'container'
    
    
        class isConcurent(model.Field):
            _XMINames = ('Behavioral_Elements.State_Machines.CompositeState.isConcurent',)
            referencedType = 'Boolean'
    
        _XMINames = ('Behavioral_Elements.State_Machines.CompositeState',)








    class SubmachineState(CompositeState):
    
        _isAbstract = 0
    
        class submachine(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.SubmachineState.submachine',)
            referencedType = 'StateMachine'
            referencedEnd = 'subMachineStates'
    
        _XMINames = ('Behavioral_Elements.State_Machines.SubmachineState',)


    class SubactivityState(SubmachineState):

        _isAbstract = 0
    
        class dynamicArguments(model.Field):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.SubactivityState.dynamicArguments',)
            referencedType = 'ArgListsExpression'
    
    
        class isDynamic(model.Field):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.SubactivityState.isDynamic',)
            referencedType = 'Boolean'
    
        _XMINames = ('Behavioral_Elements.Activity_Graphs.SubactivityState',)





        class dynamicMultiplicity(model.Field):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.SubactivityState.dynamicMultiplicity',)
            referencedType = 'Multiplicity'
    


    class Relationship(ModelElement):
        _isAbstract = 0
        _XMINames = ('Foundation.Core.Relationship',)


    class Dependency(Relationship):
        _isAbstract = 0
    
        class suppliers(model.Collection):
            _XMINames = ('Foundation.Core.Dependency.supplier',)
            referencedType = 'ModelElement'
            referencedEnd = 'supplierDependencies'
    
    
        class clients(model.Collection):
            _XMINames = ('Foundation.Core.Dependency.client',)
            referencedType = 'ModelElement'
            referencedEnd = 'clientDependencies'
    
        _XMINames = ('Foundation.Core.Dependency',)




    class Usage(Dependency):
        _isAbstract = 0
        _XMINames = ('Foundation.Core.Usage',)


    class CallAction(Action):

        _isAbstract = 0
    
        class operation(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.CallAction.operation',)
            referencedType = 'Operation'
            referencedEnd = 'callActions'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.CallAction',)


    class Include(Relationship):

        _isAbstract = 0
    
        class addition(model.Reference):
            _XMINames = ('Behavioral_Elements.Use_Cases.Include.addition',)
            referencedType = 'UseCase'
            referencedEnd = 'includes'
    







        class base(model.Reference):
            _XMINames = ('Behavioral_Elements.Use_Cases.Include.base',)
            referencedType = 'UseCase'
            referencedEnd = 'includes2'
    
        _XMINames = ('Behavioral_Elements.Use_Cases.Include',)


    class Feature(ModelElement):

        _isAbstract = 1
    
        class owner(model.Reference):
            _XMINames = ('Foundation.Core.Feature.owner',)
            referencedType = 'Classifier'
            referencedEnd = 'features'
    
        _XMINames = ('Foundation.Core.Feature',)
    
        class ownerScope(model.Field):
            _XMINames = ('Foundation.Core.Feature.ownerScope',)
            referencedType = 'ScopeKind'
    







        class classifierRoles(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Feature.classifierRole',)
            referencedType = 'ClassifierRole'
            referencedEnd = 'availableFeatures'


    class BehavioralFeature(Feature):
        _isAbstract = 1
    
        class isQuery(model.Field):
            _XMINames = ('Foundation.Core.BehavioralFeature.isQuery',)
            referencedType = 'Boolean'
    
        _XMINames = ('Foundation.Core.BehavioralFeature',)
    
        class raisedSignals(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.BehavioralFeature.raisedSignal',)
            referencedType = 'Signal'
            referencedEnd = 'contexts'
    
    
        class parameters(model.Sequence):
            _XMINames = ('Foundation.Core.BehavioralFeature.parameter',)
            referencedType = 'Parameter'
            referencedEnd = 'behavioralFeature'
    
    class Method(BehavioralFeature):
    
        class body(model.Field):
            _XMINames = ('Foundation.Core.Method.body',)
            referencedType = 'ProcedureExpression'
    
        _isAbstract = 0
    
        class specification(model.Reference):
            _XMINames = ('Foundation.Core.Method.specification',)
            referencedType = 'Operation'
            referencedEnd = 'methods'
    
        _XMINames = ('Foundation.Core.Method',)




















    class GeneralizableElement(ModelElement):

        _isAbstract = 1

        _XMINames = ('Foundation.Core.GeneralizableElement',)
    
        class isRoot(model.Field):
            _XMINames = ('Foundation.Core.GeneralizableElement.isRoot',)
            referencedType = 'Boolean'

        class isAbstract(model.Field):
            _XMINames = ('Foundation.Core.GeneralizableElement.isAbstract',)
            referencedType = 'Boolean'
    
        class generalizations(model.Collection):
            _XMINames = ('Foundation.Core.GeneralizableElement.generalization',)
            referencedType = 'Generalization'
            referencedEnd = 'child'
    
    
        class specializations(model.Collection):
            _XMINames = ('Foundation.Core.GeneralizableElement.specialization',)
            referencedType = 'Generalization'
            referencedEnd = 'parent'
    


        class isLeaf(model.Field):
            _XMINames = ('Foundation.Core.GeneralizableElement.isLeaf',)
            referencedType = 'Boolean'
    


    class Namespace(ModelElement):

        _isAbstract = 0

        _XMINames = ('Foundation.Core.Namespace',)
    
        class ownedElements(model.Collection):
            _XMINames = ('Foundation.Core.Namespace.ownedElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'namespace'




    class Classifier(GeneralizableElement,Namespace):

        _isAbstract = 0
    
        class structuralFeatures(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.structuralFeature',)
            referencedType = 'StructuralFeature'
            referencedEnd = 'type'
    
    
        class features(model.Sequence):
            _XMINames = ('Foundation.Core.Classifier.feature',)
            referencedType = 'Feature'
            referencedEnd = 'owner'
    
    
        class parameters(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.parameter',)
            referencedType = 'Parameter'
            referencedEnd = 'type'
    
    
        class objectFlowStates(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.objectFlowState',)
            referencedType = 'ObjectFlowState'
            referencedEnd = 'type'
    
    
        class classifiersInState(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.classifierInState',)
            referencedType = 'ClassifierInState'
            referencedEnd = 'type'
    


        class participants(model.Collection):
            _XMINames = ('Foundation.Core.Classifier.participant',)
            referencedType = 'AssociationEnd'
            referencedEnd = 'specifications'
    

        class associationEnds(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.associationEnd',)
            referencedType = 'AssociationEnd'
            referencedEnd = 'type'
    
    
        class collaborations(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.collaboration',)
            referencedType = 'Collaboration'
            referencedEnd = 'representedClassifier'
    
    
        class powertypeRanges(model.Collection):
            _XMINames = ('Foundation.Core.Classifier.powertypeRange',)
            referencedType = 'Generalization'
            referencedEnd = 'powertype'
    
        _XMINames = ('Foundation.Core.Classifier',)
    
        class createActions(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.createAction',)
            referencedType = 'CreateAction'
            referencedEnd = 'instantiation'
    
    
        class instances(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.instance',)
            referencedType = 'Instance'
            referencedEnd = 'classifiers'
    
    
        class classifierRoles(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Classifier.classifierRole',)
            referencedType = 'ClassifierRole'
            referencedEnd = 'bases'
    












    class Node(Classifier):
        _isAbstract = 0
    
        class residents(model.Collection):
            _XMINames = ('Foundation.Core.Node.resident',)
            referencedType = 'Component'
            referencedEnd = 'deploymentLocations'
    
        _XMINames = ('Foundation.Core.Node',)



    class Association(GeneralizableElement,Relationship):

        _isAbstract = 0
    
        class connections(model.Sequence):
            _XMINames = ('Foundation.Core.Association.connection',)
            referencedType = 'AssociationEnd'
            referencedEnd = 'association'
    
        _XMINames = ('Foundation.Core.Association',)
    
        class associationRoles(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Association.associationRole',)
            referencedType = 'AssociationRole'
            referencedEnd = 'base'
    
    
        class links(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Association.link',)
            referencedType = 'Link'
            referencedEnd = 'association'


    class Class(Classifier):

        _isAbstract = 0

        _XMINames = ('Foundation.Core.Class',)
    
        class isActive(model.Field):
            _XMINames = ('Foundation.Core.Class.isActive',)
            referencedType = 'Boolean'
    


















    class AssociationClass(Association,Class):
        _isAbstract = 0
        _XMINames = ('Foundation.Core.AssociationClass',)


    class Stimulus(ModelElement):

        _isAbstract = 0

        _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus',)
    
        class sender(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.sender',)
            referencedType = 'Instance'
            referencedEnd = 'stimuli3'


        class receiver(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.receiver',)
            referencedType = 'Instance'
            referencedEnd = 'stimuli2'
    
    
        class arguments(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.argument',)
            referencedType = 'Instance'
            referencedEnd = 'stimuli1'
    
    
        class dispatchAction(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.dispatchAction',)
            referencedType = 'Action'
            referencedEnd = 'stimuli'
    
    
        class communicationLink(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.communicationLink',)
            referencedType = 'Link'
            referencedEnd = 'stimuli'
    






















    class StateMachine(ModelElement):

        _isAbstract = 0
    
        class transitionses(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.StateMachine.transitions',)
            referencedType = 'Transition'
            referencedEnd = 'stateMachine'
    
        _XMINames = ('Behavioral_Elements.State_Machines.StateMachine',)
    
        class context(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.StateMachine.context',)
            referencedType = 'ModelElement'
            referencedEnd = 'behaviors'
    
    
        class top(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.StateMachine.top',)
            referencedType = 'State'
            referencedEnd = 'stateMachine'
    







        class subMachineStates(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.StateMachine.subMachineState',)
            referencedType = 'SubmachineState'
            referencedEnd = 'submachine'


    class Event(ModelElement):

        _isAbstract = 1
    
        class states(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.Event.state',)
            referencedType = 'State'
            referencedEnd = 'deferrableEvents'
    
    
        class transitions(model.Collection):
            _XMINames = ('Behavioral_Elements.State_Machines.Event.transition',)
            referencedType = 'Transition'
            referencedEnd = 'trigger'
    
        _XMINames = ('Behavioral_Elements.State_Machines.Event',)







        class parameters(model.Sequence):
            _XMINames = ('Behavioral_Elements.State_Machines.Event.parameter',)
            referencedType = 'Parameter'
            referencedEnd = 'event'


    class TimeEvent(Event):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.TimeEvent',)
    
        class when(model.Field):
            _XMINames = ('Behavioral_Elements.State_Machines.TimeEvent.when',)
            referencedType = 'TimeExpression'


    class Object(Instance):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.Object',)


    class TerminateAction(Action):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.TerminateAction',)











    class ElementImport(Base):

        _isAbstract = 0
    
        class alias(model.Field):
            _XMINames = ('Model_Management.ElementImport.alias',)
            referencedType = 'Name'
    
        _XMINames = ('Model_Management.ElementImport',)
    
        class package(model.Reference):
            _XMINames = ('Model_Management.ElementImport.package',)
            referencedType = 'Package'
            referencedEnd = 'elementImports'
    
    
        class modelElement(model.Reference):
            _XMINames = ('Model_Management.ElementImport.modelElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'elementImports'
    

        class visibility(model.Field):
            _XMINames = ('Model_Management.ElementImport.visibility',)
            referencedType = 'VisibilityKind'


    class DestroyAction(Action):

        _isAbstract = 0

        _XMINames = ('Behavioral_Elements.Common_Behavior.DestroyAction',)


    class ClassifierInState(Classifier):

        _isAbstract = 0
    
        class type(model.Reference):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ClassifierInState.type',)
            referencedType = 'Classifier'
            referencedEnd = 'classifiersInState'
    
    
        class inStates(model.Collection):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ClassifierInState.inState',)
            referencedType = 'State'
            referencedEnd = 'classifiersInState'
    
        _XMINames = ('Behavioral_Elements.Activity_Graphs.ClassifierInState',)










    class NodeInstance(Instance):

        _isAbstract = 0
    
        class residents(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.NodeInstance.resident',)
            referencedType = 'ComponentInstance'
            referencedEnd = 'nodeInstance'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.NodeInstance',)


    class Signal(Classifier):

        _isAbstract = 0
    
        class receptions(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Signal.reception',)
            referencedType = 'Reception'
            referencedEnd = 'signal'
    
    
        class occurrences(model.Collection):
            isNavigable = False
            _XMINames = ('Behavioral_Elements.Common_Behavior.Signal.occurrence',)
            referencedType = 'SignalEvent'
            referencedEnd = 'signal'
    


        class contexts(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Signal.context',)
            referencedType = 'BehavioralFeature'
            referencedEnd = 'raisedSignals'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Signal',)
    
        class sendActions(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Signal.sendAction',)
            referencedType = 'SendAction'
            referencedEnd = 'signal'
    

    class Exception(Signal):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.Exception',)


    class SimpleState(State):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.SimpleState',)












    class ObjectFlowState(SimpleState):

        _isAbstract = 0

        _XMINames = ('Behavioral_Elements.Activity_Graphs.ObjectFlowState',)
    
        class isSynch(model.Field):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ObjectFlowState.isSynch',)
            referencedType = 'Boolean'
    
    
        class parameters(model.Collection):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ObjectFlowState.parameter',)
            referencedType = 'Parameter'
            referencedEnd = 'states'
    
    
        class type(model.Reference):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ObjectFlowState.type',)
            referencedType = 'Classifier'
            referencedEnd = 'objectFlowStates'
    








    class Constraint(ModelElement):
    
        class body(model.Field):
            _XMINames = ('Foundation.Core.Constraint.body',)
            referencedType = 'BooleanExpression'
    
        _isAbstract = 0
        _XMINames = ('Foundation.Core.Constraint',)
    
        class constrainedElement2(model.Reference):
            isNavigable = False
            _XMINames = ('Foundation.Core.Constraint.constrainedElement2',)
            referencedType = 'Stereotype'
            referencedEnd = 'stereotypeConstraints'
    
    
        class constrainedElements(model.Sequence):
            _XMINames = ('Foundation.Core.Constraint.constrainedElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'constraints'
    










    class Transition(ModelElement):

        _isAbstract = 0
    
        class source(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.source',)
            referencedType = 'StateVertex'
            referencedEnd = 'outgoings'
    
    
        class guard(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.guard',)
            referencedType = 'Guard'
            referencedEnd = 'transition'


        class trigger(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.trigger',)
            referencedType = 'Event'
            referencedEnd = 'transitions'
    
        _XMINames = ('Behavioral_Elements.State_Machines.Transition',)







        class target(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.target',)
            referencedType = 'StateVertex'
            referencedEnd = 'incomings'
    
    
        class stateMachine(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.stateMachine',)
            referencedType = 'StateMachine'
            referencedEnd = 'transitionses'
    
    
        class state(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.state',)
            referencedType = 'State'
            referencedEnd = 'internalTransitions'
    
    
        class effect(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.effect',)
            referencedType = 'Action'
            referencedEnd = 'transition'
   


    class Flow(Relationship):

        _isAbstract = 0
    
        class sources(model.Collection):
            _XMINames = ('Foundation.Core.Flow.source',)
            referencedType = 'ModelElement'
            referencedEnd = 'sourceFlows'
    
        _XMINames = ('Foundation.Core.Flow',)
    
        class targets(model.Collection):
            _XMINames = ('Foundation.Core.Flow.target',)
            referencedType = 'ModelElement'
            referencedEnd = 'targetFlows'
    

















    class StructuralFeature(Feature):

        _isAbstract = 1

        _XMINames = ('Foundation.Core.StructuralFeature',)
    
        class targetScope(model.Field):
            _XMINames = ('Foundation.Core.StructuralFeature.targetScope',)
            referencedType = 'ScopeKind'
    
    
        class changeability(model.Field):
            _XMINames = ('Foundation.Core.StructuralFeature.changeability',)
            referencedType = 'ChangeableKind'
    
    
        class multiplicity(model.Field):
            _XMINames = ('Foundation.Core.StructuralFeature.multiplicity',)
            referencedType = 'Multiplicity'
    
    
        class type(model.Reference):
            _XMINames = ('Foundation.Core.StructuralFeature.type',)
            referencedType = 'Classifier'
            referencedEnd = 'structuralFeatures'
    


    class UseCase(Classifier):

        _isAbstract = 0
    
        class extends2(model.Collection):
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.extend2',)
            referencedType = 'Extend'
            referencedEnd = 'base'
    
    
        class extends(model.Collection):
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.extend',)
            referencedType = 'Extend'
            referencedEnd = 'extension'
    
    
        class extensionPoints(model.Collection):
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.extensionPoint',)
            referencedType = 'ExtensionPoint'
            referencedEnd = 'useCase'
    
        _XMINames = ('Behavioral_Elements.Use_Cases.UseCase',)







        class includes2(model.Collection):
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.include2',)
            referencedType = 'Include'
            referencedEnd = 'base'
    
    
        class includes(model.Collection):
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.include',)
            referencedType = 'Include'
            referencedEnd = 'addition'
    

    class Actor(Classifier):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Use_Cases.Actor',)


















    class AttributeLink(ModelElement):

        _isAbstract = 0
    
        class linkEnd(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink.linkEnd',)
            referencedType = 'LinkEnd'
            referencedEnd = 'qualifiedValues'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink',)
    
        class instance(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink.instance',)
            referencedType = 'Instance'
            referencedEnd = 'slots'
    
    
        class attribute(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink.attribute',)
            referencedType = 'Attribute'
            referencedEnd = 'attributeLinks'
    







        class value(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink.value',)
            referencedType = 'Instance'
            referencedEnd = 'attributeLinks'
    


    class SignalEvent(Event):
        _isAbstract = 0
    
        class signal(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.SignalEvent.signal',)
            referencedType = 'Signal'
            referencedEnd = 'occurrences'
    
        _XMINames = ('Behavioral_Elements.State_Machines.SignalEvent',)


    class Package(GeneralizableElement,Namespace):
        _isAbstract = 0
    
        class elementImports(model.Collection):
            _XMINames = ('Model_Management.Package.elementImport',)
            referencedType = 'ElementImport'
            referencedEnd = 'package'
    
        _XMINames = ('Model_Management.Package',)


    class Subsystem(Package,Classifier):

        _isAbstract = 0

        _XMINames = ('Model_Management.Subsystem',)
    
        class isInstantiable(model.Field):
            _XMINames = ('Model_Management.Subsystem.isInstantiable',)
            referencedType = 'Boolean'
    


    class CallEvent(Event):

        _isAbstract = 0
    
        class operation(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.CallEvent.operation',)
            referencedType = 'Operation'
            referencedEnd = 'occurrences'
    
        _XMINames = ('Behavioral_Elements.State_Machines.CallEvent',)











    class Attribute(StructuralFeature):

        _isAbstract = 0
    
        class initialValue(model.Field):
            _XMINames = ('Foundation.Core.Attribute.initialValue',)
            referencedType = 'Expression'
        
        class associationEndRoles(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Attribute.associationEndRole',)
            referencedType = 'AssociationEndRole'
            referencedEnd = 'availableQualifiers'
    
        _XMINames = ('Foundation.Core.Attribute',)
    
        class associationEnd(model.Reference):
            _XMINames = ('Foundation.Core.Attribute.associationEnd',)
            referencedType = 'AssociationEnd'
            referencedEnd = 'qualifiers'
        
        class attributeLinks(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Attribute.attributeLink',)
            referencedType = 'AttributeLink'
            referencedEnd = 'attribute'
    

    class StubState(StateVertex):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.StubState',)
    
        class referenceState(model.Field):
            _XMINames = ('Behavioral_Elements.State_Machines.StubState.referenceState',)
            referencedType = 'Name'
    


    class AssociationEndRole(AssociationEnd):

        _isAbstract = 0
    
        class availableQualifiers(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationEndRole.availableQualifier',)
            referencedType = 'Attribute'
            referencedEnd = 'associationEndRoles'

    
        class base(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationEndRole.base',)
            referencedType = 'AssociationEnd'
            referencedEnd = 'associationEndRoles'
    
        _XMINames = ('Behavioral_Elements.Collaborations.AssociationEndRole',)




    class SynchState(StateVertex):

        _isAbstract = 0

        _XMINames = ('Behavioral_Elements.State_Machines.SynchState',)
    
        class bound(model.Field):
            _XMINames = ('Behavioral_Elements.State_Machines.SynchState.bound',)
            referencedType = 'UnlimitedInteger'


    class FinalState(State):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.FinalState',)


    class Link(ModelElement):

        _isAbstract = 0
    
        class connections(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Link.connection',)
            referencedType = 'LinkEnd'
            referencedEnd = 'link'
    
        class stimuli(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Link.stimulus',)
            referencedType = 'Stimulus'
            referencedEnd = 'communicationLink'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Link',)
    
        class association(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Link.association',)
            referencedType = 'Association'
            referencedEnd = 'links'


    class LinkObject(Object,Link):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.LinkObject',)


    class Operation(BehavioralFeature):

        _isAbstract = 0
    
        class collaborations(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Operation.collaboration',)
            referencedType = 'Collaboration'
            referencedEnd = 'representedOperation'
    
        class callActions(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Operation.callAction',)
            referencedType = 'CallAction'
            referencedEnd = 'operation'
    
        _XMINames = ('Foundation.Core.Operation',)
    
        class methods(model.Collection):
            _XMINames = ('Foundation.Core.Operation.method',)
            referencedType = 'Method'
            referencedEnd = 'specification'
        
        class concurrency(model.Field):
            _XMINames = ('Foundation.Core.Operation.concurrency',)
            referencedType = 'CallConcurrencyKind'
    
        class isRoot(model.Field):
            _XMINames = ('Foundation.Core.Operation.isRoot',)
            referencedType = 'Boolean'
    
    
        class specification(model.Field):
            _XMINames = ('Foundation.Core.Operation.specification',)
            referencedType = 'String'
    
    
        class isLeaf(model.Field):
            _XMINames = ('Foundation.Core.Operation.isLeaf',)
            referencedType = 'Boolean'
    


        class occurrences(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Operation.occurrence',)
            referencedType = 'CallEvent'
            referencedEnd = 'operation'
    


    class ActionState(SimpleState):
        _isAbstract = 0
    
        class dynamicArguments(model.Field):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ActionState.dynamicArguments',)
            referencedType = 'ArgListsExpression'
    
    
        class isDynamic(model.Field):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ActionState.isDynamic',)
            referencedType = 'Boolean'
    
        _XMINames = ('Behavioral_Elements.Activity_Graphs.ActionState',)
    
        class dynamicMultiplicity(model.Field):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ActionState.dynamicMultiplicity',)
            referencedType = 'Multiplicity'
    



    class SendAction(Action):
        _isAbstract = 0
    
        class signal(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.SendAction.signal',)
            referencedType = 'Signal'
            referencedEnd = 'sendActions'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.SendAction',)


    class ElementResidence(Base):

        _isAbstract = 0
    
        class resident(model.Reference):
            _XMINames = ('Foundation.Core.ElementResidence.resident',)
            referencedType = 'ModelElement'
            referencedEnd = 'elementResidences'
    
        _XMINames = ('Foundation.Core.ElementResidence',)
    
        class implementationLocation(model.Reference):
            _XMINames = ('Foundation.Core.ElementResidence.implementationLocation',)
            referencedType = 'Component'
            referencedEnd = 'residentElements'
    


        class visibility(model.Field):
            _XMINames = ('Foundation.Core.ElementResidence.visibility',)
            referencedType = 'VisibilityKind'
    

    class Binding(Dependency):

        _isAbstract = 0

        _XMINames = ('Foundation.Core.Binding',)
    
        class arguments(model.Sequence):
            _XMINames = ('Foundation.Core.Binding.argument',)
            referencedType = 'ModelElement'
            referencedEnd = 'bindings'
    


    class TemplateParameter(Base):
        _isAbstract = 0
    
        class modelElement(model.Reference):
            _XMINames = ('Foundation.Core.TemplateParameter.modelElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'templateParameters'
    




        class defaultElement(model.Reference):
            _XMINames = ('Foundation.Core.TemplateParameter.defaultElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'templateParameters3'
    
        _XMINames = ('Foundation.Core.TemplateParameter',)
    
        class modelElement2(model.Reference):
            _XMINames = ('Foundation.Core.TemplateParameter.modelElement2',)
            referencedType = 'ModelElement'
            referencedEnd = 'templateParameters2'
    


    class ActionSequence(Action):

        _isAbstract = 0

        _XMINames = ('Behavioral_Elements.Common_Behavior.ActionSequence',)
    
        class actions(model.Sequence):
            _XMINames = ('Behavioral_Elements.Common_Behavior.ActionSequence.action',)
            referencedType = 'Action'
            referencedEnd = 'actionSequence'
    




    class Parameter(ModelElement):

        _isAbstract = 0
    
        class states(model.Collection):
            isNavigable = False
            _XMINames = ('Foundation.Core.Parameter.state',)
            referencedType = 'ObjectFlowState'
            referencedEnd = 'parameters'
    
        class kind(model.Field):
            _XMINames = ('Foundation.Core.Parameter.kind',)
            referencedType = 'ParameterDirectionKind'
    
        _XMINames = ('Foundation.Core.Parameter',)
    
        class behavioralFeature(model.Reference):
            _XMINames = ('Foundation.Core.Parameter.behavioralFeature',)
            referencedType = 'BehavioralFeature'
            referencedEnd = 'parameters'
    
    
        class defaultValue(model.Field):
            _XMINames = ('Foundation.Core.Parameter.defaultValue',)
            referencedType = 'Expression'
    


        class type(model.Reference):
            _XMINames = ('Foundation.Core.Parameter.type',)
            referencedType = 'Classifier'
            referencedEnd = 'parameters'

        class event(model.Reference):
            isNavigable = False
            _XMINames = ('Foundation.Core.Parameter.event',)
            referencedType = 'Event'
            referencedEnd = 'parameters'
    
    class ExtensionPoint(ModelElement):

        _isAbstract = 0
    
        class extends(model.Collection):
            _XMINames = ('Behavioral_Elements.Use_Cases.ExtensionPoint.extend',)
            referencedType = 'Extend'
            referencedEnd = 'extensionPoints'
    
    
        class useCase(model.Reference):
            _XMINames = ('Behavioral_Elements.Use_Cases.ExtensionPoint.useCase',)
            referencedType = 'UseCase'
            referencedEnd = 'extensionPoints'
    
        _XMINames = ('Behavioral_Elements.Use_Cases.ExtensionPoint',)

        class location(model.Field):
            _XMINames = ('Behavioral_Elements.Use_Cases.ExtensionPoint.location',)
            referencedType = 'LocationReference'


    class ComponentInstance(Instance):
        _isAbstract = 0
    
        class nodeInstance(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.ComponentInstance.nodeInstance',)
            referencedType = 'NodeInstance'
            referencedEnd = 'residents'
    
    
        class residents(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.ComponentInstance.resident',)
            referencedType = 'Instance'
            referencedEnd = 'componentInstance'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.ComponentInstance',)








    class Abstraction(Dependency):

        _isAbstract = 0
        _XMINames = ('Foundation.Core.Abstraction',)
    
        class mapping(model.Field):
            _XMINames = ('Foundation.Core.Abstraction.mapping',)
            referencedType = 'MappingExpression'    



    class Permission(Dependency):
        _isAbstract = 0
        _XMINames = ('Foundation.Core.Permission',)


    class Collaboration(Namespace,GeneralizableElement):

        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Collaborations.Collaboration',)
    
        class representedClassifier(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Collaboration.representedClassifier',)
            referencedType = 'Classifier'
            referencedEnd = 'collaborations'









        class interactions(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.Collaboration.interaction',)
            referencedType = 'Interaction'
            referencedEnd = 'context'
    
    
        class representedOperation(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Collaboration.representedOperation',)
            referencedType = 'Operation'
            referencedEnd = 'collaborations'
    
    
        class constrainingElements(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.Collaboration.constrainingElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'collaborations'













    class Component(Classifier):

        _isAbstract = 0
    
        class deploymentLocations(model.Collection):
            _XMINames = ('Foundation.Core.Component.deploymentLocation',)
            referencedType = 'Node'
            referencedEnd = 'residents'
    
    
        class residentElements(model.Collection):
            _XMINames = ('Foundation.Core.Component.residentElement',)
            referencedType = 'ElementResidence'
            referencedEnd = 'implementationLocation'
    
        _XMINames = ('Foundation.Core.Component',)



    class CallState(ActionState):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Activity_Graphs.CallState',)











    class ClassifierRole(Classifier):
        _isAbstract = 0
    
        class bases(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.base',)
            referencedType = 'Classifier'
            referencedEnd = 'classifierRoles'
    
    
        class messages1(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.message1',)
            referencedType = 'Message'
            referencedEnd = 'receiver'
    
    
        class multiplicity(model.Field):
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.multiplicity',)
            referencedType = 'Multiplicity'
    
        _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole',)
    
        class messages2(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.message2',)
            referencedType = 'Message'
            referencedEnd = 'sender'
    
        class availableFeatures(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.availableFeature',)
            referencedType = 'Feature'
            referencedEnd = 'classifierRoles'
    
    
        class availableContents(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.availableContents',)
            referencedType = 'ModelElement'
            referencedEnd = 'classifierRoles'



    class UninterpretedAction(Action):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.UninterpretedAction',)


    class AssociationRole(Association):
        _isAbstract = 0
    
        class multiplicity(model.Field):
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationRole.multiplicity',)
            referencedType = 'Multiplicity'
    





        class base(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationRole.base',)
            referencedType = 'Association'
            referencedEnd = 'associationRoles'
    
        _XMINames = ('Behavioral_Elements.Collaborations.AssociationRole',)
    
        class messages(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationRole.message',)
            referencedType = 'Message'
            referencedEnd = 'communicationConnection'

    class Interface(Classifier):
        _isAbstract = 0
        _XMINames = ('Foundation.Core.Interface',)



    class Interaction(ModelElement):
        _isAbstract = 0
    
        class messages(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.Interaction.message',)
            referencedType = 'Message'
            referencedEnd = 'interaction'
    
        _XMINames = ('Behavioral_Elements.Collaborations.Interaction',)
    

        class context(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Interaction.context',)
            referencedType = 'Collaboration'
            referencedEnd = 'interactions'


    class ChangeEvent(Event):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.ChangeEvent',)
    
        class changeExpression(model.Field):
            _XMINames = ('Behavioral_Elements.State_Machines.ChangeEvent.changeExpression',)
            referencedType = 'BooleanExpression'


    class Extension(Base):
        _isAbstract = 0
        _XMINames = ('Extension',)
    
        class extenderID(model.Field):
            _XMINames = ('Extension.extenderID',)
            referencedType = 'String'
    
    
        class extender(model.Field):
            _XMINames = ('Extension.extender',)
            referencedType = 'String'
    
        class baseElement(model.Reference):
            _XMINames = ('Extension.baseElement',)
            referencedType = 'Base'
            referencedEnd = 'extensions'
    

    class ActivityGraph(StateMachine):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Activity_Graphs.ActivityGraph',)
    
        class partitions(model.Collection):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ActivityGraph.partition',)
            referencedType = 'Partition'
            referencedEnd = 'activityGraph'
    

    class Partition(ModelElement):

        _isAbstract = 0
    
        class activityGraph(model.Reference):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.Partition.activityGraph',)
            referencedType = 'ActivityGraph'
            referencedEnd = 'partitions'
    
        _XMINames = ('Behavioral_Elements.Activity_Graphs.Partition',)



        class contents(model.Collection):
            _XMINames = ('Behavioral_Elements.Activity_Graphs.Partition.contents',)
            referencedType = 'ModelElement'
            referencedEnd = 'partitions'

    class Pseudostate(StateVertex):

        _isAbstract = 0
    
        class kind(model.Field):
            _XMINames = ('Behavioral_Elements.State_Machines.Pseudostate.kind',)
            referencedType = 'PseudostateKind'
    
        _XMINames = ('Behavioral_Elements.State_Machines.Pseudostate',)




    class CreateAction(Action):

        _isAbstract = 0
    
        class instantiation(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.CreateAction.instantiation',)
            referencedType = 'Classifier'
            referencedEnd = 'createActions'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.CreateAction',)


    class Reception(BehavioralFeature):

        _isAbstract = 0
    
        class isAbstarct(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.isAbstarct',)
            referencedType = 'Boolean'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Reception',)
    
        class isRoot(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.isRoot',)
            referencedType = 'Boolean'





    
        class specification(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.specification',)
            referencedType = 'String'

        class signal(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.signal',)
            referencedType = 'Signal'
            referencedEnd = 'receptions'
    
        class isLeaf(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.isLeaf',)
            referencedType = 'Boolean'


    class Model(Package):
        _isAbstract = 0
        _XMINames = ('Model_Management.Model',)






























    class Comment(ModelElement):

        _isAbstract = 0

        _XMINames = ('Foundation.Core.Comment',)
    
        class annotatedElements(model.Collection):
            _XMINames = ('Foundation.Core.Comment.annotatedElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'comments'
    

    class LinkEnd(ModelElement):

        _isAbstract = 0
    
        class instance(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd.instance',)
            referencedType = 'Instance'
            referencedEnd = 'linkEnds'
    
    
        class qualifiedValues(model.Collection):
            _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd.qualifiedValue',)
            referencedType = 'AttributeLink'
            referencedEnd = 'linkEnd'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd',)
    
        class link(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd.link',)
            referencedType = 'Link'
            referencedEnd = 'connections'
    
    
        class associationEnd(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd.associationEnd',)
            referencedType = 'AssociationEnd'
            referencedEnd = 'linkEnds'























    class Extend(Relationship):

        _isAbstract = 0
    
        class base(model.Reference):
            _XMINames = ('Behavioral_Elements.Use_Cases.Extend.base',)
            referencedType = 'UseCase'
            referencedEnd = 'extends2'
    
        _XMINames = ('Behavioral_Elements.Use_Cases.Extend',)
    
        class extensionPoints(model.Sequence):
            _XMINames = ('Behavioral_Elements.Use_Cases.Extend.extensionPoint',)
            referencedType = 'ExtensionPoint'
            referencedEnd = 'extends'
    
    
        class extension(model.Reference):
            _XMINames = ('Behavioral_Elements.Use_Cases.Extend.extension',)
            referencedType = 'UseCase'
            referencedEnd = 'extends'
    
        class condition(model.Field):
            _XMINames = ('Behavioral_Elements.Use_Cases.Extend.condition',)
            referencedType = 'BooleanExpression'
    
    class DataType(Classifier):
        _isAbstract = 0
        _XMINames = ('Foundation.Core.DataType',)


    class Argument(ModelElement):
        _isAbstract = 0
    
        class action(model.Reference):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Argument.action',)
            referencedType = 'Action'
            referencedEnd = 'actualArguments'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Argument',)
    
        class value(model.Field):
            _XMINames = ('Behavioral_Elements.Common_Behavior.Argument.value',)
            referencedType = 'Expression'
















    class Generalization(Relationship):

        _isAbstract = 0
    
        class powertype(model.Reference):
            _XMINames = ('Foundation.Core.Generalization.powertype',)
            referencedType = 'Classifier'
            referencedEnd = 'powertypeRanges'
    
        _XMINames = ('Foundation.Core.Generalization',)
    
        class parent(model.Reference):
            _XMINames = ('Foundation.Core.Generalization.parent',)
            referencedType = 'GeneralizableElement'
            referencedEnd = 'specializations'
    
    
        class child(model.Reference):
            _XMINames = ('Foundation.Core.Generalization.child',)
            referencedType = 'GeneralizableElement'
            referencedEnd = 'generalizations'    
    
        class discriminator(model.Field):
            _XMINames = ('Foundation.Core.Generalization.discriminator',)
            referencedType = 'Name'
    
    class Stereotype(GeneralizableElement):

        _isAbstract = 0
    
        class extendedElements(model.Collection):
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.extendedElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'stereotype'
    
        _XMINames = ('Foundation.Extension_Mechanisms.Stereotype',)
    
        class stereotypeConstraints(model.Collection):
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.stereotypeConstraint',)
            referencedType = 'Constraint'
            referencedEnd = 'constrainedElement2'
    
    
        class icon(model.Field):
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.icon',)
            referencedType = 'Geometry'
    
    
        class baseClass(model.Field):
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.baseClass',)
            referencedType = 'Name'
    
    
        class requiredTags(model.Collection):
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.requiredTag',)
            referencedType = 'TaggedValue'
            referencedEnd = 'stereotype'
    

    class Guard(ModelElement):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.Guard',)
    
        class transition(model.Reference):
            _XMINames = ('Behavioral_Elements.State_Machines.Guard.transition',)
            referencedType = 'Transition'
            referencedEnd = 'guard'
    
    
        class expression(model.Field):
            _XMINames = ('Behavioral_Elements.State_Machines.Guard.expression',)
            referencedType = 'BooleanExpression'
    










    class TaggedValue(Element):

        _isAbstract = 0
    
        class tag(model.Field):
            _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue.tag',)
            referencedType = 'Name'
    
        _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue',)
    
        class stereotype(model.Reference):
            _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue.stereotype',)
            referencedType = 'Stereotype'
            referencedEnd = 'requiredTags'
    
    
        class modelElement(model.Reference):
            _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue.modelElement',)
            referencedType = 'ModelElement'
            referencedEnd = 'taggedValues'
    
    
        class value(model.Field):
            _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue.value',)
            referencedType = 'String'
    

    class Message(ModelElement):

        _isAbstract = 0
    
        class interaction(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.interaction',)
            referencedType = 'Interaction'
            referencedEnd = 'messages'
        
        class sender(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.sender',)
            referencedType = 'ClassifierRole'
            referencedEnd = 'messages2'    
    
        class messages4(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.message4',)
            referencedType = 'Message'
            referencedEnd = 'activator'
    
        class communicationConnection(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.communicationConnection',)
            referencedType = 'AssociationRole'
            referencedEnd = 'messages'


        _XMINames = ('Behavioral_Elements.Collaborations.Message',)
    
        class messages3(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.message3',)
            referencedType = 'Message'
            referencedEnd = 'predecessors'
    
    
        class receiver(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.receiver',)
            referencedType = 'ClassifierRole'
            referencedEnd = 'messages1'
    
    
        class activator(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.activator',)
            referencedType = 'Message'
            referencedEnd = 'messages4'
    
    
        class action(model.Reference):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.action',)
            referencedType = 'Action'
            referencedEnd = 'messages'
    
        class predecessors(model.Collection):
            _XMINames = ('Behavioral_Elements.Collaborations.Message.predecessor',)
            referencedType = 'Message'
            referencedEnd = 'messages3'
    


    class DataValue(Instance):
        _isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.DataValue',)


config.setupModule()


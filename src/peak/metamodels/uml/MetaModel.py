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
    TransWarp.

    Oh, one item of note for the user...  in the enumerations and
    element/feature names, Python reserved words have had an '_' appended;
    so 'return' becomes 'return_' and 'in' becomes 'in_'.
"""

from peak.api import *


# XXX The generator rewrite really should sort simple attributes to be defined
# XXX before nested classes; the code will be much more readable that way.











class UMLClass:

    class Expression(model.DataType):
    
        class body(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Data_Types.Expression.body'
            _XMINames = ('Foundation.Data_Types.Expression.body',)
            name = 'body'
            referencedType = 'String'
    
        _XMINames = ('Foundation.Data_Types.Expression',)
    
        class language(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Data_Types.Expression.language'
            _XMINames = ('Foundation.Data_Types.Expression.language',)
            name = 'language'
            referencedType = 'Name'
    


    class TimeExpression(Expression):
        _XMINames = ('Foundation.Data_Types.TimeExpression',)


    class VisibilityKind(model.Enumeration):
        protected = 'protected'
        _XMINames = ('Foundation.Data_Types.VisibilityKind',)
        public = 'public'
        private = 'private'










    class Base(model.Element):
        isAbstract = 1
    
        class extensions(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Base.extension',)
            name = 'extensions'
            referencedType = 'Extension'
            refTypeQN = 'Base.extension'
            referencedEnd = 'baseElement'
    
        _XMINames = ('Base',)


    class Element(Base):
        isAbstract = 1
        _XMINames = ('Foundation.Core.Element',)


    class ModelElement(Element):
    
        class isSpecification(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.ModelElement.isSpecification'
            _XMINames = ('Foundation.Core.ModelElement.isSpecification',)
            name = 'isSpecification'
            referencedType = 'Boolean'
    
        isAbstract = 1
    
        class elementResidences(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.elementResidence',)
            name = 'elementResidences'
            referencedType = 'ElementResidence'
            refTypeQN = 'Foundation.Core.ModelElement.elementResidence'
            referencedEnd = 'resident'
    
    
        class stereotype(model.Reference):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.stereotype',)
            name = 'stereotype'
            referencedType = 'Stereotype'
            refTypeQN = 'Foundation.Core.ModelElement.stereotype'
            referencedEnd = 'extendedElements'
    
    
        class targetFlows(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.targetFlow',)
            name = 'targetFlows'
            referencedType = 'Flow'
            refTypeQN = 'Foundation.Core.ModelElement.targetFlow'
            referencedEnd = 'targets'
    
    
        class taggedValues(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.taggedValue',)
            name = 'taggedValues'
            referencedType = 'TaggedValue'
            refTypeQN = 'Foundation.Core.ModelElement.taggedValue'
            referencedEnd = 'modelElement'
    
    
        class templateParameters2(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.templateParameter2',)
            name = 'templateParameters2'
            referencedType = 'TemplateParameter'
            refTypeQN = 'Foundation.Core.ModelElement.templateParameter2'
            referencedEnd = 'modelElement2'
    


        class visibility(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.ModelElement.visibility'
            _XMINames = ('Foundation.Core.ModelElement.visibility',)
            name = 'visibility'
            referencedType = 'VisibilityKind'
    
        _XMINames = ('Foundation.Core.ModelElement',)
    
        class presentations(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.presentation',)
            name = 'presentations'
            referencedType = 'PresentationElement'
            refTypeQN = 'Foundation.Core.ModelElement.presentation'
            referencedEnd = 'subjects'
    
    
        class bindings(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.binding',)
            name = 'bindings'
            referencedType = 'Binding'
            refTypeQN = 'Foundation.Core.ModelElement.binding'
            referencedEnd = 'arguments'
    
    
        class templateParameters(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.templateParameter',)
            name = 'templateParameters'
            referencedType = 'TemplateParameter'
            refTypeQN = 'Foundation.Core.ModelElement.templateParameter'
            referencedEnd = 'modelElement'
    



        class partitions(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.partition',)
            name = 'partitions'
            referencedType = 'Partition'
            refTypeQN = 'Foundation.Core.ModelElement.partition1'
            referencedEnd = 'contents'
    
    
        class sourceFlows(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.sourceFlow',)
            name = 'sourceFlows'
            referencedType = 'Flow'
            refTypeQN = 'Foundation.Core.ModelElement.sourceFlow'
            referencedEnd = 'sources'
    
    
        class behaviors(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.behavior',)
            name = 'behaviors'
            referencedType = 'StateMachine'
            refTypeQN = 'Foundation.Core.ModelElement.behavior'
            referencedEnd = 'context'
    
    
        class classifierRoles(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.classifierRole',)
            name = 'classifierRoles'
            referencedType = 'ClassifierRole'
            refTypeQN = 'Foundation.Core.ModelElement.classifierRole1'
            referencedEnd = 'availableContents'
    


        class collaborations(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.collaboration',)
            name = 'collaborations'
            referencedType = 'Collaboration'
            refTypeQN = 'Foundation.Core.ModelElement.collaboration1'
            referencedEnd = 'constrainingElements'
    
    
        class namespace(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.namespace',)
            name = 'namespace'
            referencedType = 'Namespace'
            refTypeQN = 'Foundation.Core.ModelElement.namespace'
            referencedEnd = 'ownedElements'
    
    
        class comments(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.comment',)
            name = 'comments'
            referencedType = 'Comment'
            refTypeQN = 'Foundation.Core.ModelElement.comment'
            referencedEnd = 'annotatedElements'
    
    
        class name(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.ModelElement.name'
            _XMINames = ('Foundation.Core.ModelElement.name',)
            name = 'name'
            referencedType = 'Name'
    




        class elementImports(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.elementImport',)
            name = 'elementImports'
            referencedType = 'ElementImport'
            refTypeQN = 'Foundation.Core.ModelElement.elementImport2'
            referencedEnd = 'modelElement'
    
    
        class supplierDependencies(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.supplierDependency',)
            name = 'supplierDependencies'
            referencedType = 'Dependency'
            refTypeQN = 'Foundation.Core.ModelElement.supplierDependency'
            referencedEnd = 'suppliers'
    
    
        class clientDependencies(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.clientDependency',)
            name = 'clientDependencies'
            referencedType = 'Dependency'
            refTypeQN = 'Foundation.Core.ModelElement.clientDependency'
            referencedEnd = 'clients'
    
    
        class templateParameters3(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.templateParameter3',)
            name = 'templateParameters3'
            referencedType = 'TemplateParameter'
            refTypeQN = 'Foundation.Core.ModelElement.templateParameter3'
            referencedEnd = 'defaultElement'
    


        class constraints(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ModelElement.constraint',)
            name = 'constraints'
            referencedType = 'Constraint'
            refTypeQN = 'Foundation.Core.ModelElement.constraint'
            referencedEnd = 'constrainedElements'
    

    class Action(ModelElement):

        isAbstract = 0
    
        class state3(model.Reference):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.state3',)
            name = 'state3'
            referencedType = 'State'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Action.state3'
            referencedEnd = 'doActivity'
    
    
        class target(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Action.target'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.target',)
            name = 'target'
            referencedType = 'ObjectSetExpression'
    
    
        class script(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Action.script'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.script',)
            name = 'script'
            referencedType = 'ActionExpression'
    


        class stimuli(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.stimulus',)
            name = 'stimuli'
            referencedType = 'Stimulus'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Action.stimulus'
            referencedEnd = 'dispatchAction'
    
    
        class transition(model.Reference):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.transition',)
            name = 'transition'
            referencedType = 'Transition'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Action.transition'
            referencedEnd = 'effect'
    
    
        class messages(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.message',)
            name = 'messages'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Action.message'
            referencedEnd = 'action'
    
    
        class isAsynchronous(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Action.isAsynchronous'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.isAsynchronous',)
            name = 'isAsynchronous'
            referencedType = 'Boolean'
    




        class actionSequence(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.actionSequence',)
            name = 'actionSequence'
            referencedType = 'ActionSequence'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Action.actionSequence'
            referencedEnd = 'actions'
    
    
        class recurrence(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Action.recurrence'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.recurrence',)
            name = 'recurrence'
            referencedType = 'IterationExpression'
    
    
        class state2(model.Reference):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.state2',)
            name = 'state2'
            referencedType = 'State'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Action.state2'
            referencedEnd = 'exit'
    
    
        class state1(model.Reference):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.state1',)
            name = 'state1'
            referencedType = 'State'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Action.state1'
            referencedEnd = 'entry'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Action',)



        class actualArguments(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Action.actualArgument',)
            name = 'actualArguments'
            referencedType = 'Argument'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Action.actualArgument'
            referencedEnd = 'action'
    

    class ReturnAction(Action):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.ReturnAction',)


    class PresentationElement(Element):
        isAbstract = 1
    
        class subjects(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.PresentationElement.subject',)
            name = 'subjects'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.PresentationElement.subject'
            referencedEnd = 'presentations'
    
        _XMINames = ('Foundation.Core.PresentationElement',)


    class AssociationEnd(ModelElement):
    
        class isNavigable(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.AssociationEnd.isNavigable'
            _XMINames = ('Foundation.Core.AssociationEnd.isNavigable',)
            name = 'isNavigable'
            referencedType = 'Boolean'
    
        isAbstract = 0
    
        class changeability(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.AssociationEnd.changeability'
            _XMINames = ('Foundation.Core.AssociationEnd.changeability',)
            name = 'changeability'
            referencedType = 'ChangeableKind'
    
    
        class specifications(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.AssociationEnd.specification',)
            name = 'specifications'
            referencedType = 'Classifier'
            refTypeQN = 'Foundation.Core.AssociationEnd.specification'
            referencedEnd = 'participants'
    
    
        class multiplicity(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.AssociationEnd.multiplicity'
            _XMINames = ('Foundation.Core.AssociationEnd.multiplicity',)
            name = 'multiplicity'
            referencedType = 'Multiplicity'
    
    
        class aggregation(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.AssociationEnd.aggregation'
            _XMINames = ('Foundation.Core.AssociationEnd.aggregation',)
            name = 'aggregation'
            referencedType = 'AggregationKind'
    
    
        class ordering(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.AssociationEnd.ordering'
            _XMINames = ('Foundation.Core.AssociationEnd.ordering',)
            name = 'ordering'
            referencedType = 'OrderingKind'
    
        class associationEndRoles(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.AssociationEnd.associationEndRole',)
            name = 'associationEndRoles'
            referencedType = 'AssociationEndRole'
            refTypeQN = 'Foundation.Core.AssociationEnd.associationEndRole'
            referencedEnd = 'base'
    
    
        class linkEnds(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.AssociationEnd.linkEnd',)
            name = 'linkEnds'
            referencedType = 'LinkEnd'
            refTypeQN = 'Foundation.Core.AssociationEnd.linkEnd'
            referencedEnd = 'associationEnd'
    
    
        class targetScope(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.AssociationEnd.targetScope'
            _XMINames = ('Foundation.Core.AssociationEnd.targetScope',)
            name = 'targetScope'
            referencedType = 'ScopeKind'
    
        _XMINames = ('Foundation.Core.AssociationEnd',)
    
        class type(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.AssociationEnd.type',)
            name = 'type'
            referencedType = 'Classifier'
            refTypeQN = 'Foundation.Core.AssociationEnd.type'
            referencedEnd = 'associationEnds'
    



        class qualifiers(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.AssociationEnd.qualifier',)
            name = 'qualifiers'
            referencedType = 'Attribute'
            refTypeQN = 'Foundation.Core.AssociationEnd.qualifier'
            referencedEnd = 'associationEnd'
    
    
        class association(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.AssociationEnd.association',)
            name = 'association'
            referencedType = 'Association'
            refTypeQN = 'Foundation.Core.AssociationEnd.association'
            referencedEnd = 'connections'
    






















    class Instance(ModelElement):
    
        isAbstract = 0
    
        class stimuli1(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.stimulus1',)
            name = 'stimuli1'
            referencedType = 'Stimulus'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Instance.stimulus1'
            referencedEnd = 'arguments'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Instance',)
    
        class componentInstance(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.componentInstance',)
            name = 'componentInstance'
            referencedType = 'ComponentInstance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Instance.componentInstance'
            referencedEnd = 'residents'
    
    
        class classifiers(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.classifier',)
            name = 'classifiers'
            referencedType = 'Classifier'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Instance.classifier'
            referencedEnd = 'instances'







    
        class slots(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.slot',)
            name = 'slots'
            referencedType = 'AttributeLink'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Instance.slot'
            referencedEnd = 'instance'
    
    
        class stimuli3(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.stimulus3',)
            name = 'stimuli3'
            referencedType = 'Stimulus'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Instance.stimulus3'
            referencedEnd = 'sender'
    
    
        class attributeLinks(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.attributeLink',)
            name = 'attributeLinks'
            referencedType = 'AttributeLink'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Instance.attributeLink'
            referencedEnd = 'value'
    
    
        class linkEnds(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.linkEnd',)
            name = 'linkEnds'
            referencedType = 'LinkEnd'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Instance.linkEnd'
            referencedEnd = 'instance'
    


        class stimuli2(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Instance.stimulus2',)
            name = 'stimuli2'
            referencedType = 'Stimulus'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Instance.stimulus2'
            referencedEnd = 'receiver'
    

    class UseCaseInstance(Instance):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Use_Cases.UseCaseInstance',)


    class StateVertex(ModelElement):
        isAbstract = 1
        _XMINames = ('Behavioral_Elements.State_Machines.StateVertex',)
    
        class container(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.StateVertex.container',)
            name = 'container'
            referencedType = 'CompositeState'
            refTypeQN = 'Behavioral_Elements.State_Machines.StateVertex.container'
            referencedEnd = 'subvertices'
    
    
        class outgoings(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.StateVertex.outgoing',)
            name = 'outgoings'
            referencedType = 'Transition'
            refTypeQN = 'Behavioral_Elements.State_Machines.StateVertex.outgoing'
            referencedEnd = 'source'
    



        class incomings(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.StateVertex.incoming',)
            name = 'incomings'
            referencedType = 'Transition'
            refTypeQN = 'Behavioral_Elements.State_Machines.StateVertex.incoming'
            referencedEnd = 'target'


    class State(StateVertex):

        isAbstract = 0
    
        class doActivity(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.State.doActivity',)
            name = 'doActivity'
            referencedType = 'Action'
            refTypeQN = 'Behavioral_Elements.State_Machines.State.doActivity'
            referencedEnd = 'state3'
    
    
        class exit(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.State.exit',)
            name = 'exit'
            referencedType = 'Action'
            refTypeQN = 'Behavioral_Elements.State_Machines.State.exit'
            referencedEnd = 'state2'









        class internalTransitions(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.State.internalTransition',)
            name = 'internalTransitions'
            referencedType = 'Transition'
            refTypeQN = 'Behavioral_Elements.State_Machines.State.internalTransition'
            referencedEnd = 'state'
    
    
        class stateMachine(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.State.stateMachine',)
            name = 'stateMachine'
            referencedType = 'StateMachine'
            refTypeQN = 'Behavioral_Elements.State_Machines.State.stateMachine'
            referencedEnd = 'top'
    
    
        class deferrableEvents(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.State.deferrableEvent',)
            name = 'deferrableEvents'
            referencedType = 'Event'
            refTypeQN = 'Behavioral_Elements.State_Machines.State.deferrableEvent'
            referencedEnd = 'states'
    
    
        class classifiersInState(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.State.classifierInState',)
            name = 'classifiersInState'
            referencedType = 'ClassifierInState'
            refTypeQN = 'Behavioral_Elements.State_Machines.State.classifierInState'
            referencedEnd = 'inStates'
    


        class entry(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.State.entry',)
            name = 'entry'
            referencedType = 'Action'
            refTypeQN = 'Behavioral_Elements.State_Machines.State.entry'
            referencedEnd = 'state1'
    
        _XMINames = ('Behavioral_Elements.State_Machines.State',)


    class CompositeState(State):
        isAbstract = 0
    
        class subvertices(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.CompositeState.subvertex',)
            name = 'subvertices'
            referencedType = 'StateVertex'
            refTypeQN = 'Behavioral_Elements.State_Machines.CompositeState.subvertex'
            referencedEnd = 'container'
    
    
        class isConcurent(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.State_Machines.CompositeState.isConcurent'
            _XMINames = ('Behavioral_Elements.State_Machines.CompositeState.isConcurent',)
            name = 'isConcurent'
            referencedType = 'Boolean'
    
        _XMINames = ('Behavioral_Elements.State_Machines.CompositeState',)








    class SubmachineState(CompositeState):
    
        isAbstract = 0
    
        class submachine(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.SubmachineState.submachine',)
            name = 'submachine'
            referencedType = 'StateMachine'
            refTypeQN = 'Behavioral_Elements.State_Machines.SubmachineState.submachine'
            referencedEnd = 'subMachineStates'
    
        _XMINames = ('Behavioral_Elements.State_Machines.SubmachineState',)


    class SubactivityState(SubmachineState):

        isAbstract = 0
    
        class dynamicArguments(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Activity_Graphs.SubactivityState.dynamicArguments'
            _XMINames = ('Behavioral_Elements.Activity_Graphs.SubactivityState.dynamicArguments',)
            name = 'dynamicArguments'
            referencedType = 'ArgListsExpression'
    
    
        class isDynamic(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Activity_Graphs.SubactivityState.isDynamic'
            _XMINames = ('Behavioral_Elements.Activity_Graphs.SubactivityState.isDynamic',)
            name = 'isDynamic'
            referencedType = 'Boolean'
    
        _XMINames = ('Behavioral_Elements.Activity_Graphs.SubactivityState',)





        class dynamicMultiplicity(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Activity_Graphs.SubactivityState.dynamicMultiplicity'
            _XMINames = ('Behavioral_Elements.Activity_Graphs.SubactivityState.dynamicMultiplicity',)
            name = 'dynamicMultiplicity'
            referencedType = 'Multiplicity'
    


    class Relationship(ModelElement):
        isAbstract = 0
        _XMINames = ('Foundation.Core.Relationship',)


    class Dependency(Relationship):
        isAbstract = 0
    
        class suppliers(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Dependency.supplier',)
            name = 'suppliers'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.Dependency.supplier'
            referencedEnd = 'supplierDependencies'
    
    
        class clients(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Dependency.client',)
            name = 'clients'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.Dependency.client'
            referencedEnd = 'clientDependencies'
    
        _XMINames = ('Foundation.Core.Dependency',)




    class Usage(Dependency):
        isAbstract = 0
        _XMINames = ('Foundation.Core.Usage',)


    class CallAction(Action):

        isAbstract = 0
    
        class operation(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.CallAction.operation',)
            name = 'operation'
            referencedType = 'Operation'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.CallAction.operation'
            referencedEnd = 'callActions'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.CallAction',)


    class Include(Relationship):

        isAbstract = 0
    
        class addition(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.Include.addition',)
            name = 'addition'
            referencedType = 'UseCase'
            refTypeQN = 'Behavioral_Elements.Use_Cases.Include.addition'
            referencedEnd = 'includes'
    







        class base(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.Include.base',)
            name = 'base'
            referencedType = 'UseCase'
            refTypeQN = 'Behavioral_Elements.Use_Cases.Include.base'
            referencedEnd = 'includes2'
    
        _XMINames = ('Behavioral_Elements.Use_Cases.Include',)


    class Feature(ModelElement):

        isAbstract = 1
    
        class owner(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Feature.owner',)
            name = 'owner'
            referencedType = 'Classifier'
            refTypeQN = 'Foundation.Core.Feature.owner'
            referencedEnd = 'features'
    
        _XMINames = ('Foundation.Core.Feature',)
    
        class ownerScope(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Feature.ownerScope'
            _XMINames = ('Foundation.Core.Feature.ownerScope',)
            name = 'ownerScope'
            referencedType = 'ScopeKind'
    







        class classifierRoles(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Feature.classifierRole',)
            name = 'classifierRoles'
            referencedType = 'ClassifierRole'
            refTypeQN = 'Foundation.Core.Feature.classifierRole'
            referencedEnd = 'availableFeatures'


    class BehavioralFeature(Feature):
        isAbstract = 1
    
        class isQuery(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.BehavioralFeature.isQuery'
            _XMINames = ('Foundation.Core.BehavioralFeature.isQuery',)
            name = 'isQuery'
            referencedType = 'Boolean'
    
        _XMINames = ('Foundation.Core.BehavioralFeature',)
    
        class raisedSignals(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.BehavioralFeature.raisedSignal',)
            name = 'raisedSignals'
            referencedType = 'Signal'
            refTypeQN = 'Foundation.Core.BehavioralFeature.raisedSignal'
            referencedEnd = 'contexts'
    
    
        class parameters(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.BehavioralFeature.parameter',)
            name = 'parameters'
            referencedType = 'Parameter'
            refTypeQN = 'Foundation.Core.BehavioralFeature.parameter'
            referencedEnd = 'behavioralFeature'
    
    class Method(BehavioralFeature):
    
        class body(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Method.body'
            _XMINames = ('Foundation.Core.Method.body',)
            name = 'body'
            referencedType = 'ProcedureExpression'
    
        isAbstract = 0
    
        class specification(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Method.specification',)
            name = 'specification'
            referencedType = 'Operation'
            refTypeQN = 'Foundation.Core.Method.specification'
            referencedEnd = 'methods'
    
        _XMINames = ('Foundation.Core.Method',)


    class GeneralizableElement(ModelElement):

        isAbstract = 1

        _XMINames = ('Foundation.Core.GeneralizableElement',)
    
        class isRoot(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.GeneralizableElement.isRoot'
            _XMINames = ('Foundation.Core.GeneralizableElement.isRoot',)
            name = 'isRoot'
            referencedType = 'Boolean'





    
        class generalizations(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.GeneralizableElement.generalization',)
            name = 'generalizations'
            referencedType = 'Generalization'
            refTypeQN = 'Foundation.Core.GeneralizableElement.generalization'
            referencedEnd = 'child'
    
    
        class specializations(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.GeneralizableElement.specialization',)
            name = 'specializations'
            referencedType = 'Generalization'
            refTypeQN = 'Foundation.Core.GeneralizableElement.specialization'
            referencedEnd = 'parent'
    
    
        class isLeaf(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.GeneralizableElement.isLeaf'
            _XMINames = ('Foundation.Core.GeneralizableElement.isLeaf',)
            name = 'isLeaf'
            referencedType = 'Boolean'
    














    class Namespace(ModelElement):

        isAbstract = 0

        _XMINames = ('Foundation.Core.Namespace',)
    
        class ownedElements(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Namespace.ownedElement',)
            name = 'ownedElements'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.Namespace.ownedElement'
            referencedEnd = 'namespace'
    


    class Classifier(GeneralizableElement,Namespace):

        isAbstract = 0
    
        class structuralFeatures(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.structuralFeature',)
            name = 'structuralFeatures'
            referencedType = 'StructuralFeature'
            refTypeQN = 'Foundation.Core.Classifier.structuralFeature'
            referencedEnd = 'type'
    
    
        class features(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.feature',)
            name = 'features'
            referencedType = 'Feature'
            refTypeQN = 'Foundation.Core.Classifier.feature'
            referencedEnd = 'owner'
    
    
        class parameters(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.parameter',)
            name = 'parameters'
            referencedType = 'Parameter'
            refTypeQN = 'Foundation.Core.Classifier.parameter'
            referencedEnd = 'type'
    
    
        class objectFlowStates(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.objectFlowState',)
            name = 'objectFlowStates'
            referencedType = 'ObjectFlowState'
            refTypeQN = 'Foundation.Core.Classifier.objectFlowState'
            referencedEnd = 'type'
    
    
        class classifiersInState(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.classifierInState',)
            name = 'classifiersInState'
            referencedType = 'ClassifierInState'
            refTypeQN = 'Foundation.Core.Classifier.classifierInState'
            referencedEnd = 'type'
    
    
        class participants(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.participant',)
            name = 'participants'
            referencedType = 'AssociationEnd'
            refTypeQN = 'Foundation.Core.Classifier.participant'
            referencedEnd = 'specifications'
    


        class associationEnds(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.associationEnd',)
            name = 'associationEnds'
            referencedType = 'AssociationEnd'
            refTypeQN = 'Foundation.Core.Classifier.associationEnd'
            referencedEnd = 'type'
    
    
        class collaborations(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.collaboration',)
            name = 'collaborations'
            referencedType = 'Collaboration'
            refTypeQN = 'Foundation.Core.Classifier.collaboration'
            referencedEnd = 'representedClassifier'
    
    
        class powertypeRanges(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.powertypeRange',)
            name = 'powertypeRanges'
            referencedType = 'Generalization'
            refTypeQN = 'Foundation.Core.Classifier.powertypeRange'
            referencedEnd = 'powertype'
    
        _XMINames = ('Foundation.Core.Classifier',)
    
        class createActions(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.createAction',)
            name = 'createActions'
            referencedType = 'CreateAction'
            refTypeQN = 'Foundation.Core.Classifier.createAction'
            referencedEnd = 'instantiation'
    
    
        class instances(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.instance',)
            name = 'instances'
            referencedType = 'Instance'
            refTypeQN = 'Foundation.Core.Classifier.instance'
            referencedEnd = 'classifiers'
    
    
        class classifierRoles(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Classifier.classifierRole',)
            name = 'classifierRoles'
            referencedType = 'ClassifierRole'
            refTypeQN = 'Foundation.Core.Classifier.classifierRole'
            referencedEnd = 'bases'
    

    class Node(Classifier):
        isAbstract = 0
    
        class residents(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Node.resident',)
            name = 'residents'
            referencedType = 'Component'
            refTypeQN = 'Foundation.Core.Node.resident'
            referencedEnd = 'deploymentLocations'
    
        _XMINames = ('Foundation.Core.Node',)








    class Association(GeneralizableElement,Relationship):

        isAbstract = 0
    
        class connections(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Association.connection',)
            name = 'connections'
            referencedType = 'AssociationEnd'
            refTypeQN = 'Foundation.Core.Association.connection'
            referencedEnd = 'association'
    
        _XMINames = ('Foundation.Core.Association',)
    
        class associationRoles(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Association.associationRole',)
            name = 'associationRoles'
            referencedType = 'AssociationRole'
            refTypeQN = 'Foundation.Core.Association.associationRole'
            referencedEnd = 'base'
    
    
        class links(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Association.link',)
            name = 'links'
            referencedType = 'Link'
            refTypeQN = 'Foundation.Core.Association.link'
            referencedEnd = 'association'
    







    class Class(Classifier):

        isAbstract = 0

        _XMINames = ('Foundation.Core.Class',)
    
        class isActive(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Class.isActive'
            _XMINames = ('Foundation.Core.Class.isActive',)
            name = 'isActive'
            referencedType = 'Boolean'
    


    class AssociationClass(Association,Class):
        isAbstract = 0
        _XMINames = ('Foundation.Core.AssociationClass',)


    class Stimulus(ModelElement):

        isAbstract = 0

        _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus',)
    
        class sender(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.sender',)
            name = 'sender'
            referencedType = 'Instance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Stimulus.sender'
            referencedEnd = 'stimuli3'






    
        class receiver(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.receiver',)
            name = 'receiver'
            referencedType = 'Instance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Stimulus.receiver'
            referencedEnd = 'stimuli2'
    
    
        class arguments(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.argument',)
            name = 'arguments'
            referencedType = 'Instance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Stimulus.argument'
            referencedEnd = 'stimuli1'
    
    
        class dispatchAction(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.dispatchAction',)
            name = 'dispatchAction'
            referencedType = 'Action'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Stimulus.dispatchAction'
            referencedEnd = 'stimuli'
    
    
        class communicationLink(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Stimulus.communicationLink',)
            name = 'communicationLink'
            referencedType = 'Link'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Stimulus.communicationLink'
            referencedEnd = 'stimuli'
    


    class StateMachine(ModelElement):

        isAbstract = 0
    
        class transitionses(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.StateMachine.transitions',)
            name = 'transitionses'
            referencedType = 'Transition'
            refTypeQN = 'Behavioral_Elements.State_Machines.StateMachine.transition'
            referencedEnd = 'stateMachine'
    
        _XMINames = ('Behavioral_Elements.State_Machines.StateMachine',)
    
        class context(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.StateMachine.context',)
            name = 'context'
            referencedType = 'ModelElement'
            refTypeQN = 'Behavioral_Elements.State_Machines.StateMachine.context'
            referencedEnd = 'behaviors'
    
    
        class top(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.StateMachine.top',)
            name = 'top'
            referencedType = 'State'
            refTypeQN = 'Behavioral_Elements.State_Machines.StateMachine.top'
            referencedEnd = 'stateMachine'
    







        class subMachineStates(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.StateMachine.subMachineState',)
            name = 'subMachineStates'
            referencedType = 'SubmachineState'
            refTypeQN = 'Behavioral_Elements.State_Machines.StateMachine.submachineState'
            referencedEnd = 'submachine'


    class Event(ModelElement):

        isAbstract = 1
    
        class states(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Event.state',)
            name = 'states'
            referencedType = 'State'
            refTypeQN = 'Behavioral_Elements.State_Machines.Event.state'
            referencedEnd = 'deferrableEvents'
    
    
        class transitions(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Event.transition',)
            name = 'transitions'
            referencedType = 'Transition'
            refTypeQN = 'Behavioral_Elements.State_Machines.Event.transition'
            referencedEnd = 'trigger'
    
        _XMINames = ('Behavioral_Elements.State_Machines.Event',)







        class parameters(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Event.parameter',)
            name = 'parameters'
            referencedType = 'Parameter'
            refTypeQN = 'Behavioral_Elements.State_Machines.Event.parameter'
            referencedEnd = 'event'


    class TimeEvent(Event):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.TimeEvent',)
    
        class when(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.State_Machines.TimeEvent.when'
            _XMINames = ('Behavioral_Elements.State_Machines.TimeEvent.when',)
            name = 'when'
            referencedType = 'TimeExpression'
    


    class LocationReference(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.LocationReference',)


    class Object(Instance):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.Object',)


    class TerminateAction(Action):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.TerminateAction',)


    class UnlimitedInteger(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.UnlimitedInteger',)


    class Integer(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.Integer',)


    class ElementImport(Base):

        isAbstract = 0
    
        class alias(model.Field):
            isRequired = 1
            qualifiedName = 'Model_Management.ElementImport.alias'
            _XMINames = ('Model_Management.ElementImport.alias',)
            name = 'alias'
            referencedType = 'Name'
    
        _XMINames = ('Model_Management.ElementImport',)
    
        class package(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Model_Management.ElementImport.package',)
            name = 'package'
            referencedType = 'Package'
            refTypeQN = 'Model_Management.ElementImport.package'
            referencedEnd = 'elementImports'
    
    
        class modelElement(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Model_Management.ElementImport.modelElement',)
            name = 'modelElement'
            referencedType = 'ModelElement'
            refTypeQN = 'Model_Management.ElementImport.modelElement'
            referencedEnd = 'elementImports'
    





        class visibility(model.Field):
            isRequired = 1
            qualifiedName = 'Model_Management.ElementImport.visibility'
            _XMINames = ('Model_Management.ElementImport.visibility',)
            name = 'visibility'
            referencedType = 'VisibilityKind'

    class DestroyAction(Action):

        isAbstract = 0

        _XMINames = ('Behavioral_Elements.Common_Behavior.DestroyAction',)


    class ClassifierInState(Classifier):

        isAbstract = 0
    
        class type(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ClassifierInState.type',)
            name = 'type'
            referencedType = 'Classifier'
            refTypeQN = 'Behavioral_Elements.Activity_Graphs.ClassifierInState.type'
            referencedEnd = 'classifiersInState'
    
    
        class inStates(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ClassifierInState.inState',)
            name = 'inStates'
            referencedType = 'State'
            refTypeQN = 'Behavioral_Elements.Activity_Graphs.ClassifierInState.inState'
            referencedEnd = 'classifiersInState'
    
        _XMINames = ('Behavioral_Elements.Activity_Graphs.ClassifierInState',)



    class NodeInstance(Instance):

        isAbstract = 0
    
        class residents(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.NodeInstance.resident',)
            name = 'residents'
            referencedType = 'ComponentInstance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.NodeInstance.resident'
            referencedEnd = 'nodeInstance'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.NodeInstance',)


    class Signal(Classifier):

        isAbstract = 0
    
        class receptions(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Signal.reception',)
            name = 'receptions'
            referencedType = 'Reception'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Signal.reception'
            referencedEnd = 'signal'
    
    
        class occurrences(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Signal.occurrence',)
            name = 'occurrences'
            referencedType = 'SignalEvent'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Signal.occurrence'
            referencedEnd = 'signal'
    


        class contexts(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Signal.context',)
            name = 'contexts'
            referencedType = 'BehavioralFeature'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Signal.context'
            referencedEnd = 'raisedSignals'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Signal',)
    
        class sendActions(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Signal.sendAction',)
            name = 'sendActions'
            referencedType = 'SendAction'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Signal.sendAction'
            referencedEnd = 'signal'
    

    class Exception(Signal):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.Exception',)


    class SimpleState(State):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.SimpleState',)












    class ObjectFlowState(SimpleState):

        isAbstract = 0

        _XMINames = ('Behavioral_Elements.Activity_Graphs.ObjectFlowState',)
    
        class isSynch(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Activity_Graphs.ObjectFlowState.isSynch'
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ObjectFlowState.isSynch',)
            name = 'isSynch'
            referencedType = 'Boolean'
    
    
        class parameters(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ObjectFlowState.parameter',)
            name = 'parameters'
            referencedType = 'Parameter'
            refTypeQN = 'Behavioral_Elements.Activity_Graphs.ObjectFlowState.parameter'
            referencedEnd = 'states'
    
    
        class type(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ObjectFlowState.type',)
            name = 'type'
            referencedType = 'Classifier'
            refTypeQN = 'Behavioral_Elements.Activity_Graphs.ObjectFlowState.type'
            referencedEnd = 'objectFlowStates'
    


    class MappingExpression(Expression):
        _XMINames = ('Foundation.Data_Types.MappingExpression',)




    class Constraint(ModelElement):
    
        class body(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Constraint.body'
            _XMINames = ('Foundation.Core.Constraint.body',)
            name = 'body'
            referencedType = 'BooleanExpression'
    
        isAbstract = 0
        _XMINames = ('Foundation.Core.Constraint',)
    
        class constrainedElement2(model.Reference):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Constraint.constrainedElement2',)
            name = 'constrainedElement2'
            referencedType = 'Stereotype'
            refTypeQN = 'Foundation.Core.Constraint.constrainedElement2'
            referencedEnd = 'stereotypeConstraints'
    
    
        class constrainedElements(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Constraint.constrainedElement',)
            name = 'constrainedElements'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.Constraint.constrainedElement'
            referencedEnd = 'constraints'
    










    class PseudostateKind(model.Enumeration):
        fork = 'fork'
        shallowHistory = 'shallowHistory'
        junction = 'junction'
        branch = 'branch'
        deepHistory = 'deepHistory'
        _XMINames = ('Foundation.Data_Types.PseudostateKind',)
        initial = 'initial'
        final = 'final'
        join = 'join'


    class Transition(ModelElement):

        isAbstract = 0
    
        class source(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.source',)
            name = 'source'
            referencedType = 'StateVertex'
            refTypeQN = 'Behavioral_Elements.State_Machines.Transition.source'
            referencedEnd = 'outgoings'
    
    
        class guard(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.guard',)
            name = 'guard'
            referencedType = 'Guard'
            refTypeQN = 'Behavioral_Elements.State_Machines.Transition.guard'
            referencedEnd = 'transition'






    
        class trigger(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.trigger',)
            name = 'trigger'
            referencedType = 'Event'
            refTypeQN = 'Behavioral_Elements.State_Machines.Transition.trigger'
            referencedEnd = 'transitions'
    
        _XMINames = ('Behavioral_Elements.State_Machines.Transition',)
    
        class target(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.target',)
            name = 'target'
            referencedType = 'StateVertex'
            refTypeQN = 'Behavioral_Elements.State_Machines.Transition.target'
            referencedEnd = 'incomings'
    
    
        class stateMachine(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.stateMachine',)
            name = 'stateMachine'
            referencedType = 'StateMachine'
            refTypeQN = 'Behavioral_Elements.State_Machines.Transition.stateMachine'
            referencedEnd = 'transitionses'
    
    
        class state(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.state',)
            name = 'state'
            referencedType = 'State'
            refTypeQN = 'Behavioral_Elements.State_Machines.Transition.state'
            referencedEnd = 'internalTransitions'
    
    
        class effect(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Transition.effect',)
            name = 'effect'
            referencedType = 'Action'
            refTypeQN = 'Behavioral_Elements.State_Machines.Transition.effect'
            referencedEnd = 'transition'
   

    class Flow(Relationship):

        isAbstract = 0
    
        class sources(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Flow.source',)
            name = 'sources'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.Flow.source'
            referencedEnd = 'sourceFlows'
    
        _XMINames = ('Foundation.Core.Flow',)
    
        class targets(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Flow.target',)
            name = 'targets'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.Flow.target'
            referencedEnd = 'targetFlows'
    







    class StructuralFeature(Feature):

        isAbstract = 1

        _XMINames = ('Foundation.Core.StructuralFeature',)
    
        class targetScope(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.StructuralFeature.targetScope'
            _XMINames = ('Foundation.Core.StructuralFeature.targetScope',)
            name = 'targetScope'
            referencedType = 'ScopeKind'
    
    
        class changeability(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.StructuralFeature.changeability'
            _XMINames = ('Foundation.Core.StructuralFeature.changeability',)
            name = 'changeability'
            referencedType = 'ChangeableKind'
    
    
        class multiplicity(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.StructuralFeature.multiplicity'
            _XMINames = ('Foundation.Core.StructuralFeature.multiplicity',)
            name = 'multiplicity'
            referencedType = 'Multiplicity'
    
    
        class type(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.StructuralFeature.type',)
            name = 'type'
            referencedType = 'Classifier'
            refTypeQN = 'Foundation.Core.StructuralFeature.type'
            referencedEnd = 'structuralFeatures'
    


    class UseCase(Classifier):

        isAbstract = 0
    
        class extends2(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.extend2',)
            name = 'extends2'
            referencedType = 'Extend'
            refTypeQN = 'Behavioral_Elements.Use_Cases.UseCase.extend2'
            referencedEnd = 'base'
    
    
        class extends(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.extend',)
            name = 'extends'
            referencedType = 'Extend'
            refTypeQN = 'Behavioral_Elements.Use_Cases.UseCase.extend'
            referencedEnd = 'extension'
    
    
        class extensionPoints(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.extensionPoint',)
            name = 'extensionPoints'
            referencedType = 'ExtensionPoint'
            refTypeQN = 'Behavioral_Elements.Use_Cases.UseCase.extensionPoint'
            referencedEnd = 'useCase'
    
        _XMINames = ('Behavioral_Elements.Use_Cases.UseCase',)







        class includes2(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.include2',)
            name = 'includes2'
            referencedType = 'Include'
            refTypeQN = 'Behavioral_Elements.Use_Cases.UseCase.include2'
            referencedEnd = 'base'
    
    
        class includes(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.UseCase.include',)
            name = 'includes'
            referencedType = 'Include'
            refTypeQN = 'Behavioral_Elements.Use_Cases.UseCase.include'
            referencedEnd = 'addition'
    

    class Actor(Classifier):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Use_Cases.Actor',)


    class Time(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.Time',)














    class AttributeLink(ModelElement):

        isAbstract = 0
    
        class linkEnd(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink.linkEnd',)
            name = 'linkEnd'
            referencedType = 'LinkEnd'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.AttributeLink.linkEnd'
            referencedEnd = 'qualifiedValues'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink',)
    
        class instance(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink.instance',)
            name = 'instance'
            referencedType = 'Instance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.AttributeLink.instance'
            referencedEnd = 'slots'
    
    
        class attribute(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink.attribute',)
            name = 'attribute'
            referencedType = 'Attribute'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.AttributeLink.attribute'
            referencedEnd = 'attributeLinks'
    







        class value(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.AttributeLink.value',)
            name = 'value'
            referencedType = 'Instance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.AttributeLink.value'
            referencedEnd = 'attributeLinks'
    


    class SignalEvent(Event):
        isAbstract = 0
    
        class signal(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.SignalEvent.signal',)
            name = 'signal'
            referencedType = 'Signal'
            refTypeQN = 'Behavioral_Elements.State_Machines.SignalEvent.signal'
            referencedEnd = 'occurrences'
    
        _XMINames = ('Behavioral_Elements.State_Machines.SignalEvent',)


    class Package(GeneralizableElement,Namespace):
        isAbstract = 0
    
        class elementImports(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Model_Management.Package.elementImport',)
            name = 'elementImports'
            referencedType = 'ElementImport'
            refTypeQN = 'Model_Management.Package.elementImport'
            referencedEnd = 'package'
    
        _XMINames = ('Model_Management.Package',)


    class Subsystem(Package,Classifier):

        isAbstract = 0

        _XMINames = ('Model_Management.Subsystem',)
    
        class isInstantiable(model.Field):
            isRequired = 1
            qualifiedName = 'Model_Management.Subsystem.isInstantiable'
            _XMINames = ('Model_Management.Subsystem.isInstantiable',)
            name = 'isInstantiable'
            referencedType = 'Boolean'
    


    class CallEvent(Event):

        isAbstract = 0
    
        class operation(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.CallEvent.operation',)
            name = 'operation'
            referencedType = 'Operation'
            refTypeQN = 'Behavioral_Elements.State_Machines.CallEvent.operation'
            referencedEnd = 'occurrences'
    
        _XMINames = ('Behavioral_Elements.State_Machines.CallEvent',)

    name = 'UML_MetaModel'










    class Attribute(StructuralFeature):

        isAbstract = 0
    
        class initialValue(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Attribute.initialValue'
            _XMINames = ('Foundation.Core.Attribute.initialValue',)
            name = 'initialValue'
            referencedType = 'Expression'
        
        class associationEndRoles(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Attribute.associationEndRole',)
            name = 'associationEndRoles'
            referencedType = 'AssociationEndRole'
            refTypeQN = 'Foundation.Core.Attribute.associationEndRole'
            referencedEnd = 'availableQualifiers'
    
        _XMINames = ('Foundation.Core.Attribute',)
    
        class associationEnd(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Attribute.associationEnd',)
            name = 'associationEnd'
            referencedType = 'AssociationEnd'
            refTypeQN = 'Foundation.Core.Attribute.associationEnd'
            referencedEnd = 'qualifiers'
        
        class attributeLinks(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Attribute.attributeLink',)
            name = 'attributeLinks'
            referencedType = 'AttributeLink'
            refTypeQN = 'Foundation.Core.Attribute.attributeLink'
            referencedEnd = 'attribute'
    

    class ProcedureExpression(Expression):
        _XMINames = ('Foundation.Data_Types.ProcedureExpression',)


    class BooleanExpression(Expression):
        _XMINames = ('Foundation.Data_Types.BooleanExpression',)


    class CallConcurrencyKind(model.Enumeration):
        concurrent = 'concurrent'
        guarded = 'guarded'
        _XMINames = ('Foundation.Data_Types.CallConcurrencyKind',)
        sequential = 'sequential'


    class StubState(StateVertex):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.StubState',)
    
        class referenceState(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.State_Machines.StubState.referenceState'
            _XMINames = ('Behavioral_Elements.State_Machines.StubState.referenceState',)
            name = 'referenceState'
            referencedType = 'Name'
    


    class AssociationEndRole(AssociationEnd):
        isAbstract = 0
    
        class availableQualifiers(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationEndRole.availableQualifier',)
            name = 'availableQualifiers'
            referencedType = 'Attribute'
            refTypeQN = 'Behavioral_Elements.Collaborations.AssociationEndRole.availableQualifier'
            referencedEnd = 'associationEndRoles'
    
    
        class base(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationEndRole.base',)
            name = 'base'
            referencedType = 'AssociationEnd'
            refTypeQN = 'Behavioral_Elements.Collaborations.AssociationEndRole.base'
            referencedEnd = 'associationEndRoles'
    
        _XMINames = ('Behavioral_Elements.Collaborations.AssociationEndRole',)


    class MultiplicityRange(model.DataType):
    
        class upper(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Data_Types.MultiplicityRange.upper'
            _XMINames = ('Foundation.Data_Types.MultiplicityRange.upper',)
            name = 'upper'
            referencedType = 'UnlimitedInteger'
    
    
        class lower(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Data_Types.MultiplicityRange.lower'
            _XMINames = ('Foundation.Data_Types.MultiplicityRange.lower',)
            name = 'lower'
            referencedType = 'Integer'
    
        _XMINames = ('Foundation.Data_Types.MultiplicityRange',)
    
        class multiplicity(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Data_Types.MultiplicityRange.multiplicity',)
            name = 'multiplicity'
            referencedType = 'Multiplicity'
            refTypeQN = 'Foundation.Data_Types.MultiplicityRange.multiplicity'
            referencedEnd = 'ranges'
    

    class ActionExpression(Expression):
        _XMINames = ('Foundation.Data_Types.ActionExpression',)


    class ObjectSetExpression(Expression):
        _XMINames = ('Foundation.Data_Types.ObjectSetExpression',)


    class SynchState(StateVertex):

        isAbstract = 0

        _XMINames = ('Behavioral_Elements.State_Machines.SynchState',)
    
        class bound(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.State_Machines.SynchState.bound'
            _XMINames = ('Behavioral_Elements.State_Machines.SynchState.bound',)
            name = 'bound'
            referencedType = 'UnlimitedInteger'
    


    class FinalState(State):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.FinalState',)


    class Link(ModelElement):

        isAbstract = 0
    
        class connections(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Link.connection',)
            name = 'connections'
            referencedType = 'LinkEnd'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Link.connection'
            referencedEnd = 'link'
    
        class stimuli(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Link.stimulus',)
            name = 'stimuli'
            referencedType = 'Stimulus'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Link.stimulus'
            referencedEnd = 'communicationLink'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Link',)
    
        class association(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Link.association',)
            name = 'association'
            referencedType = 'Association'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Link.association'
            referencedEnd = 'links'


    class LinkObject(Object,Link):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.LinkObject',)


    class ChangeableKind(model.Enumeration):
        frozen = 'frozen'
        addOnly = 'addOnly'
        changeable = 'changeable'
        _XMINames = ('Foundation.Data_Types.ChangeableKind',)










    class Operation(BehavioralFeature):

        isAbstract = 0
    
        class collaborations(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Operation.collaboration',)
            name = 'collaborations'
            referencedType = 'Collaboration'
            refTypeQN = 'Foundation.Core.Operation.collaboration'
            referencedEnd = 'representedOperation'
    
    
        class callActions(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Operation.callAction',)
            name = 'callActions'
            referencedType = 'CallAction'
            refTypeQN = 'Foundation.Core.Operation.callAction'
            referencedEnd = 'operation'
    
        _XMINames = ('Foundation.Core.Operation',)
    
        class methods(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Operation.method',)
            name = 'methods'
            referencedType = 'Method'
            refTypeQN = 'Foundation.Core.Operation.method'
            referencedEnd = 'specification'
        
        class concurrency(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Operation.concurrency'
            _XMINames = ('Foundation.Core.Operation.concurrency',)
            name = 'concurrency'
            referencedType = 'CallConcurrencyKind'
    
        class isRoot(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Operation.isRoot'
            _XMINames = ('Foundation.Core.Operation.isRoot',)
            name = 'isRoot'
            referencedType = 'Boolean'
    
    
        class specification(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Operation.specification'
            _XMINames = ('Foundation.Core.Operation.specification',)
            name = 'specification'
            referencedType = 'String'
    
    
        class isLeaf(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Operation.isLeaf'
            _XMINames = ('Foundation.Core.Operation.isLeaf',)
            name = 'isLeaf'
            referencedType = 'Boolean'
    
    
        class occurrences(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Operation.occurrence',)
            name = 'occurrences'
            referencedType = 'CallEvent'
            refTypeQN = 'Foundation.Core.Operation.occurrence'
            referencedEnd = 'operation'
    

    class ArgListsExpression(Expression):
        _XMINames = ('Foundation.Data_Types.ArgListsExpression',)


    class ActionState(SimpleState):
        isAbstract = 0
    
        class dynamicArguments(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Activity_Graphs.ActionState.dynamicArguments'
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ActionState.dynamicArguments',)
            name = 'dynamicArguments'
            referencedType = 'ArgListsExpression'
    
    
        class isDynamic(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Activity_Graphs.ActionState.isDynamic'
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ActionState.isDynamic',)
            name = 'isDynamic'
            referencedType = 'Boolean'
    
        _XMINames = ('Behavioral_Elements.Activity_Graphs.ActionState',)
    
        class dynamicMultiplicity(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Activity_Graphs.ActionState.dynamicMultiplicity'
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ActionState.dynamicMultiplicity',)
            name = 'dynamicMultiplicity'
            referencedType = 'Multiplicity'
    


    class SendAction(Action):
        isAbstract = 0
    
        class signal(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.SendAction.signal',)
            name = 'signal'
            referencedType = 'Signal'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.SendAction.signal'
            referencedEnd = 'sendActions'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.SendAction',)


    class ElementResidence(Base):

        isAbstract = 0
    
        class resident(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ElementResidence.resident',)
            name = 'resident'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.ElementResidence.resident'
            referencedEnd = 'elementResidences'
    
        _XMINames = ('Foundation.Core.ElementResidence',)
    
        class implementationLocation(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.ElementResidence.implementationLocation',)
            name = 'implementationLocation'
            referencedType = 'Component'
            refTypeQN = 'Foundation.Core.ElementResidence.implementationLocation'
            referencedEnd = 'residentElements'
    
    
        class visibility(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.ElementResidence.visibility'
            _XMINames = ('Foundation.Core.ElementResidence.visibility',)
            name = 'visibility'
            referencedType = 'VisibilityKind'
    









    class Binding(Dependency):

        isAbstract = 0

        _XMINames = ('Foundation.Core.Binding',)
    
        class arguments(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Binding.argument',)
            name = 'arguments'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.Binding.argument'
            referencedEnd = 'bindings'
    


    class TemplateParameter(Base):
        isAbstract = 0
    
        class modelElement(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.TemplateParameter.modelElement',)
            name = 'modelElement'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.TemplateParameter.modelElement'
            referencedEnd = 'templateParameters'
    
    
        class defaultElement(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.TemplateParameter.defaultElement',)
            name = 'defaultElement'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.TemplateParameter.defaultElement'
            referencedEnd = 'templateParameters3'
    
        _XMINames = ('Foundation.Core.TemplateParameter',)
    
        class modelElement2(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.TemplateParameter.modelElement2',)
            name = 'modelElement2'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.TemplateParameter.modelElement2'
            referencedEnd = 'templateParameters2'
    


    class ActionSequence(Action):

        isAbstract = 0

        _XMINames = ('Behavioral_Elements.Common_Behavior.ActionSequence',)
    
        class actions(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.ActionSequence.action',)
            name = 'actions'
            referencedType = 'Action'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.ActionSequence.action'
            referencedEnd = 'actionSequence'
    


    class Parameter(ModelElement):

        isAbstract = 0
    
        class states(model.Collection):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Parameter.state',)
            name = 'states'
            referencedType = 'ObjectFlowState'
            refTypeQN = 'Foundation.Core.Parameter.state'
            referencedEnd = 'parameters'
    
        class kind(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Parameter.kind'
            _XMINames = ('Foundation.Core.Parameter.kind',)
            name = 'kind'
            referencedType = 'ParameterDirectionKind'
    
        _XMINames = ('Foundation.Core.Parameter',)
    
        class behavioralFeature(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Parameter.behavioralFeature',)
            name = 'behavioralFeature'
            referencedType = 'BehavioralFeature'
            refTypeQN = 'Foundation.Core.Parameter.behavioralFeature'
            referencedEnd = 'parameters'
    
    
        class defaultValue(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Parameter.defaultValue'
            _XMINames = ('Foundation.Core.Parameter.defaultValue',)
            name = 'defaultValue'
            referencedType = 'Expression'
    
    
        class type(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Parameter.type',)
            name = 'type'
            referencedType = 'Classifier'
            refTypeQN = 'Foundation.Core.Parameter.type'
            referencedEnd = 'parameters'
    





        class event(model.Reference):
            isNavigable = 0
            isRequired = 1
            _XMINames = ('Foundation.Core.Parameter.event',)
            name = 'event'
            referencedType = 'Event'
            refTypeQN = 'Foundation.Core.Parameter.event'
            referencedEnd = 'parameters'
    

    class ExtensionPoint(ModelElement):

        isAbstract = 0
    
        class extends(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.ExtensionPoint.extend',)
            name = 'extends'
            referencedType = 'Extend'
            refTypeQN = 'Behavioral_Elements.Use_Cases.ExtensionPoint.extend'
            referencedEnd = 'extensionPoints'
    
    
        class useCase(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.ExtensionPoint.useCase',)
            name = 'useCase'
            referencedType = 'UseCase'
            refTypeQN = 'Behavioral_Elements.Use_Cases.ExtensionPoint.useCase'
            referencedEnd = 'extensionPoints'
    
        _XMINames = ('Behavioral_Elements.Use_Cases.ExtensionPoint',)







        class location(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Use_Cases.ExtensionPoint.location'
            _XMINames = ('Behavioral_Elements.Use_Cases.ExtensionPoint.location',)
            name = 'location'
            referencedType = 'LocationReference'


    class ComponentInstance(Instance):
        isAbstract = 0
    
        class nodeInstance(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.ComponentInstance.nodeInstance',)
            name = 'nodeInstance'
            referencedType = 'NodeInstance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.ComponentInstance.nodeInstance'
            referencedEnd = 'residents'
    
    
        class residents(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.ComponentInstance.resident',)
            name = 'residents'
            referencedType = 'Instance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.ComponentInstance.resident'
            referencedEnd = 'componentInstance'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.ComponentInstance',)


    class MessageDirectionKind(model.Enumeration):
        _XMINames = ('Foundation.Data_Types.MessageDirectionKind',)
        activation = 'activation'
        return_ = 'return'




    class Abstraction(Dependency):

        isAbstract = 0
        _XMINames = ('Foundation.Core.Abstraction',)
    
        class mapping(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Abstraction.mapping'
            _XMINames = ('Foundation.Core.Abstraction.mapping',)
            name = 'mapping'
            referencedType = 'MappingExpression'    


    class String(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.String',)


    class Permission(Dependency):
        isAbstract = 0
        _XMINames = ('Foundation.Core.Permission',)


    class Collaboration(Namespace,GeneralizableElement):

        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Collaborations.Collaboration',)
    
        class representedClassifier(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Collaboration.representedClassifier',)
            name = 'representedClassifier'
            referencedType = 'Classifier'
            refTypeQN = 'Behavioral_Elements.Collaborations.Collaboration.representedClassifier'
            referencedEnd = 'collaborations'





    
        class interactions(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Collaboration.interaction',)
            name = 'interactions'
            referencedType = 'Interaction'
            refTypeQN = 'Behavioral_Elements.Collaborations.Collaboration.interaction'
            referencedEnd = 'context'
    
    
        class representedOperation(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Collaboration.representedOperation',)
            name = 'representedOperation'
            referencedType = 'Operation'
            refTypeQN = 'Behavioral_Elements.Collaborations.Collaboration.representedOperation'
            referencedEnd = 'collaborations'
    
    
        class constrainingElements(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Collaboration.constrainingElement',)
            name = 'constrainingElements'
            referencedType = 'ModelElement'
            refTypeQN = 'Behavioral_Elements.Collaborations.Collaboration.constrainingElement'
            referencedEnd = 'collaborations'













    class Component(Classifier):

        isAbstract = 0
    
        class deploymentLocations(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Component.deploymentLocation',)
            name = 'deploymentLocations'
            referencedType = 'Node'
            refTypeQN = 'Foundation.Core.Component.deploymentLocation'
            referencedEnd = 'residents'
    
    
        class residentElements(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Component.residentElement',)
            name = 'residentElements'
            referencedType = 'ElementResidence'
            refTypeQN = 'Foundation.Core.Component.residentElement'
            referencedEnd = 'implementationLocation'
    
        _XMINames = ('Foundation.Core.Component',)


    class Mapping(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.Mapping',)


    class CallState(ActionState):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Activity_Graphs.CallState',)








    class ClassifierRole(Classifier):
        isAbstract = 0
    
        class bases(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.base',)
            name = 'bases'
            referencedType = 'Classifier'
            refTypeQN = 'Behavioral_Elements.Collaborations.ClassifierRole.base'
            referencedEnd = 'classifierRoles'
    
    
        class messages1(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.message1',)
            name = 'messages1'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Collaborations.ClassifierRole.message1'
            referencedEnd = 'receiver'
    
    
        class multiplicity(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Collaborations.ClassifierRole.multiplicity'
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.multiplicity',)
            name = 'multiplicity'
            referencedType = 'Multiplicity'
    
        _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole',)
    
        class messages2(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.message2',)
            name = 'messages2'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Collaborations.ClassifierRole.message2'
            referencedEnd = 'sender'
    
        class availableFeatures(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.availableFeature',)
            name = 'availableFeatures'
            referencedType = 'Feature'
            refTypeQN = 'Behavioral_Elements.Collaborations.ClassifierRole.availableFeature'
            referencedEnd = 'classifierRoles'
    
    
        class availableContents(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.ClassifierRole.availableContents',)
            name = 'availableContents'
            referencedType = 'ModelElement'
            refTypeQN = 'Behavioral_Elements.Collaborations.ClassifierRole.availableContents'
            referencedEnd = 'classifierRoles'


    class Geometry(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.Geometry',)


    class UninterpretedAction(Action):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.UninterpretedAction',)


    class AssociationRole(Association):
        isAbstract = 0
    
        class multiplicity(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Collaborations.AssociationRole.multiplicity'
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationRole.multiplicity',)
            name = 'multiplicity'
            referencedType = 'Multiplicity'
    


        class base(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationRole.base',)
            name = 'base'
            referencedType = 'Association'
            refTypeQN = 'Behavioral_Elements.Collaborations.AssociationRole.base'
            referencedEnd = 'associationRoles'
    
        _XMINames = ('Behavioral_Elements.Collaborations.AssociationRole',)
    
        class messages(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.AssociationRole.message',)
            name = 'messages'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Collaborations.AssociationRole.message'
            referencedEnd = 'communicationConnection'

    class Interface(Classifier):
        isAbstract = 0
        _XMINames = ('Foundation.Core.Interface',)


    class TypeExpression(Expression):
        _XMINames = ('Foundation.Data_Types.TypeExpression',)


    class Interaction(ModelElement):
        isAbstract = 0
    
        class messages(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Interaction.message',)
            name = 'messages'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Collaborations.Interaction.message'
            referencedEnd = 'interaction'
    
        _XMINames = ('Behavioral_Elements.Collaborations.Interaction',)
    
        class context(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Interaction.context',)
            name = 'context'
            referencedType = 'Collaboration'
            refTypeQN = 'Behavioral_Elements.Collaborations.Interaction.context'
            referencedEnd = 'interactions'


    class ChangeEvent(Event):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.ChangeEvent',)
    
        class changeExpression(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.State_Machines.ChangeEvent.changeExpression'
            _XMINames = ('Behavioral_Elements.State_Machines.ChangeEvent.changeExpression',)
            name = 'changeExpression'
            referencedType = 'BooleanExpression'
    


    class Name(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.Name',)


    class Extension(Base):
        isAbstract = 0
        _XMINames = ('Extension',)
    
        class extenderID(model.Field):
            isRequired = 1
            qualifiedName = 'Extension.extenderID'
            _XMINames = ('Extension.extenderID',)
            name = 'extenderID'
            referencedType = 'String'
    
    
        class extender(model.Field):
            isRequired = 1
            qualifiedName = 'Extension.extender'
            _XMINames = ('Extension.extender',)
            name = 'extender'
            referencedType = 'String'
    
    
        class baseElement(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Extension.baseElement',)
            name = 'baseElement'
            referencedType = 'Base'
            refTypeQN = 'Extension.baseElement'
            referencedEnd = 'extensions'
    


    class ActivityGraph(StateMachine):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Activity_Graphs.ActivityGraph',)
    
        class partitions(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Activity_Graphs.ActivityGraph.partition',)
            name = 'partitions'
            referencedType = 'Partition'
            refTypeQN = 'Behavioral_Elements.Activity_Graphs.ActivityGraph.partition'
            referencedEnd = 'activityGraph'
    









    class Multiplicity(model.DataType):
    
        class ranges(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Data_Types.Multiplicity.range',)
            name = 'ranges'
            referencedType = 'MultiplicityRange'
            refTypeQN = 'Foundation.Data_Types.Multiplicity.range'
            referencedEnd = 'multiplicity'
    
        _XMINames = ('Foundation.Data_Types.Multiplicity',)


    class OrderingKind(model.Enumeration):
        sorted = 'sorted'
        _XMINames = ('Foundation.Data_Types.OrderingKind',)
        ordered = 'ordered'
        unordered = 'unordered'


    class Partition(ModelElement):

        isAbstract = 0
    
        class activityGraph(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Activity_Graphs.Partition.activityGraph',)
            name = 'activityGraph'
            referencedType = 'ActivityGraph'
            refTypeQN = 'Behavioral_Elements.Activity_Graphs.Partition.activityGraph'
            referencedEnd = 'partitions'
    
        _XMINames = ('Behavioral_Elements.Activity_Graphs.Partition',)






        class contents(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Activity_Graphs.Partition.contents',)
            name = 'contents'
            referencedType = 'ModelElement'
            refTypeQN = 'Behavioral_Elements.Activity_Graphs.Partition.contents'
            referencedEnd = 'partitions'

    class Pseudostate(StateVertex):

        isAbstract = 0
    
        class kind(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.State_Machines.Pseudostate.kind'
            _XMINames = ('Behavioral_Elements.State_Machines.Pseudostate.kind',)
            name = 'kind'
            referencedType = 'PseudostateKind'
    
        _XMINames = ('Behavioral_Elements.State_Machines.Pseudostate',)


    class CreateAction(Action):

        isAbstract = 0
    
        class instantiation(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.CreateAction.instantiation',)
            name = 'instantiation'
            referencedType = 'Classifier'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.CreateAction.instantiation'
            referencedEnd = 'createActions'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.CreateAction',)




    class AggregationKind(model.Enumeration):
        aggregate = 'aggregate'
        composite = 'composite'
        none = 'none'
        _XMINames = ('Foundation.Data_Types.AggregationKind',)


    class Reception(BehavioralFeature):

        isAbstract = 0
    
        class isAbstarct(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Reception.isAbstarct'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.isAbstarct',)
            name = 'isAbstarct'
            referencedType = 'Boolean'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Reception',)
    
        class isRoot(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Reception.isRoot'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.isRoot',)
            name = 'isRoot'
            referencedType = 'Boolean'
    
    
        class specification(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Reception.specification'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.specification',)
            name = 'specification'
            referencedType = 'String'
    






        class signal(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.signal',)
            name = 'signal'
            referencedType = 'Signal'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Reception.signal'
            referencedEnd = 'receptions'
    
    
        class isLeaf(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Reception.isLeaf'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Reception.isLeaf',)
            name = 'isLeaf'
            referencedType = 'Boolean'


    class ParameterDirectionKind(model.Enumeration):
        _XMINames = ('Foundation.Data_Types.ParameterDirectionKind',)
        out = 'out'
        return_ = 'return'
        inout = 'inout'
        in_ = 'in'


    class Model(Package):
        isAbstract = 0
        _XMINames = ('Model_Management.Model',)












    class Comment(ModelElement):

        isAbstract = 0

        _XMINames = ('Foundation.Core.Comment',)
    
        class annotatedElements(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Comment.annotatedElement',)
            name = 'annotatedElements'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Core.Comment.annotatedElement'
            referencedEnd = 'comments'
    

    class LinkEnd(ModelElement):

        isAbstract = 0
    
        class instance(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd.instance',)
            name = 'instance'
            referencedType = 'Instance'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.LinkEnd.instance'
            referencedEnd = 'linkEnds'
    
    
        class qualifiedValues(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd.qualifiedValue',)
            name = 'qualifiedValues'
            referencedType = 'AttributeLink'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.LinkEnd.qualifiedValue'
            referencedEnd = 'linkEnd'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd',)
    
        class link(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd.link',)
            name = 'link'
            referencedType = 'Link'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.LinkEnd.link'
            referencedEnd = 'connections'
    
    
        class associationEnd(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.LinkEnd.associationEnd',)
            name = 'associationEnd'
            referencedType = 'AssociationEnd'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.LinkEnd.associationEnd'
            referencedEnd = 'linkEnds'


    class ScopeKind(model.Enumeration):
        instance = 'instance'
        _XMINames = ('Foundation.Data_Types.ScopeKind',)
        classifier = 'classifier'


    class IterationExpression(Expression):
        _XMINames = ('Foundation.Data_Types.IterationExpression',)













    class Extend(Relationship):

        isAbstract = 0
    
        class base(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.Extend.base',)
            name = 'base'
            referencedType = 'UseCase'
            refTypeQN = 'Behavioral_Elements.Use_Cases.Extend.base'
            referencedEnd = 'extends2'
    
        _XMINames = ('Behavioral_Elements.Use_Cases.Extend',)
    
        class extensionPoints(model.Sequence):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.Extend.extensionPoint',)
            name = 'extensionPoints'
            referencedType = 'ExtensionPoint'
            refTypeQN = 'Behavioral_Elements.Use_Cases.Extend.extensionPoint'
            referencedEnd = 'extends'
    
    
        class extension(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Use_Cases.Extend.extension',)
            name = 'extension'
            referencedType = 'UseCase'
            refTypeQN = 'Behavioral_Elements.Use_Cases.Extend.extension'
            referencedEnd = 'extends'
    
        class condition(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Use_Cases.Extend.condition'
            _XMINames = ('Behavioral_Elements.Use_Cases.Extend.condition',)
            name = 'condition'
            referencedType = 'BooleanExpression'
    
    class OperationDirectionKind(model.Enumeration):
        provide = 'provide'
        require = 'require'
        _XMINames = ('Foundation.Data_Types.OperationDirectionKind',)


    class DataType(Classifier):
        isAbstract = 0
        _XMINames = ('Foundation.Core.DataType',)


    class Argument(ModelElement):
        isAbstract = 0
    
        class action(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Common_Behavior.Argument.action',)
            name = 'action'
            referencedType = 'Action'
            refTypeQN = 'Behavioral_Elements.Common_Behavior.Argument.action'
            referencedEnd = 'actualArguments'
    
        _XMINames = ('Behavioral_Elements.Common_Behavior.Argument',)
    
        class value(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.Common_Behavior.Argument.value'
            _XMINames = ('Behavioral_Elements.Common_Behavior.Argument.value',)
            name = 'value'
            referencedType = 'Expression'










    class Generalization(Relationship):

        isAbstract = 0
    
        class powertype(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Generalization.powertype',)
            name = 'powertype'
            referencedType = 'Classifier'
            refTypeQN = 'Foundation.Core.Generalization.powertype'
            referencedEnd = 'powertypeRanges'
    
        _XMINames = ('Foundation.Core.Generalization',)
    
        class parent(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Generalization.parent',)
            name = 'parent'
            referencedType = 'GeneralizableElement'
            refTypeQN = 'Foundation.Core.Generalization.parent'
            referencedEnd = 'specializations'
    
    
        class child(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Core.Generalization.child',)
            name = 'child'
            referencedType = 'GeneralizableElement'
            refTypeQN = 'Foundation.Core.Generalization.child'
            referencedEnd = 'generalizations'    
    
        class discriminator(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Core.Generalization.discriminator'
            _XMINames = ('Foundation.Core.Generalization.discriminator',)
            name = 'discriminator'
            referencedType = 'Name'
    
    class Stereotype(GeneralizableElement):

        isAbstract = 0
    
        class extendedElements(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.extendedElement',)
            name = 'extendedElements'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Extension_Mechanisms.Stereotype.extendedElement'
            referencedEnd = 'stereotype'
    
        _XMINames = ('Foundation.Extension_Mechanisms.Stereotype',)
    
        class stereotypeConstraints(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.stereotypeConstraint',)
            name = 'stereotypeConstraints'
            referencedType = 'Constraint'
            refTypeQN = 'Foundation.Extension_Mechanisms.Stereotype.stereotypeConstraint'
            referencedEnd = 'constrainedElement2'
    
    
        class icon(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Extension_Mechanisms.Stereotype.icon'
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.icon',)
            name = 'icon'
            referencedType = 'Geometry'
    
    
        class baseClass(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Extension_Mechanisms.Stereotype.baseClass'
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.baseClass',)
            name = 'baseClass'
            referencedType = 'Name'
    
    
        class requiredTags(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Extension_Mechanisms.Stereotype.requiredTag',)
            name = 'requiredTags'
            referencedType = 'TaggedValue'
            refTypeQN = 'Foundation.Extension_Mechanisms.Stereotype.requiredTag'
            referencedEnd = 'stereotype'
    

    class Guard(ModelElement):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.State_Machines.Guard',)
    
        class transition(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.State_Machines.Guard.transition',)
            name = 'transition'
            referencedType = 'Transition'
            refTypeQN = 'Behavioral_Elements.State_Machines.Guard.transition'
            referencedEnd = 'guard'
    
    
        class expression(model.Field):
            isRequired = 1
            qualifiedName = 'Behavioral_Elements.State_Machines.Guard.expression'
            _XMINames = ('Behavioral_Elements.State_Machines.Guard.expression',)
            name = 'expression'
            referencedType = 'BooleanExpression'
    


    class Boolean(model.PrimitiveType):
        _XMINames = ('Foundation.Data_Types.Boolean',)






    class TaggedValue(Element):

        isAbstract = 0
    
        class tag(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Extension_Mechanisms.TaggedValue.tag'
            _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue.tag',)
            name = 'tag'
            referencedType = 'Name'
    
        _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue',)
    
        class stereotype(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue.stereotype',)
            name = 'stereotype'
            referencedType = 'Stereotype'
            refTypeQN = 'Foundation.Extension_Mechanisms.TaggedValue.stereotype'
            referencedEnd = 'requiredTags'
    
    
        class modelElement(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue.modelElement',)
            name = 'modelElement'
            referencedType = 'ModelElement'
            refTypeQN = 'Foundation.Extension_Mechanisms.TaggedValue.modelElement'
            referencedEnd = 'taggedValues'
    
    
        class value(model.Field):
            isRequired = 1
            qualifiedName = 'Foundation.Extension_Mechanisms.TaggedValue.value'
            _XMINames = ('Foundation.Extension_Mechanisms.TaggedValue.value',)
            name = 'value'
            referencedType = 'String'
    

    class Message(ModelElement):

        isAbstract = 0
    
        class interaction(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.interaction',)
            name = 'interaction'
            referencedType = 'Interaction'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.interaction'
            referencedEnd = 'messages'
        
        class sender(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.sender',)
            name = 'sender'
            referencedType = 'ClassifierRole'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.sender'
            referencedEnd = 'messages2'    
    
        class messages4(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.message4',)
            name = 'messages4'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.message4'
            referencedEnd = 'activator'
    
        class communicationConnection(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.communicationConnection',)
            name = 'communicationConnection'
            referencedType = 'AssociationRole'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.communicationConnection'
            referencedEnd = 'messages'


        _XMINames = ('Behavioral_Elements.Collaborations.Message',)
    
        class messages3(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.message3',)
            name = 'messages3'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.message3'
            referencedEnd = 'predecessors'
    
    
        class receiver(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.receiver',)
            name = 'receiver'
            referencedType = 'ClassifierRole'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.receiver'
            referencedEnd = 'messages1'
    
    
        class activator(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.activator',)
            name = 'activator'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.activator'
            referencedEnd = 'messages4'
    
    
        class action(model.Reference):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.action',)
            name = 'action'
            referencedType = 'Action'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.action'
            referencedEnd = 'messages'
    
        class predecessors(model.Collection):
            isNavigable = 1
            isRequired = 1
            _XMINames = ('Behavioral_Elements.Collaborations.Message.predecessor',)
            name = 'predecessors'
            referencedType = 'Message'
            refTypeQN = 'Behavioral_Elements.Collaborations.Message.predecessor'
            referencedEnd = 'messages3'
    


    class DataValue(Instance):
        isAbstract = 0
        _XMINames = ('Behavioral_Elements.Common_Behavior.DataValue',)


setupModule()


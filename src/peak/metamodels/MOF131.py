"""MOF 1.3.1 implementation as a PEAK domain model - far from finished yet"""

from peak.api import *
from kjbuckets import *

from peak.model.datatypes import Name, String, Boolean, Integer, \
    UnlimitedInteger, UNBOUNDED

__all__ = [
    'Name', 'String', 'Boolean', 'Integer', 'UnlimitedInteger', 'UNBOUNDED',
    'AnnotationType', 'DependencyKind', 'FormatType', 'CONTAINER_DEP',
    'CONTENTS_DEP', 'SIGNATURE_DEP', 'CONSTRAINED_ELEMENTS_DEP',
    'SPECIALIZATION_DEP', 'IMPORT_DEP', 'TYPE_DEFINITION_DEP',
    'REFERENCED_ENDS_DEP', 'TAGGED_ELEMENTS_DEP', 'INDIRECT_DEP', 'ALL_DEP',
    'MultiplicityType', 'VisibilityKind', 'DepthKind', 'DirectionKind',
    'ScopeKind', 'AggregationKind', 'EvaluationKind', 'LiteralType,
    'VerifyResultKind', 'ViolationType', 'NameNotFound', 'NameNotResolved',
    'ObjectNotExternalizable', 'FormatNotSupported',
    'IllformedExternalizedObject', 'MOFModel',
]

AnnotationType = DependencyKind = FormatType = String


CONTAINER_DEP = 'container'
CONTENTS_DEP = 'contents'
SIGNATURE_DEP = 'signature'
CONSTRAINT_DEP = 'constraint'
CONSTRAINED_ELEMENTS_DEP = 'constrained elements'
SPECIALIZATION_DEP = 'specialization'
IMPORT_DEP = 'import'
TYPE_DEFINITION_DEP = 'type definition'
REFERENCED_ENDS_DEP = 'referenced ends'
TAGGED_ELEMENTS_DEP = 'tagged elements'
INDIRECT_DEP = 'indirect'
ALL_DEP = 'all'





class MultiplicityType(model.Immutable):

    class lower(model.Field):
        fieldOrder = 1
        referencedType = Integer

    class upper(model.Field)
        fieldOrder = 2
        referencedType = UnlimitedInteger

    class isOrdered(model.Field):
        fieldOrder = 3
        referencedType = Boolean

    class isUnique(model.Field):
        fieldOrder = 4
        referencedType = Boolean



class VisibilityKind(model.Enumeration):
    public_vis = 'public_vis'
    protected_vis = 'protected_vis'
    private_vis = 'private_vis'



class DepthKind(model.Enumeration):
    shallow = 'shallow'
    deep = 'deep'



class DirectionKind(model.Enumeration):
    in_dir = 'in_dir'
    out_dir = 'out_dir'
    inout_dir = 'inout_dir'
    return_dir = 'return_dir'
    


class ScopeKind(model.Enumeration):
    instance_level = 'instance_level'
    classifier_level = 'classifier_level'


class AggregationKind(model.Enumeration):
    none = 'none'
    shared = 'shared'
    composite = 'composite'


class EvaluationKind(model.Enumeration):
    immediate = 'immediate'
    deferred = 'deferred'


class LiteralType(model.PrimitiveType):
    pass


class VerifyResultKind(model.Enumeration):
    valid = 'valid'
    invalid = 'invalid'
    published = 'published'


class ViolationType(model.Immutable):

    class errorKind(model.Field):
        referencedType = String

    class elementInError(model.Reference):
        referencedType = 'MOFModel/ModelElement'

    class valuesInError(model.Field):
        pass    # XXX

    class errorDescription(model.Field):
        referencedType = String


class NameNotFound(Exception):
    pass    # name


class NameNotResolved(Exception):
    pass    # explanation, restOfName
            # explanation in ('InvalidName','MissingName','NotNameSpace',
            #   'CannotProceed')


class ObjectNotExternalizable(Exception):
    pass


class FormatNotSupported(Exception):
    pass


class IllformedExternalizedObject(Exception):
    pass





















class MOFModel(model.Model):

    class ModelElement(model.Element):
    
        mdl_isAbstract = True

        class name(model.Field):
            referencedType = Name

        class annotation(model.Field):
            referencedType = AnnotationType

        class qualifiedName(model.DerivedAssociation):
        
            def get(feature, element):
                names = [element.name]
                while element.container is not None:
                    element = element.container
                    names.insert(0,element.name)
                return names

            def _getList(feature, element):
                return [feature.get(element)]

        class container(model.Reference):
            referencedType = 'Namespace'
            referencedEnd  = 'contents'

        class requiredElements(model.DerivedAssociation):
            def _getList(feature, element):
                return element.findRequiredElements()

        class constraints(model.Collection):
            referencedType = 'Constraint'
            referencedEnd  = 'constrainedElements'






        def _visitDependencies(self,visitor):
            if self.container is not None:
                visitor(CONTAINER_DEP,[self.container])
            if self.constraints:
                visitor(CONSTRAINT_DEP,self.constraints)


        def isVisible(self,otherElement):
            return True


        def verify(self, depth=DepthKind.shallow):  # XXX
            raise NotImplementedError




























        def isRequiredBecause(self, otherElement):

            """Dependency kind (or 'None') between this and 'otherElement'"""

            stack = [self]; push = stack.push; pop = stack.pop
            output = []; append = output.append

            visitedObjects = kjSet([id(self)])
            haveVisited = visitedObjects.member
            visit = visitedObjects.add
            
            def visitor(kind,items):

                for item in items:
                    if item is otherElement:
                        append(kind)
                        return

                    ii = id(item)
                    if not haveVisited(ii):
                        visit(ii)
                        push(item)

            while stack and not output:
                pop()._visitDependencies(visitor)

            if output:
                return output[0]

            return None











        def findRequiredElements(self, kinds=(ALL_DEP,), recursive=False):

            """List elements this one depends on by 'kinds' relationships"""

            kindSet = kjSet(list(kinds))

            if kindSet.member(ALL_DEP):
                # include all dependency types
                include = lambda x: 1
            else:
                # include only types specified
                include = kindSet.member

            output = []; append = output.append
            visitedObjects = kjSet([id(self)])
            haveVisited = visitedObjects.member
            visit = visitedObjects.add
            
            def visitor(kind,items):

                if include(kind):

                    for item in items:
                        ii = id(item)

                        if not haveVisited(ii):
                            append(item)
                            visit(ii)

                            if recursive:
                                item._visitDependencies(visitor)
            
            self._visitDependencies(visitor)
            return output







    class Namespace(ModelElement):


        mdl_isAbstract = True


        class contents(model.Sequence):
        
            referencedType = 'ModelElement'
            referencedEnd  = 'container'

            def validateAdd(feature, element, item):    # XXX

                if not element.nameIsValid(item):
                    raise KeyError("Item already exists with name",item.name)

                if not isinstance(item, element.__class__._allowedContents):
                    raise TypeError("Invalid content for container",item)


        def lookupElement(self, name):
            for ob in self.contents:
                if ob.name==name:
                    return ob
            raise NameNotFound(name)


        def resolvedQualifiedName(self, qualifiedName):
            i=0
            ns=self
            for name in qualifiedName:
                if not isinstance(s, MOFModel.Namespace):
                    raise NameNotResolved('NotNameSpace',qualifiedName[i:])
                try:
                    ns = ns.lookupElement(name)
                except NameNotFound:
                    raise NameNotResolved('MissingName',qualifiedName[i:])
                i+=1                    
            return ns


        def nameIsValid(self,proposedName):
            for ob in self.contents:
                if ob.name==proposedName:
                    return False
            else:
                return True


        def findElementsByType(self, ofType, includeSubtypes=True):
            if includeSubtypes:
                return [ob for ob in self.contents if isinstance(ob,ofType)]
            return [ob for ob in self.contents if type(ob) is ofType]


        def _visitDependencies(self,visitor):
            if self.contents:
                visitor(CONTENTS_DEP,self.contents)
            super(MOFModel.Namespace,self)._visitDependencies(visitor)























    class GeneralizableElement(Namespace):

        mdl_isAbstract = True

        class visibility(model.Field):
            referencedType = VisibilityKind
            defaultValue = VisibilityKind.public_vis

        class isAbstract(model.Field):
            referencedType = Boolean
            defaultValue = False

        class isRoot(model.Field):
            referencedType = Boolean
            defaultValue = False

        class isLeaf(model.Field):
            referencedType = Boolean
            defaultValue = False

        class supertypes(model.Sequence):
        
            referencedType = 'GeneralizableElement'
            # XXX referencedEnd  = 'subtypes'

            def validateAdd(feature, element, item):    # XXX

                if not isinstance(item,element.__class__):
                    raise TypeError("Can't inherit from different type",item)

                if element.isRoot:
                    raise ValueError("Root type can't inherit",element)

                if item.isLeaf:
                    raise ValueError("Can't subtype leaf", item)

                if element in item.allSupertypes():
                    raise ValueError("Circular inheritance",item)
                    
                # XXX Diamond rule, visibility, name collisions

        def allSupertypes(self):
            output=[]
            for base in self.supertypes:
                output.append(base)
                for base in base.allSupertypes():
                    if base in output:
                        output.remove(base)
                    output.append(base)
            return output


        def _visitDependencies(self,visitor):
            if self.supertypes:
                visitor(SPECIALIZATION_DEP,self.supertypes)
            super(MOFModel.GeneralizableElement,self)._visitDependencies(visitor)


    class Import(ModelElement):

        def _visitDependencies(self,visitor):
            if self.importedNamespace is not None:
                visitor(IMPORT_DEP,[self.importedNamespace])
            super(MOFModel.Import,self)._visitDependencies(visitor)
            

    class Constraint(ModelElement):

        def _visitDependencies(self,visitor):
            if self.constrainedElements:
                visitor(CONSTRAINED_ELEMENTS_DEP,self.constrainedElements)
            super(MOFModel.Constraint,self)._visitDependencies(visitor)


    class Tag(ModelElement):

        def _visitDependencies(self,visitor):
            if self.elements:
                visitor(TAGGED_ELEMENTS_DEP,self.elements)
            super(MOFModel.Tag,self)._visitDependencies(visitor)


    class Package(GeneralizableElement):

        _allowedContents = binding.classAttr(

            binding.bindSequence(
                'Package','Class','DataType','Exception','Constraint',
                'Constant', 'Tag',
            )

        )

    class Classifier(GeneralizableElement):

        mdl_isAbstract = True


    class Association(Classifier):

        _allowedContents = binding.classAttr(
            binding.bindSequence('AssociationEnd','Constraint','Tag')
        )


    class DataType(Classifier):

        _allowedContents = binding.classAttr(
            binding.bindSequence('Constraint','TypeAlias','Tag')
        )


    class Class(Classifier):

        _allowedContents = binding.classAttr(
            binding.bindSequence(
                'Class', 'DataType', 'Attribute', 'Reference', 'Operation',
                'Exception','Constraint','Constant','Tag'
            )
        )



    class Feature(ModelElement):

        mdl_isAbstract = True


    class BehavioralFeature(Namespace, Feature):

        mdl_isAbstract = True


    class Operation(BehavioralFeature):

        _allowedContents = binding.classAttr(
            binding.bindSequence('Parameter','Constraint','Tag')
        )

        def _visitDependencies(self,visitor):

            if self.exceptions:
                visitor(SIGNATURE_DEP,self.exceptions)

            # XXX should this also do parameters?

            super(MOFModel.Operation,self)._visitDependencies(visitor)


    class Exception(BehavioralFeature):

        _allowedContents = binding.classAttr(
            binding.bindSequence('Parameter','Tag')
        )










    class TypedElement(ModelElement):

        mdl_isAbstract = True

        def _visitDependencies(self,visitor):

            if self.type is not None:
                visitor(TYPE_DEFINITION_DEP,[self.type])

            super(MOFModel.TypedElement,self)._visitDependencies(visitor)


    class TypeAlias(TypedElement):
        pass

    class Constant(TypedElement):
        pass

    class Parameter(TypedElement):
        pass

    class AssociationEnd(TypedElement):
        pass


















    class StructuralFeature(Feature,TypedElement):

        mdl_isAbstract = True


    class Attribute(StructuralFeature):
        pass


    class Reference(StructuralFeature):

        def _visitDependencies(self,visitor):

            ends = []
            
            if self.referencedEnd is not None:
                ends.append(self.referencedEnd)

            if self.exposedEnd is not None:
                ends.append(self.exposedEnd)

            if ends:
                visitor(REFERENCED_ENDS_DEP,ends)

            super(MOFModel.Reference,self)._visitDependencies(visitor)

    

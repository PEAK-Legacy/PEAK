"""MOF 1.3.1 implementation as a PEAK domain model - far from finished yet"""

from __future__ import generators
from peak.api import *
from kjbuckets import *
from peak.util.imports import importObject
from peak.model.datatypes import Name, String, Boolean, Integer, \
    UnlimitedInteger, TypeCode

__all__ = [
    'Name', 'String', 'Boolean', 'Integer', 'UnlimitedInteger',
    'AnnotationType', 'DependencyKind', 'FormatType', 'CONTAINER_DEP',
    'CONTENTS_DEP', 'SIGNATURE_DEP', 'CONSTRAINED_ELEMENTS_DEP',
    'SPECIALIZATION_DEP', 'IMPORT_DEP', 'TYPE_DEFINITION_DEP',
    'REFERENCED_ENDS_DEP', 'TAGGED_ELEMENTS_DEP', 'INDIRECT_DEP', 'ALL_DEP',
    'MultiplicityType', 'VisibilityKind', 'DepthKind', 'DirectionKind',
    'ScopeKind', 'AggregationKind', 'EvaluationKind', 'LiteralType',
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

_readers = PropertyName('peak.metamodels.mof1.3.readers.*')
_writers = PropertyName('peak.metamodels.mof1.3.writers.*')

class MultiplicityType(model.DataType):

    class lower(model.structField):
        sortPosn = 1
        referencedType = Integer

    class upper(model.structField):
        sortPosn = 2
        referencedType = UnlimitedInteger

    class isOrdered(model.structField):
        sortPosn = 3
        referencedType = Boolean

    class isUnique(model.structField):
        sortPosn = 4
        referencedType = Boolean



class VisibilityKind(model.Enumeration):
    public_vis = model.enum()
    protected_vis = model.enum()
    private_vis = model.enum()



class DepthKind(model.Enumeration):
    shallow = model.enum()
    deep = model.enum()



class DirectionKind(model.Enumeration):
    in_dir = model.enum()
    out_dir = model.enum()
    inout_dir = model.enum()
    return_dir = model.enum()
    


class ScopeKind(model.Enumeration):
    instance_level = model.enum()
    classifier_level = model.enum()


class AggregationKind(model.Enumeration):
    none = model.enum()
    shared = model.enum()
    composite = model.enum()


class EvaluationKind(model.Enumeration):
    immediate = model.enum()
    deferred = model.enum()


class LiteralType(model.PrimitiveType):
    pass


class VerifyResultKind(model.Enumeration):
    valid = model.enum()
    invalid = model.enum()
    published = model.enum()


class ViolationType(model.DataType):

    class errorKind(model.structField):
        referencedType = String

    class elementInError(model.structField):
        referencedType = 'MOFModel/ModelElement'

    class valuesInError(model.structField):
        referencedType = model.PrimitiveType    # XXX !

    class errorDescription(model.structField):
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





















class MOFModel(model.Model, storage.xmi.Loader):

    class ModelElement(model.Element):
    
        mdl_isAbstract = True

        class name(model.Field):
            referencedType = Name

        class annotation(model.Field):
            referencedType = AnnotationType
            defaultValue = None

        class qualifiedName(model.DerivedAssociation):

            upperBound = 1  # singular

            def _getList(feature, element):
                names = [element.name]
                while element.container is not None:
                    element = element.container
                    names.insert(0,element.name)
                return [names]

        class container(model.Reference):
            referencedType = 'Namespace'
            referencedEnd  = 'contents'
            defaultValue = None

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

        _contentsIndex = binding.Once(
            lambda s,d,a: dict([
                (ob.name, ob) for ob in s.contents
            ])
        )


        class contents(model.Sequence):
        
            referencedType = 'ModelElement'
            referencedEnd  = 'container'
            isComposite    = True

            def _onLink(feature, element, item, posn=None):

                if not element.nameIsValid(item.name):
                    raise KeyError("Item already exists with name",item.name)

                if not isinstance(item, element.__class__._allowedContents):
                    raise TypeError("Invalid content for container",item)
                    
                element._contentsIndex[item.name]=item


            def _onUnlink(feature, element, item, posn=None):
                del element._contentsIndex[item.name]


        def lookupElement(self, name):
            try:
                return self._contentsIndex[name]
            except KeyError:
                raise NameNotFound(name)




        def resolveQualifiedName(self, qualifiedName):

            i=0
            ns=self

            for name in qualifiedName:

                if not isinstance(ns, MOFModel.Namespace):
                    raise NameNotResolved('NotNameSpace',qualifiedName[i:])

                try:
                    ns = ns.lookupElement(name)
                except NameNotFound:
                    raise NameNotResolved('MissingName',qualifiedName[i:])
                i+=1                    

            return ns


        def nameIsValid(self,proposedName):
            return proposedName not in self._contentsIndex


        def findElementsByType(self, ofType, includeSubtypes=True):
            # XXX should package treat imports specially?
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


        def _MRO(self, d, a):

            output=[self]

            for base in self.supertypes:

                for base in base._MRO:

                    if base in output:
                        output.remove(base)

                    output.append(base)

            return output

        _MRO = binding.Once(_MRO)




        class supertypes(model.Sequence):
        
            referencedType = 'GeneralizableElement'

            def _onLink(feature, element, item, posn=None):

                if not isinstance(item,element.__class__):
                    raise TypeError("Can't inherit from different type",item)

                if element.isRoot:
                    raise ValueError("Root type can't inherit",element)

                if item.isLeaf:
                    raise ValueError("Can't subtype leaf", item)

                if element in item.allSupertypes():
                    raise ValueError("Circular inheritance",item)
                    
                element._delBinding('_MRO')

                # XXX Diamond rule, visibility, name collisions


            def _onUnlink(feature, element, item, posn=None):
                element._delBinding('_MRO')
            

        def allSuperTypes(self):
            return self._MRO[1:]


        def _visitDependencies(self,visitor):

            if self.supertypes:
                visitor(SPECIALIZATION_DEP,self.supertypes)

            super(MOFModel.GeneralizableElement,self)._visitDependencies(
                visitor
            )


        def _extMRO(self):

            seen = {}   # ensure each namespace is returned only once
            
            for ns in self._MRO:

                if ns in seen: continue
                seen[ns] = True

                yield ns


        def lookupElementExtended(self,name):

            for ns in self._extMRO():
                try:
                    return ns.lookupElement(name)
                except NameNotFound:
                    pass

            raise NameNotFound(name)


        def findElementsByTypeExtended(self, ofType, includeSubtypes=True):

            output = []
            names = {}
            
            for ns in self._extMRO():
                for item in ns.findElementsByType(ofType,includeSubtypes):
                    if item.name in names: continue
                    names[item.name]=item; output.append(item)

            return output







    class Import(ModelElement):

        def _visitDependencies(self,visitor):
            if self.importedNamespace is not None:
                visitor(IMPORT_DEP,[self.importedNamespace])
            super(MOFModel.Import,self)._visitDependencies(visitor)
            
        class visibility(model.Field):
            referencedType = VisibilityKind
            defaultValue = VisibilityKind.public_vis

        class isClustered(model.Field):
            referencedType = Boolean
            defaultValue = False

        class importedNamespace(model.Reference):
            referencedType = 'Namespace'


    class Constraint(ModelElement):

        def _visitDependencies(self,visitor):
            if self.constrainedElements:
                visitor(CONSTRAINED_ELEMENTS_DEP,self.constrainedElements)
            super(MOFModel.Constraint,self)._visitDependencies(visitor)

        class expression(model.Field):
            referencedType = model.PrimitiveType    # XXX 'Any'

        class language(model.Field):
            referencedType = String

        class evaluationPolicy(model.Field):
            referencedType = EvaluationKind

        class constrainedElements(model.Collection):
            referencedType = 'ModelElement'




    class Tag(ModelElement):

        def _visitDependencies(self,visitor):
            if self.elements:
                visitor(TAGGED_ELEMENTS_DEP,self.elements)
            super(MOFModel.Tag,self)._visitDependencies(visitor)

        class tagId(model.Field):
            referencedType = String

        class values(model.Field):
            referencedType = model.PrimitiveType  # XXX 'Any'
            upperBound = None

        class elements(model.Collection):
            referencedType = 'ModelElement'

























    class Package(GeneralizableElement):

        _allowedContents = binding.classAttr(

            binding.bindSequence(
                'Package','Class','DataType','Association','Exception',
                'Constraint', 'Constant', 'Import', 'Tag',
            )

        )



        def externalize(self, format='peak.model', **options):

            externalize = importObject(_writers.of(self).get(format))

            if externalize is None:
                raise FormatNotSupported(format)

            return externalize(MOFModel, self, format, **options)



        def internalize(klass, format, stream, **options):

            internalize = importObject(_readers.of(klass).get(format))

            if internalize is None:
                raise FormatNotSupported(format)

            return internalize(MOFModel, klass, format, stream, **options)


        internalize = classmethod(internalize)






    class Classifier(GeneralizableElement):

        mdl_isAbstract = True


    class Association(Classifier):

        class isDerived(model.Field):
            referencedType = Boolean
            defaultValue = False


        _allowedContents = binding.classAttr(
            binding.bindSequence('AssociationEnd','Constraint','Tag')
        )


























    class DataType(Classifier):

        _allowedContents = binding.classAttr(
            binding.bindSequence('Constraint','TypeAlias','Tag')
        )


        class typeCode(model.Field):
            referencedType = TypeCode

        class supertypes(model.Sequence):
            upperBound = 0  # no supertypes allowed


        class isRoot(model.structField):
            referencedType = Boolean
            defaultValue = True

        class isLeaf(model.structField):
            referencedType = Boolean
            defaultValue = True

        class isAbstract(model.structField):
            referencedType = Boolean
            defaultValue = False


    class Class(Classifier):

        _allowedContents = binding.classAttr(
            binding.bindSequence(
                'Class', 'DataType', 'Attribute', 'Reference', 'Operation',
                'Exception','Constraint','Constant','Tag'
            )
        )

        class isSingleton(model.Field):
            referencedType = Boolean
            defaultValue = False


    class Feature(ModelElement):

        mdl_isAbstract = True

        class visibility(model.Field):
            referencedType = VisibilityKind

        class scope(model.Field):
            referencedType = ScopeKind
































    class BehavioralFeature(Namespace, Feature):

        mdl_isAbstract = True


    class Operation(BehavioralFeature):

        class isQuery(model.Field):
            referencedType = Boolean
            defaultValue = False


        class exceptions(model.Sequence):
            referencedType = 'Exception'


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

        class type(model.Reference):    # XXX ugh
            referencedType = 'Classifier'
            lowerBound = 1  # XXX what are semantics of 'required' attrs?


        def _visitDependencies(self,visitor):

            if self.type is not None:
                visitor(TYPE_DEFINITION_DEP,[self.type])

            super(MOFModel.TypedElement,self)._visitDependencies(visitor)


    class TypeAlias(TypedElement):
        pass


    class Constant(TypedElement):

        class value(model.Field):
            referencedType = LiteralType


    class Parameter(TypedElement):

        class direction(model.Field):
            referencedType = DirectionKind

        class multiplicity(model.Field):
            referencedType = MultiplicityType







    class AssociationEnd(TypedElement):

        class multiplicity(model.Field):
            referencedType = MultiplicityType

        class aggregation(model.Field):
            referencedType = AggregationKind

        class isNavigable(model.Field):
            referencedType = Boolean
            defaultValue = True

        class isChangeable(model.Field):
            referencedType = Boolean
            defaultValue = True

        def otherEnd(self):
            # return first sibling that isn't me...
            for e in self.container.contents:
                if isinstance(e,MOFModel.AssociationEnd) and e is not self:
                    return e
                    



















    class StructuralFeature(Feature,TypedElement):

        mdl_isAbstract = True

        class multiplicity(model.Field):
            referencedType = MultiplicityType

        class isChangeable(model.Field):
            referencedType = Boolean
            defaultValue = True


    class Attribute(StructuralFeature):

        class isDerived(model.Field):
            referencedType = Boolean
            defaultValue = False
























    class Reference(StructuralFeature):

        class referencedEnd(model.Reference):
            referencedType = 'AssociationEnd'
            defaultValue = None

        class exposedEnd(model.Reference):
            referencedType = 'AssociationEnd'
            defaultValue = None

        def _visitDependencies(self,visitor):

            ends = []
            
            if self.referencedEnd is not None:
                ends.append(self.referencedEnd)

            if self.exposedEnd is not None:
                ends.append(self.exposedEnd)

            if ends:
                visitor(REFERENCED_ENDS_DEP,ends)

            super(MOFModel.Reference,self)._visitDependencies(visitor)



    # We need MultiplicityType to be part of the model, in case it's encoded
    # as such...  technically that's not supposed to happen, but the 'nsuml'
    # metamodel for UML 1.3 references it as though it were an object class.
    # So much for adherence to specs...  :(

    MultiplicityType = MultiplicityType

    NameNotFound = NameNotFound
    NameNotResolved = NameNotResolved

from types import StringType, FunctionType

from TW.StructuralModel.Queries import NodeList
from TW.StructuralModel.Features import ComputedFeature  #, StructuralModel


from TW.Utilities import Pluralizer

UMLPlurals = Pluralizer(
    stimulus='stimuli',
    subvertex='subvertices',
    classifierinstate='classifiersInState',
    contents='contents',
    availablecontents='availableContents',
)


from os.path import join,dirname

DIR = dirname(__file__)

mmx     = join(DIR,'metamodel.xml')
cache   = mmx+'.pickle'

import MMX
MetaModel = MMX.load(mmx,cache,UMLPlurals,name='UML_MetaModel')















from TW.Components import Catalyst

class _ComputedFeatures(Catalyst):

    def transformSpecification(self,featureDict):
    
        if featureDict:
            for k,v in featureDict.items():
                if type(v) is FunctionType:
                    featureDict[k]=ComputedFeature(v)
                    
        return featureDict
        
ComputedFeatures = _ComputedFeatures('')



























class _UMLModel:    # stuff that still needs refactoring

    class Integer:

        _defaultValue = 0
    
        def _convert(self,value):
            return int(value)


    class UnlimitedInteger:
    
        _defaultValue = '*'
    
        def _convert(self,value):
            if value=='*': return '*'
            return int(value)


    class String:
        _defaultValue = ''
    
        def _convert(self,value):
            return str(value)


    Name = String


    class Boolean:

        def _convert(self,value):
            return value and value != 'false'

        def _repr(self,value):
            return value and "Boolean('true')" or "Boolean('false')"





    class Multiplicity:
    
        def _convert(self,value):
        
            if type(value) is StringType:
                from string import split
                rl=[]
                for r in map(MultiplicityRange,split(value,',')):
                    rl.append(r.__of__(self.keyToItem.im_self))
                return self.newItem(self._ElementType,ranges=rl)


    class MultiplicityRange:

        def _convert(self,value):
    
            if type(value) is StringType:
                from string import split
                l = split(value,'..')
                if len(l)>2:
                    raise ValueError,"Invalid multiplicity range '%s'" % value
                if len(l)==2:
                    return self.__class__(lower=l[0],upper=l[1])
                elif l[0]=='*':
                    return self.__class__(lower=0,upper=l[0])
                else:
                    return self.__class__(lower=l[0],upper=l[0])
                
            self.inheritedAttribute('_convert')(value)

        def __repr__(self):
            return self._repr(self)
        
        def _repr(self,value):
            u,l = value.upper(), value.lower()
            if u==l: return "MultiplicityRange(%s)" % u
            return "MultiplicityRange(%s..%s)" % (l,u)




class UMLModel:

    class ModelElement(ComputedFeatures):
    
        def QualifiedName(self):
            name = self.name()
            if not name:
                return NodeList([])
                
            names = self.Get('namespace*').Get('name')
            names.reverse(); names.append(name)
            
            from string import join
            return NodeList([join(names,'.')])


    class GeneralizableElement(ComputedFeatures):
    
        def superclasses(self):
            return self.generalizations.Get('parent')

        def subclasses(self):
            return self.specializations.Get('child')


from types import StringType, FunctionType

from TW.RootModel.Queries import NodeList
from TW.RootModel._Aspects import ComputedFeature  #, RootModel
from TW.Features import Transform, FeatureSet


class _ComputedFeatures(Transform):

    def transform(self,maker,dict,verticalContext):
        for k,v in dict.items():
            if type(v) is FunctionType:
                maker[k]=ComputedFeature(v)
        
ComputedFeatures = _ComputedFeatures()


from TW.RootModel import RMX
from os.path import join,dirname

DIR = dirname(__file__)

rmx     = join(DIR,'metamodel.xml')
plurals = join(DIR,'plurals.txt')
cache   = rmx+'.pickle'

MetaModel = RMX.load(rmx,plurals,cache,name='UML_MetaModel')














class UMLModel(MetaModel):  # XXX needs RootModel, too

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




    class ModelElement:
    
        __features__ = FeatureSet(ComputedFeatures)
        
        def QualifiedName(self):
            name = self.name()
            if not name:
                return NodeList([])
                
            names = self.Get('namespace*').Get('name')
            names.reverse(); names.append(name)
            
            from string import join
            return NodeList([join(names,'.')])


    class GeneralizableElement:
    
        __features__ = FeatureSet(ComputedFeatures)
        
        def superclasses(self):
            return self.generalizations.Get('parent')

        def subclasses(self):
            return self.specializations.Get('child')


"""Domain logic and convenience features for manipulating UML Models

    This module adds a couple of domain logic features to the 'UMLClass'
    class family defined by 'peak.metamodels.uml.MetaModel'.  Specifically,
    it adds some computed features, such as the notion of a "qualified name"
    of a UML model element, and the "superclasses" and "subclasses" of UML
    generalizable elements.

    It also redefines 'model' to be 'peak.metamodels.SimpleModel', which adds
    querying and XMI reading aspects to the basic in-memory structural model.
"""

from peak.api import *
import peak.metamodels.uml.MetaModel
import peak.metamodels.SimpleModel as model
from types import StringType, FunctionType
from peak.metamodels.querying import NodeList, ComputedFeature

__bases__ = peak.metamodels.uml.MetaModel,






















class UMLClass(model.App):

    class ModelElement:
    
        def QualifiedName(self):
            name = self.name()
            if not name:
                return NodeList([])
                
            names = self.Get('namespace*').Get('name')
            names.reverse(); names.append(name)
            
            return NodeList(['.'.join(names)])

        QualifiedName = ComputedFeature(QualifiedName)


    class GeneralizableElement:
    
        def superclasses(self):
            return self.generalizations.Get('parent')

        superclasses = ComputedFeature(superclasses)
        
        def subclasses(self):
            return self.specializations.Get('child')

        subclasses = ComputedFeature(subclasses)


config.setupModule()










# Everything from here down is commented out for now...

'''
# Old stuff -- hanging onto it until we have a standard way to generate
# peak.metamodels.uml.MetaModel directly from the formal XMI
# specification of UML

from peak.util.Pluralizer import Pluralizer

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

from peak.metamodels.mof import MMX
MetaModel = MMX.load(mmx,cache,UMLPlurals,name='UML_MetaModel')














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
        
            if isinstance(value,StringType):
                rl=[]
                for r in map(MultiplicityRange,value.split(',')):
                    rl.append(r.__of__(self.keyToItem.im_self))
                return self.newItem(self._ElementType,ranges=rl)


    class MultiplicityRange:

        def _convert(self,value):
    
            if isinstance(value,StringType):
                l = value.split('..')
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
'''







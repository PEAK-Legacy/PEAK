"""Domain logic and convenience features for manipulating UML Models

    This module adds a couple of domain logic features to the 'UMLClass'
    class family defined by 'peak.metamodels.uml.MetaModel'.  Specifically,
    it adds some computed features, such as the notion of a "qualified name"
    of a UML model element, and the "superclasses" and "subclasses" of UML
    generalizable elements.

    It also redefines 'model' to be 'peak.metamodels.SimpleModel', which adds
    querying and XMI reading aspects to the basic in-memory structural model.
"""

from peak.util.imports import lazyModule
generated = lazyModule(__name__, '../../model/Foundation/Core')

__bases__ = generated,

from peak.api import *
from peak.model.queries import query






















class ModelElement:

    class qualifiedName(model.DerivedAssociation):

        def _getList(feature,element):

            name = element.name

            if not name:
                return []
            
            names = list(query([element])['namespace*']['name'])
            names.reverse(); names.append(name)
        
            return ['.'.join(names)]


class GeneralizableElement:

    class superclasses(model.DerivedAssociation):

        def _getList(feature,element):
            return list(query([element])['generalization']['parent'])
    

    class subclasses(model.DerivedAssociation):

        def _getList(feature,element):
            return list(query([element])['specialization']['child'])












class Namespace:

        def __getitem__(self,key):

            if '.' in key:
                ob = self
                for k in key.split('.'):
                    ob = ob[k]
                return ob

            for ob in self.ownedElements:
                if getattr(ob,'name',None)==key:
                    return ob

            raise KeyError, key


        def find(self,*criteria):
            q = query(self.ownedElements)
            for c in criteria:
                q = q[c]
            return q


config.setupModule()


"""Domain logic and convenience features for manipulating UML Models

    This module adds a couple of domain logic features to the UML structural
    model defined by 'peak.metamodels.UML13.model'.  Specifically,
    it adds some computed features, such as the notion of a "qualified name"
    of a UML model element, and the "superclasses" and "subclasses" of UML
    generalizable elements.  It also gives namespaces a '__getitem__' method
    for easy retrieval of object contents, and a 'find' operation for running
    queries over a UML model.
"""

from peak.util.imports import lazyModule
generated = lazyModule(__name__, '../../model/Foundation/Core')

__bases__ = generated,

from peak.api import *
from peak.model.queries import query























class ModelElement:

    class name:
        defaultValue = None


    class qualifiedName(model.DerivedFeature):

        def _getList(feature,element):

            name = element.name

            if not name:
                return []
            
            names = list(query([element])['namespace*']['name'])
            names.reverse(); names.append(name)
        
            return ['.'.join(names)]


class GeneralizableElement:

    class superclasses(model.DerivedFeature):

        def _getList(feature,element):
            return list(query([element])['generalization']['parent'])
    

    class subclasses(model.DerivedFeature):

        def _getList(feature,element):
            return list(query([element])['specialization']['child'])








class Namespace:

    _contentsIndex = binding.Once(
        lambda s,d,a: dict([
            (ob.name, ob) for ob in s.ownedElement
        ])
    )


    class ownedElement:

        def _onLink(feature, element, item, posn=None):                
            element._contentsIndex[item.name]=item

        def _onUnlink(feature, element, item, posn=None):
            del element._contentsIndex[item.name]


    def __getitem__(self,key):

        if '.' in key:
            ob = self
            for k in key.split('.'):
                ob = ob[k]
            return ob

        return self._contentsIndex[key]


    def find(self,*criteria):
        q = query(self.ownedElements)
        for c in criteria:
            q = q[c]
        return q


config.setupModule()


"""Extend an SEF model with the ability to read XML Metadata Interchange files

    Usage::

        import TW.XMI.Reading as SEF

        class MyMetaModel(SEF.App):

            class anElementOfMyMetaModel(SEF.Element):

                ...

    In other words, create a metamodel as you normally would with SEF classes,
    but using the TW.XMI.Reading module instead of SEF.  Of course, you can
    also create your own variant modules that combine other aspects with this
    one over the base SEF module.  Also, you may choose to define your
    metamodel in a module that does not import a specific variant of the SEF
    module, but instead uses the default unless overridden in an inheriting
    module.  (See, for example, 'TW.UML.MetaModel', which uses the default
    SEF implementation, and 'TW.UML.Model', which adds domain logic to the
    raw UML metamodel, and elects to use 'TW.StructuralModel.SimpleModel' in
    place of the default SEF module.
"""        

from TW.API import *
from TW.Utils.SOX import Node, Document, load
from kjbuckets import kjGraph

__bases__ = SEF












class XMINode(Node):

    _acquiredAttrs = 'factory','target'

    def _finish(self):
        idref=getattr(self,'xmi.idref',None)
        if idref: return self.factory.get(idref)
    

class XMIJunk(XMINode):

    def _newNode(self,name,atts):
        if name=='XMI.content':
            return XMIElement(name,atts)
        else:
            return XMIJunk(name,atts)
            
    def _finish(self):
        return self


class XMIDocument(Document):

    def _newNode(self,name,atts):
        return XMIJunk(name,atts)

    def _finish(self):
        return self._findFirst('XMI.content')[0]._subNodes













class XMIElement(XMINode):

    def _newNode(self,name,atts):

        if atts.has_key('xmi.id'):

            key = atts['xmi.id']
            element = self.factory.newItem(name,key)         # creating new Element
            
            if element is None:
                return XMINode(name,atts)    # ignore unknown types
                
            return XMIElement(name,atts,target=element)

        elif atts.has_key('xmi.idref'):
        
            key = atts['xmi.idref']
            
            if not self.factory.has_key(key):
                self.factory.addForwardReference(key,self.target)
                
            return XMINode(name,atts)


        # Otherwise, it's a feature
        
        newTarget = self.factory.getSubtarget(self.target,name)
        
        if newTarget is not None:
            return XMIElement(name,atts,target=newTarget)
        else:
            return XMINode(name,atts)    # ignore unknown features


    def _finish(self):
        return self.target._fromXMI(self)





class XMIFactory:

    def __init__(self,rootService):
        self.rootService = rootService
        self.contents = {}
        self.forwards = kjGraph()
        
    def __getitem__(self,key):      return self.contents[key]
    def get(self,key,default=None): return self.contents.get(key,default)
    def has_key(self,key):          return self.contents.has_key(key)

    def addForwardReference(self,key,target):
        self.forwards.add(key,target)


    def newItem(self,typeName,key):

        typeName = getattr(self.rootService,'_XMIMap',{}).get(typeName)
        if not typeName: return None
        
        element = self.rootService.newElement(typeName)
        self.contents[key]=element
        
        # Fix up any outstanding forward references
        forwards = self.forwards
        if forwards.has_key(key):
            for obj in forwards.neighbors(key):
                obj.addItem(element)
            del forwards[key]

        return element


    def getSubtarget(self,target,name):
        featureName = getattr(target,'_XMIMap',{}).get(name)  
        if not featureName: return None

        return getattr(target,featureName)



class XMIMapMaker(SEF.Base):

    def __class_init__(thisClass, newClass, next):

        if __proceed__ is not None:
            __proceed__(thisClass, newClass, next)
        else:
            next().__class_init__(newClass,next)

        xm = newClass._XMIMap = {}

        for attName in dir(newClass):
            for k in getattr(getattr(newClass,attName),'_XMINames',()):
                xm[k] = attName



























class StructuralFeature:

    def _fromXMI(self,node):
    
        v = getattr(node,'xmi.value',None)
        if v is not None:
            self.set(v)
        elif node._subNodes:
            self.set(node._subNodes[0])
        elif node._allNodes:
            self.set(''.join(node._allNodes))
        else:
            return node


class Classifier(XMIMapMaker):

    def _fromXMI(self,node):
        return self



class Reference:
    def _fromXMI(self,node):
        map(self.set,node._subNodes)


class Collection:
    def _fromXMI(self,node):
        add = self.addItem
        for node in node._subNodes:
            if not self.isReferenced(node): add(node)









class App(XMIMapMaker):

    def _fromXMI(self,node):
        return node


    def _XMIroot(self,*args,**kw):
        document = apply(XMIDocument,args,kw)
        document.factory = XMIFactory(self)
        document.target = self
        return document


    def importFromXMI(self,filename_or_stream):
        return load(filename_or_stream, self._XMIroot())


setupModule()

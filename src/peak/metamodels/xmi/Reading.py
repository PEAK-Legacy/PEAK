from TW import *
from TW.SOX import Node, Document, load
from kjbuckets import kjGraph


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



class XMIMapMaker(RegistryBuilder):

    def registerItem(self,reg,attName,attVal):
        for k in getattr(attVal,'_XMINames',()):
            reg[k] = attName

XMIMapMaker = XMIMapMaker()


































class XMIReading:

    _XMIMap = XMIMapMaker

    class _sefStructuralFeature:
    
        def _fromXMI(self,node):
        
            v = getattr(node,'xmi.value',None)
            if v is not None:
                self.set(v)
            elif node._subNodes:
                self.set(node._subNodes[0])
            elif node._allNodes:
                from string import join
                self.set(join(node._allNodes,''))
            else:
                return node

    class _sefClassifier:
    
        def _fromXMI(self,node):
            return self

        _XMIMap = XMIMapMaker


    class _sefReference:
        def _fromXMI(self,node):
            map(self.set,node._subNodes)
    
    class _sefSet:
        def _fromXMI(self,node):
            add = self.addItem
            for node in node._subNodes:
                if not node in self: add(node)

    def _fromXMI(self,node):
        return node


    def _XMIroot(self,*args,**kw):
        document = apply(XMIDocument,args,kw)
        document.factory = XMIFactory(self)
        document.target = self
        return document

    def importFromXMI(self,filename_or_stream):
        return load(filename_or_stream,self._XMIroot())


from TW.SOX import Node, Document, load
from TW.Aspects import Aspect

class XMINode(Node):

    def __init__(self,name,atts,factory):
        Node.__init__.im_func(self,name,atts)
        self.factory = factory
        
    def _finish(self):
        idref=getattr(self,'xmi.idref',None)
        if idref and self.factory.has_key(idref):
            return self.factory.keyToItem(idref)
    
    def _newNode(self,name,atts):
        return XMINode(name,atts,self.factory)


class XMIJunk(XMINode):

    def _newNode(self,name,atts):
        if name=='XMI.content':
            return XMIElement(name,atts,self.factory)
        else:
            return XMIJunk(name,atts,self.factory)
            
    def _finish(self):
        return self













class XMIElement(XMINode):

    def _newNode(self,name,atts):

        if 'xmi.id' in atts:
            key = atts['xmi.id']
        elif 'xmi.idref' in atts:
            key = atts['xmi.idref']
        else:
            key = None
            
        factory = self.factory
        xmap = getattr(factory,'_xmiMap',None)
        
        if xmap and xmap.has_key(name):
            element = xmap[name].__of__(factory)            
        else:
            element = self.factory.newItem(name,key)
            if element is None:
                return XMINode(name,atts,self.factory)
                
        return XMIElement(name,atts,element)
        
    def _finish(self):
        return self.factory._fromXMI(self)


class XMIDocument(Document):

    def _newNode(self,name,atts):
        return XMIJunk(name,atts,self.factory)

    def _finish(self):
        return self._findFirst('XMI.content')[0]._subNodes







class XMIReading(Aspect):

    class attribute_feature:
    
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

    
    class type_flavor:
    
        def _fromXMI(self,node):
            return self


    class ref_feature:
    
        def _fromXMI(self,node):
            self.set(node._subNodes[0])


    class list_feature:

        def _fromXMI(self,node):
            self.set(node._subNodes)


    def _fromXMI(self,node):
        return node


        
    def _XMIroot(self,*args,**kw):
        document = apply(XMIDocument,args,kw)
        document.factory = self
        return document
        
    def importFromXMI(self,filename_or_stream):
        self.roots.extend(load(filename_or_stream,self._XMIroot))


"""Extend a PEAK model with the ability to read XML Metadata Interchange files

    Usage::

        import peak.metamodels.xmi.reading as model

        class MyMetaModel(model.App):

            class anElementOfMyMetaModel(model.Element):

                ...

    In other words, create a metamodel as you normally would with 'peak.model'
    classes, but using the 'peak.metamodels.xmi.reading' module instead of
    'peak.model.api'.  Of course, you can also create your own variant
    modules that combine other aspects with this one over the base
    'peak.model.api' module.  Also, you may choose to define your metamodel
    in a module that does not import a specific variant of the 'peak.model'
    module, but instead uses the default unless overridden in an inheriting
    module.  (See, for example, 'peak.metamodels.uml.MetaModel', which uses
    the default model implementation, and 'peak.metamodels.UML.Model', which
    adds domain logic to the raw UML metamodel, and elects to use
    'peak.metamodels.SimpleModel' in place of the default 'peak.model' module.

    TODO

        XMI 1.0

        - marshal strings to values (needs support from peak.model & uml.Model)

          * ints, enums, booleans, other...?

        - handle CORBA types (YAGNI?)

        - HREF support (ugh!)  Note that cross-file HREF needs some way to cache
          the other documents and an associated DM, if it's to be dynamic.

        XMI 1.1

        - Attribute-encoded datatypes

        - XML namespaces (required by spec!)

        - metamodel lookups

        Writing

        - needs to know composition link direction (needs peak.model support)

        - Possible algorithms:

          - Direct write w/UUIDs, don't keep comments, PIs, extensions or IDs.
            This is probably fast and simple for application data, but useless
            for round-tripping metadata with modeling tools.

          - Direct write, keep extras but push to end of containing XML tag if
            object represented by tag was modified (we'll need to keep track of
            comments and processing instructions as well as ignorable
            whitespace for this to work well).  This is almost certainly the
            one we'll implement, *maybe* with XMI.diff support.
          
          - Modify pseudo-DOM in place, allowing for possible persistent DOM
            implementation.  This only seems useful if we don't use our
            existing pseudo-DOM, or rewrite it to proxy to a "real" DOM.  And
            that would only be useful if such a persistent "real" DOM existed
            that we needed to use.  YAGNI, but doc'd here for clarification.

        Other

        - cross-reference between files could be supported by having document
          objects able to supply a relative or absolute reference to another
          document.  But this requires HREF support.  :(
"""

from peak.api import *
from peak.util import SOX
from weakref import WeakValueDictionary

__bases__ = model,





class XMINode(object):

    indexAttrs = 'xmi.uuid', 'xmi.id'

    __slots__ = [
        '_name','subNodes','allNodes','attrs','index','document',
        '__weakref__','parent','isExtension',
    ]


    def __init__(self,name='',atts={}):
        self._name = name
        self.attrs = dict(atts.items())
        self.subNodes = []
        self.allNodes = []
        self.isExtension = (self._name=='XMI.extension')

    def _acquireFrom(self, parent):
        self.index = parent.index
        self.document = parent.document
        self.parent = parent
        

    def _addNode(self,name,node):
        self.allNodes.append(node)
        self.subNodes.append(node)

    def _newNode(self,name,atts):
        return self.__class__(name,atts)
        
    def _addText(self,text):
        self.allNodes.append(text)

    def _finish(self):
        atts = self.attrs
        for a in self.indexAttrs:
            if atts.has_key(a):
                self.index[(a,atts[a])] = self
        return self


    def getId(self):
        atts = self.attrs
        for a in self.indexAttrs:
            if atts.has_key(a):
                return (a,atts[a])
        Id = None,id(self)
        self.index[Id] = self
        return Id

    def getRef(self):
        atts = self.attrs
        if 'xmi.uuidref' in atts:
            return 'xmi.uuid', atts['xmi.uuidref']
        if 'xmi.idref' in atts:
            return 'xmi.id',  atts['xmi.idref']
        #XXX need to check href for XMI 1.1
        return self.getId()
    
    def getValue(self):
        atts = self.attrs
        if 'xmi.value' in atts:
            return atts['xmi.value']
        # XXX check for subnodes
        return ''.join(self.allNodes)

    def findNode(self,name):
        if self._name==name:
            return self
        for node in self.subNodes:
            f = node.findNode(name)
            if f is not None:
                return f









    def stateForClass(self, klass, dm):
    
        d = {}

        for attr,val in self.attrs.items():

            if attr.startswith('xmi.'): continue
            f = dm.getFeature(klass, attr)
            if f is None: continue

            if model.IValue.isImplementedBy(f):
                d[f.attrName] = f.fromString(val)
            else:
                d.setdefault(f.attrName,[]).extend(
                    [dm[('xmi.id',n)] for n in val.split()]
                )
            
        for node in self.subNodes:

            if node.isExtension: continue
            f = dm.getFeature(klass, node._name)
            if f is None: continue

            if model.IValue.isImplementedBy(f):
                d[f.attrName] = f.fromString(node.getValue())
            else:
                d.setdefault(f.attrName,[]).extend(
                    [dm[n.getRef()]
                        for n in node.subNodes if not n.isExtension]
                )

        coll = self.parent
        if coll is None: return d
        owner = coll.parent
        if owner is None: return d

        owner = dm[owner.getRef()]
        f = dm.getFeature(owner.__class__, coll._name)

        other = f.referencedEnd
        
        if other:
            d['__xmi_parent_attr__'] = pa = getattr(klass,other).attrName
            d.setdefault(pa,[owner])

        return d




































class XMIDocument(binding.AutoCreated, XMINode):

    index = binding.New(WeakValueDictionary)
    attrs = binding.New(dict)
    subNodes = allNodes = binding.New(list)
    _name = None
    parent = None
    
    document = binding.bindToSelf()


    def version(self,d,a):
        return self.attrs['xmi.version']

    version = binding.Once(version)


    def _newNode(self,name,atts):
        return XMINode(name,atts)


    def _finish(self):

        self.index[()] = root = self.findNode('XMI.content')

        for sub in root.subNodes:
            sub.parent = None
        return self













class XMI_DM(storage.EntityDM):

    resetStatesAfterTxn = False

    index = binding.bindTo('document/index')

    metamodel = binding.requireBinding("Metamodel with _XMIMap")

    document = binding.requireBinding("XMIDocument with data to use")


    def ghost(self, oid, state=None):
        if oid==():
            return model.PersistentQuery()
        klass = self.getClass(self.index[oid]._name)
        return klass()


    def getClass(self,name):
        return getattr(self.metamodel,self.metamodel._XMIMap[name]) # XXX
        

    def getFeature(self,klass,name):
        return getattr(klass,klass._XMIMap.get(name,''),None)  # XXX
        

    def load(self, oid, ob):
        
        target = self.index[oid]

        if oid==():
            return [
                self[n.getRef()] for n in target.subNodes if not n.isExtension
            ]
        
        return target.stateForClass(ob.__class__, self)





class XMIMapMaker_Meta(type):

    def __init__(klass, name, bases, dict):

        super(XMIMapMaker_Meta,klass).__init__(name, bases, dict)

        xm = {}
        for b in bases:
            xm.update(getattr(b,'_XMIMap',{}))

        for attName, obj in dict.items():
            for k in getattr(obj,'_XMINames',()):
                xm[k] = attName

        klass._XMIMap = xm


class XMIMapMaker:

    __metaclass__ = XMIMapMaker_Meta


class Classifier(XMIMapMaker):
    pass

















class App(XMIMapMaker):

    class __DM(XMI_DM):
        metamodel = binding.bindToParent()
        document  = XMIDocument

    def importFromXMI(self,filename_or_stream):   
        SOX.load(filename_or_stream, self.__DM.document)
        return self.__DM[()]


config.setupModule()

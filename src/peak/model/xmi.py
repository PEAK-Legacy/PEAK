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

        - XMI.field: needs model support for 'fromFields()'

        - handle CORBA types (YAGNI?)

        - HREF support (ugh!)  Note that cross-file HREF needs some way to cache
          the other documents and an associated DM, if it's to be dynamic.

        XMI 1.1

        - Attribute-encoded datatypes

        - metamodel lookups

        Writing

        - needs to know composition link direction (needs peak.model support)

        - Algorithm plan:

          - Element state will contain a reference to pseudo-DOM node, if
            available.  Elements are saved by modifying node in-place.
            Sub-elements are saved using their node, if the node's parent is
            the containing element's node.  If the sub-element has no node,
            save the sub-element (creating a node), and point its node's
            parent to the current element's node.

          - If the sub-element's node's parent is *not* the current element's
            node, create an 'xmi.idref' node linking to the sub-element node.

          - New elements, and non-persistent objects simply create a "fresh"
            node for use by the containing element.  Elements keep a reference
            to this new node, so that potential containers can tell if they've
            seen it.

          - We only care about keeping XMI.Extension tags, and then probably
            only ones contained directly in an element.  If a node is modified,
            its extension tags should all be moved to the end of the modified
            node's children, with comments to trace where they came from, and
            a warning issued if any extensions are moved from their original
            position.

          - Generate new ID's as UUIDs, and place in both UUID and ID fields;
            need to standardize on a '__uuid__' or similar field in elements
            so that elements that need/want a UUID to map over to/from another
            data system can do so.

          - Format transforms can be supported via DM.thunk(); it should be
            possible to copy an entire model from one DM to another in this
            way, and thus switch between XMI 1.0 and 1.1 (or other) storage
            formats.

          - For thunking to be effective, XMI.extensions must be sharable,
            and therefore immutable -- so XMI extension/text class is needed.

          - XMIDocument should become persistent, and use a second-order DM to
            load/save it.  Modifying XMINode instances should flag the
            XMIDocument as changed.  We can then implement a transactional
            file-based DM that can load and save the XMIDocument itself.

          - XMIDocument needs to know its version or select a strategy object
            to handle node updates for a particular XMI version.

          - Need to research 'ignorableWhitespace' et al to ensure that we can
            write cleanly indented files but with same semantics as originals.

        Other

        - cross-reference between files could be supported by having document
          objects able to supply a relative or absolute reference to another
          document.  But this requires HREF support.  :(

        - XMI.any, XMI.CorbaTypeCode, XMI.CorbaTcXXX ...?

"""

from peak.api import *
from peak.util import SOX
from weakref import WeakValueDictionary

















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
        # XXX check for non-xmi. attrs to support attr-enc datatypes
        # XXX check for subnodes
        # XXX if all subnodes are XMI.field, use fromFields()
        # XXX if other subnodes, treat as object refs/values
        # XXX also, we should probably refactor to handle multiplicity>1
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
        if ':' in name:
            return getattr(self.metamodel,name.split(':',1)[1])
        return getattr(self.metamodel,name.split('.')[-1])

    def getFeature(self,klass,name):
        return getattr(klass,klass._XMIMap.get(name,''),None)  # XXX
        

    def load(self, oid, ob):
        
        target = self.index[oid]

        if oid==():
            return [
                self[n.getRef()] for n in target.subNodes if not n.isExtension
            ]
        
        return target.stateForClass(ob.__class__, self)





class Loader(binding.Component):

    class __DM(XMI_DM):
        metamodel = binding.bindToParent()
        document  = XMIDocument

    def importFromXMI(self,filename_or_stream):   
        SOX.load(filename_or_stream, self.__DM.document)
        return self.__DM[()]




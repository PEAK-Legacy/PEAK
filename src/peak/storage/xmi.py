"""Base classes for storing/retrieving model objects via XMI format

    TODO

        Write Algorithm

          - needs to know composition link direction (needs peak.model support)

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

          - We only care about keeping XMI.Extension tags contained directly
            in an element, in the top-level object list (XMI.content), and
            in the XMI.Extensions block.  If a node is modified, its extension
            tags may be moved to the end of the modified node's children.

          - Generate new ID's as UUIDs, and place in both UUID and ID fields;
            need to standardize on a '__uuid__' or similar field in elements
            so that elements that need/want a UUID to map over to/from another
            data system can do so.

          - Format transforms can be supported via DM.thunk(); it should be
            possible to copy an entire model from one DM to another in this
            way, and thus switch between XMI 1.0 and 1.1 (or other) storage
            formats.

          - For thunking to be effective, XMI.extensions must be sharable,
            and therefore immutable -- so we need an XMI extension/text class.

          - XMIDocument should become persistent, and use a second-order DM to
            load/save it.  Modifying XMINode instances should flag the
            XMIDocument as changed.  We can then implement a transactional
            file-based DM that can load and save the XMIDocument itself.

          - XMIDocument needs to know its version or select a strategy object
            to handle node updates for a particular XMI version.

          - Need to research 'ignorableWhitespace' et al to ensure that we can
            write cleanly indented files but with same semantics as originals.

        XMI 1.2

            XMI 1.2 is mostly a simplification and clarification of XMI 1.1;
            we should consider whether the dropped features are really
            necessary even in our 1.1 support; it's highly unlikely we'll
            encounter them in actual use.  We may wish to simply implement
            XMI 1.2 and call it "backward compatible" with XMI 1.1:

            * XMI 1.2 drops support for CORBA types in favor of
              MOF 1.4 types, and using XML Schema Datatypes for the boolean,
              integer, long, float, double, and string types.

            * The list of removed types includes: XMI.struct, XMI.arrayLen,
              XMI.array, XMI.discrim, XMI.union, and XMI.any.  (Note that
              XMI.any is used by the CWM 1.0 metamodel!)

            * Datatype elements kept are: XMI.field, XMI.sequence,
              XMI.seqItem, and XMI.enum.
                        
            Clarifications added to 1.2 spec that should probably be
            interpreted as applicable in 1.1 as well:
            
                - Encoding of multi-valued attributes; note that it is not
                  permissible to have a value for a feature both in an
                  object tag's attribute and in the object's contained tags.

                - "Nested packages may result in name collision; a namespace
                  prefix is required in this case."  Need to review EBNF,
                  and "Namespace Qualified XML Element Names".  This may
                  require metadata support on the writing side.

        XMI 2.0

            * Requires full URI-based namespace handling; maybe we should
              go ahead and add this to current implementation?  Note that
              this means all the 'xmi.*' tag and attribute names are now
              'xmi:' instead.

            * Further note on namespace handling: it sounds as though
              XML attribute names for the target model are unqualified, and
              indeed that element names can be so as well.

            * Top-level element may not be the 'XMI' tag; if a document
              represents a single object and doesn't want to include the
              XMI documentation, it can simply add an 'xmi:version'
              attribute to the outermost tag representing the serialized
              object.

            * Compositions are less regular: instead of nesting object
              tags inside an attribute tag, the attribute and object tags
              can be combined.  The tag name is the attribute name, and a
              new 'xmi:type' attribute indicates the type of the object.
              If omitted, the type of the object is assumed to be the type
              specified by the composite reference.

            * XMI 2.0 allows configuration-based control over whether
              attributes are serialized, including derived attributes;
              how should we handle derived attributes in XMI 1.x?

            * Although 'xmi:id' is the normal ID attribute, it can be
              specified via a tagged value as being different.  It isn't
              clear how this would work if there were multiple ID attributes
              per XMI file.


        Other

          - XMI.any  (it's used by OMG metamodels such as CWM 1.0, mainly
            for things like strings, when the feature the value is stored in
            allows "any" value.)

          - metamodel lookups

          - cross-reference between files could be supported by having document
            objects able to supply a relative or absolute reference to another
            document.  But this requires HREF support.  :(  Note that
            cross-file HREF needs some way to cache the other documents and an
            associated DM, if it's to be dynamic.

          - XMI.CorbaTypeCode, XMI.CorbaTcXXX ...?  These are gone in XMI 1.2;
            do we have any 1.0 or 1.1 models that need them?
"""


from peak.api import *
from peak.util import SOX
from weakref import WeakValueDictionary
from Persistence import Persistent
from xml.sax import saxutils
from types import StringTypes






















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


    def findNode(self,name):
        if self._name==name:
            return self
        for node in self.subNodes:
            f = node.findNode(name)
            if f is not None:
                return f


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

        if 'href' in atts:
            raise NotImplementedError(
                "Can't handle href yet" #XXX
            )

        if 'xmi.uuidref' in atts:
            ref = 'xmi.uuid', atts['xmi.uuidref']

        elif 'xmi.idref' in atts:
            ref = 'xmi.id',  atts['xmi.idref']
        else:
            ref = self.getId()

        return self.index[ref].getId()
        
    


    def getValue(self, feature, dm):

        atts = self.attrs

        if 'xmi.value' in atts:
            return feature.fromString(atts['xmi.value'])


        if not self.subNodes:
            return feature.fromString(''.join(self.allNodes))

        sub = self.subNodes

        if len(sub)==1 and not sub[0]._name.startswith('XMI.'):
            return dm[sub[0].getRef()]

        fields = []
        for node in sub:
            if node._name <> 'XMI.field':
                raise ValueError("Don't know how to handle", node._name) #XXX
            fields.append(node.getValue(feature,dm))

        return feature.fromFields(tuple(fields))
        

















    def stateForClass(self, klass, dm):

        d = {}

        for attr,val in self.attrs.items():

            if attr.startswith('xmi.'): continue
            f = dm.getFeature(klass, attr)
            if f is None: continue

            if f.isReference:
                obs = [dm[('xmi.id',n)] for n in val.split()]
                if f.isMany:
                    d.setdefault(f.implAttr,[]).extend(obs)
                else:
                    d[f.implAttr], = obs    # XXX
            else:
                d[f.implAttr] = f.fromString(val)

        for node in self.subNodes:

            if node.isExtension: continue
            f = dm.getFeature(klass, node._name)
            if f is None: continue

            if f.isReference:
                obs = [dm[n.getRef()] for n in node.subNodes]
                if f.isMany:
                    d.setdefault(f.implAttr,[]).extend(obs)
                else:
                    d[f.implAttr], = obs    # XXX
            else:
                d[f.implAttr] = node.getValue(f, dm)


        coll = self.parent
        if coll is None: return d
        owner = coll.parent
        if owner is None: return d


        owner = dm[owner.getRef()]
        f = dm.getFeature(owner.__class__, coll._name)

        other = f.referencedEnd

        if other:

            f = getattr(klass,other)
            d['__xmi_parent_attr__'] = pa = f.implAttr

            if f.isMany:
                d.setdefault(pa,[owner])
            else:
                d.setdefault(pa,owner)

        return d

























    def writeTo(self, indStrm):

        write = indStrm.write
        indStrm.push()

        try:
            write('<%s' % self._name.encode('utf-8'))
            for k,v in self.attrs.iteritems():
                write(' %s=%s' %
                    (k.encode('utf-8'), saxutils.quoteattr(v).encode('utf-8'))
                )

            if self.allNodes:
                write('>')
                if self.subNodes==self.allNodes:
                    write('\n'); indStrm.setMargin(1)
                    for node in self.subNodes:
                        node.writeTo(indStrm); write('\n')

                elif self.subNodes:
                    indStrm.setMargin(absolute=0)    # turn off indenting
                    # piece by piece...
                    for node in self.allNodes:
                        if isinstance(node,StringTypes):
                            write(saxutils.escape(node).encode('utf-8'))
                        else:
                            node.writeTo(indStrm)
                else:
                    indStrm.setMargin(absolute=0)    # turn off indenting
                    write(
                        saxutils.escape(''.join(self.allNodes)).encode('utf-8')
                    )

                write('</%s>' % self._name.encode('utf-8'))

            else:
                write('/>')

        finally:
            indStrm.pop()

class XMIDocument(binding.Component, XMINode):

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

    def writeTo(self, indStrm):
        indStrm.write('<?xml version="1.0" encoding="utf-8">\n')
        for node in self.subNodes:
            node.writeTo(indStrm)








class XMI_DM(storage.EntityDM):

    resetStatesAfterTxn = False

    index     = binding.bindTo('document/index')
    metamodel = binding.requireBinding("Metamodel with _XMIMap")
    document  = binding.requireBinding("XMIDocument with data to use")

    def _ghost(self, oid, state=None):
        if oid==():
            return storage.PersistentQuery()
        target = self.index[oid]
        klass = self.getClass(target._name)
        if issubclass(klass,Persistent):
            return klass()
        ob = self.cache[oid] = klass()
        ob.__dict__.update(target.stateForClass(ob.__class__, self))
        return ob


    def getClass(self,name):
        if ':' in name:
            return getattr(self.metamodel,name.split(':',1)[1])
        return getattr(self.metamodel,name.split('.')[-1])


    def getFeature(self,klass,name):    # XXX

        if ':' in name:
            name = name.split(':',1)[1]

        xm = getattr(klass,'_XMIMap',())

        if name in xm:
            return getattr(klass,xm[name],None)
        else:
            name = name.split('.')[-1]
            return getattr(klass,name,None)  



    def _load(self, oid, ob):
        
        target = self.index[oid]

        if oid==():
            return [
                self[n.getRef()] for n in target.subNodes if not n.isExtension
            ]
        
        return target.stateForClass(ob.__class__, self)



class Loader(binding.Component):

    class XMI_DM_Class(XMI_DM):
        metamodel = binding.bindToParent()
        document  = binding.New(XMIDocument)

    def importFromXMI(self,filename_or_stream):
        DM = self.XMI_DM_Class(self)
        SOX.load(filename_or_stream, DM.document)
        return DM[()]




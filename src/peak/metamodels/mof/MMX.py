from kjbuckets import *
import TW.SOX

from TW import Template, SimplePostProcessor
from TW.Utilities import Pluralizer, upToDate, toString




































class MetaModelNode(TW.SOX.Node):

    contentMap = kjGraph([
        ('', 'metamodel'), ('metamodel','package'),
        ('package','package'),
        ('package','association'), ('association','role'),
        ('package','primitive'),
        ('package','enumeration'), ('enumeration','literal'),
        ('package','datatype'),
            ('datatype','attribute'),('datatype','superclass'),
        ('package','element'),
            ('element','attribute'),('element','superclass'),
    ])

    requiredAttribs = kjGraph([
        ('package','name'), ('primitive','name'), ('enumeration','name'),
        ('literal','name'), ('datatype','name'), ('element','name'),
        ('attribute','name'), ('attribute','type'), ('element','abstract'),
        ('role','name'), ('role','type'), ('role','composite'), ('role','kind'),
        ('role','navigable'), ('superclass','type'),
    ])

    allowedAttribs = kjGraph(requiredAttribs.items()+[
        ('role','xmi.name'),('attribute','kind'),('attribute','required'),
        ('role','required')
    ])

    name = ''
    path = None

    _acquiredAttrs = ('factory','path','pluralize')
    
    featureTypeMap = {
        'ref': '_sefReference', 'bag': '_sefSet', 'list': '_sefSequence',
        'value': '_sefValue',
    }





    def __init__(self,name='',atts={},**kw):
    
        anames     = kjSet(atts.keys())
        disallowed = anames - self.allowedAttribs.reachable(name)
        missing    = self.requiredAttribs.reachable(name) - anames
        
        if missing:
            raise SyntaxError,"Missing attributes %s in element %s" % (missing.items(),name)
            
        if disallowed:
            raise SyntaxError,"Invalid attributes %s in element %s" % (disallowed.items(),name)
            
        apply(TW.SOX.Node.__init__.im_func,(self,name,atts or {}),kw)

        for a in atts.keys():
            setattr(self,a,toString(atts[a]))   # Un-unicode-ify all attributes!


    def _newNode(self,name,atts):
    
        if not self.contentMap.member(self._name,name):
            reachable = self.contentMap.reachable(self._name).items()
            raise SyntaxError,"Found %s where %s expected" % (name, `reachable`)
            
        path = self.path
        
        if self._name not in ('','metamodel'):
            if path is None:
                path=''
            else:
                path='%s%s.' % (path,self.name)
                
        return MetaModelNode(name,atts,path=path)


    def _finish(self):
        return getattr(self,'_finish_'+self._name)()

    def _finish_(self):
        return None

    def _finish_package(self):
    
        # Package reduces to sum of its associations and those of child packages
        
        a = self._get('association')
        for p in self._get('package'):
            a.extend(p)
        return a
       

    def _makeClass(self,flavor,bases=(),features=(),add=1,name=None,setXMI=1):
        d = {}
        for k,v in features:
            d[k] = v
        t = Template(name or self.name, bases or (flavor,), d)
        if setXMI:
            t['_XMINames'] = ((self.path+self.name),)
        if add:
            self.factory[self.name] = t
        return t


    def _finish_primitive(self):
        self._makeClass('_sefPrimitiveType')
        
    def _finish_enumeration(self):
        self._makeClass('_sefEnumeration', features = self._get('literal'))

    def _finish_literal(self):
        return self.name, self.name

    def _finish_attribute(self):
        isRequired=getattr(self,'required','true')=='true'
        kind = self.featureTypeMap[getattr(self,'kind','value')]

        return self.name, self._makeClass(kind, (), [
            ('name',self.name), ('referencedType',self.type), ('qualifiedName', self.path+self.name),
            ('isRequired',isRequired),
            ], add = 0
        )

    def _finish_datatype(self):
        self._makeClass('_sefDataType', self._get('superclass'), self._get('attribute'))


    def _finish_element(self):
        t = self._makeClass('_sefElement', self._get('superclass'), self._get('attribute'))
        t['isAbstract'] = (self.abstract=='true')


    def _finish_superclass(self):
        return self.type


    def _finish_role(self):
        self.isParent=(self.composite=='true')
        self.isRequired=getattr(self,'required','true')=='true'
        self.navigable=(self.navigable=='true')
        self.xmi_name=getattr(self,'xmi.name',self.name)
        self.proper_name=(self.kind=='ref') and self.xmi_name or self.pluralize(self.xmi_name)
        self.kind = self.featureTypeMap[self.kind]
        return self


    def _finish_association(self):

        roles = tuple(self._get('role'))
        if len(roles)<>2: raise SyntaxError,"Expected 2 roles, found %d" % len(roles)
        
        r0, r1 = roles; r0.home = r1.type; r1.home = r0.type
        r0.isChild=r1.isParent; r0.other_name=r1.proper_name; r0.other_key=r1.name; r0.reversible=r1.navigable
        r1.isChild=r0.isParent; r1.other_name=r0.proper_name; r1.other_key=r0.name; r1.reversible=r0.navigable

        return roles








    def _finish_metamodel(self):
    
        factory = self.factory
        
        for alist in self._get('package'):
        
            for a in alist:
            
                for r in a:
                
                    #if r.isParent:  r.kind='parent_'+r.kind
                    #elif r.isChild: r.kind='child_' +r.kind
                    
                    r.fullPath = '%s.%s' % (factory[r.home]['_XMINames'][0], r.name) # XXX

                    xnames = []
                    for x in factory[r.home]['_XMINames']: xnames.append(x+'.'+r.xmi_name)

                    assn = self._makeClass(r.kind, (), [
                            ('name',r.proper_name), ('referencedType',r.type),
                            ('refTypeQN', r.fullPath), ('referencedEnd', r.other_name),
                            ('isNavigable',r.navigable), ('_XMINames',tuple(xnames)),
                            ('isRequired',r.isRequired),
                        ], add = 0, name = r.proper_name, setXMI=0
                    )

                    factory[r.home][r.proper_name] = assn














class _Loader:

    def __call__(self, modelFile, cacheFile=None, pluralize=Pluralizer(), makerType=Template, nodeClass=MetaModelNode, 
                 *args, **kw):

        if upToDate(modelFile,cacheFile) and upToDate(__file__,cacheFile):
            return self._loadFromCache(cacheFile)

        template = apply(makerType,args,kw)

        TW.SOX.load(modelFile, nodeClass(factory=template, pluralize=pluralize))

        if cacheFile is not None:
            self._saveToCache(cacheFile,template)

        return template
        
    def _loadFromCache(self,cacheFile):
        from cPickle import load
        return load(open(cacheFile,'rb'))

    def _saveToCache(self, cacheFile, aspect):
        try:
            f = open(cacheFile,'wb')
            try:
                from cPickle import dump; dump(aspect,f,1)
            finally:
                f.close()
        except:
            try:
                from os import unlink; unlink(cacheFile)
            except:
                pass
            raise
                
load = _Loader()




















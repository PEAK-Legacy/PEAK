"""Python code generation from MOF model

    This is just a rough draft that's still missing a few important things:

    * Full type support: we need 'peak.model.datatypes' to offer reusable
      base types for CORBA primitive types, otherwise we can't generate
      types like 'Boolean', 'String', and so on.

    * A suitable mechanism for indexing the created model, such that it can
      be used as a metamodel for 'peak.storage.xmi'.

    Other issues:

    - Name conflicts w/Python built-ins?

    Cosmetics

    - Docstring formatting is a bit "off"; notably, we're not wrapping
      paragraphs, and something seems wrong with linespacing, at least
      in my tests with the CWM metamodel.
"""

from __future__ import generators

from peak.api import *
from peak.model.datatypes import TCKind, UNBOUNDED
from peak.util.IndentedStream import IndentedStream
from cStringIO import StringIO
from peak.util.advice import advice

from os.path import dirname,exists
from os import makedirs









class oncePerObject(advice):

    def __call__(self,*__args,**__kw):

        if __args[1] in __args[0].objectsWritten:
            return

        __args[0].objectsWritten[__args[1]]=True

        return self._func(*__args,**__kw)































class MOFGenerator(binding.Component):

    MOFModel  = binding.bindTo("import:peak.metamodels.MOF131:MOFModel")
    Package   = binding.bindTo("MOFModel/Package")
    Import    = binding.bindTo("MOFModel/Import")
    Class     = binding.bindTo("MOFModel/Class")
    DataType  = binding.bindTo("MOFModel/DataType")
    Attribute = binding.bindTo("MOFModel/Attribute")
    Reference = binding.bindTo("MOFModel/Reference")
    Namespace = binding.bindTo("MOFModel/Namespace")

    NameNotFound = binding.bindTo("MOFModel/NameNotFound")
    NameNotResolved = binding.bindTo("MOFModel/NameNotResolved")
    StructuralFeature = binding.bindTo("MOFModel/StructuralFeature")

    fileObject = binding.New(StringIO)

    stream = binding.Once(lambda self,d,a: IndentedStream(self.fileObject))
    write  = binding.bindTo('stream/write')
    push   = binding.bindTo('stream/push')
    pop    = binding.bindTo('stream/pop')

    objectsWritten = binding.New(dict)

    pkgPrefix  = ''
    srcDir     = ''
    writeFiles = False

    sepLine = '# ' + '-'*78 + '\n'












    def writeDocString(self, doc):

        doc = doc.replace('\\','\\\\')          # \   -> \\

        tq = 0
        while doc.endswith('"'):
            tq += 1
            doc=doc[:-1]
            
        if tq:
            # Replace trailing quotes with escaped quotes
            doc += '\\"' * tq
        
        doc = doc.replace('"""','\\"\"\\"')     # """ -> \"\"\"

        self.write('"""%s"""\n\n' % doc)


    def writeClassHeader(self, element, baseNames=[]):

        if baseNames:
            bases = '(%s)' % (','.join(baseNames))
        else:
            bases = ''
            
        self.write('class %s%s:\n\n' % (element.name,bases))
        self.push(1)

        if element.annotation:
            self.writeDocString(element.annotation)











    def beginObject(self, element, metatype='__model.Element'):

        ns = element.container
        relName = self.getRelativeName

        if hasattr(element,'supertypes'):

            baseNames = [relName(m,ns) for m in element.supertypes]    # XXX

            if not baseNames:
                baseNames.append(metatype)

        else:
            baseNames = [metatype]

        self.writeClassHeader(element, baseNames)


    def getImportName(self, element):
        return self.pkgPrefix + str('.'.join(element.qualifiedName))


    def acquire(self, element, name):

        for p in self.iterParents(element):
            if not isinstance(p,self.Namespace): continue
            try:
                return p.lookupElement(name)
            except self.NameNotFound:
                pass



    def iterParents(self, element):

        while element is not None:
            yield element
            element = element.container



    def comparePaths(self, e1, e2):

        p1 = list(self.iterParents(e1)); p1.reverse()
        p2 = list(self.iterParents(e2)); p2.reverse()

        common = [i1 for (i1,i2) in zip(p1,p2) if i1 is i2]

        cc = len(common)       
        p1 = p1[cc:]
        p2 = p2[cc:]
        
        return common, p1, p2





























    def getRelativePath(self, e1, e2):

        c,p1,p2 = self.comparePaths(e1,e2)

        if c:
            if not p2:
                p1.insert(0,c[-1])
                p2.insert(0,c[-1])
                c.pop()

            ob = self.acquire(e1,p2[0].name)

            if ob is p2[0]:
                p1=[]   # just acquire it

            return ['..']*len(p1)+[e.name for e in p2]

        p1.reverse()    # Search all parents of the source
        
        for parent in p1:

            if not isinstance(parent,self.Package):
                continue

            for imp in parent.findElementsByType(self.Import):
                c,sp1,sp2 = self.comparePaths(imp.importedNamespace, e2)
                if c:
                    # sp2 is path from imp -> e2
                    return self.getRelativePath(e1,imp)+[e.name for e in sp2]

        raise self.NameNotResolved(
            "No path between objects", e1.qualifiedName, e2.qualifiedName
        )








    pkgImportMap = binding.New(dict)
    
    def nameInPackage(self, element, package):

        pim = self.pkgImportMap
        
        try:
            return pim[package, element]
        except KeyError:
            pass

        name = element.name
        c = element.container

        while c is not None and c is not package:
            try:
                ob = package.lookupElementExtended(name)
            except self.NameNotFound:
                break
            else:
                if ob is element:
                    break
                else:
                    name = '%s__%s' % (c.name, name)
                    c = c.container

        if element.container is not package:
            self.write(
                '%-20s = __lazy(%r)\n' % (
                    str(element.name),
                    self.getImportName(element)
                )
            )

        pim[package,element] = name
        return name





    def writeFileHeader(self, package):
        self.write(self.sepLine)
        self.write('# Package: %s\n' % self.getImportName(package))
        self.write('# File:    %s\n' % self.pkgFileName(package))
        if package.supertypes:
            self.write('# Bases:   %s\n'
                % ', '.join(
                    [str('.'.join(p.qualifiedName))
                        for p in package.supertypes]
                )
            )
        self.write(self.sepLine)
        self.write("""
from peak.api          import model as __model
from peak.api          import config as __config
from peak.util.imports import lazyModule as __lazy

""")


    def writeFileFooter(self, package):
        self.write('\n\n__config.setupModule()\n\n')
        self.write(self.sepLine)
        self.write('\n\n\n')


    def exposeImportDeps(self, package, target=None):

        if target is None: target = package
        nip = self.nameInPackage
        eid = self.exposeImportDeps
        
        for klass in target.findElementsByType(self.Class):
            for k in klass.supertypes:
                if k.container is not package:
                    nip(k.container, package)
            eid(klass)




    def writePackage(self, package):

        for subPkg in package.findElementsByType(self.Package):
            self.objectsWritten[subPkg] = True

        self.writeFileHeader(package)

        self.write(self.sepLine+'\n')
        for imp in package.findElementsByType(self.Import):
            self.writeImport(imp)

        self.exposeImportDeps(package)
        self.write('\n%s\n' % self.sepLine)

        self.writeNSContents(package,{})

        for subPkg in package.findElementsByType(self.Package):
            self.write('%-20s = __lazy(__name__ + %r)\n'
                % (subPkg.name, '.'+str(subPkg.name))
            )
            
        self.writeFileFooter(package)


    writePackage = oncePerObject(writePackage)


    def pkgFileName(self,package):

        from os.path import join
        path = self.srcDir

        for p in self.getImportName(package).split('.'):
            path = join(path,p)
        
        for ob in package.findElementsByType(self.Package):
            return join(path,'__init__.py')
        else:
            return '%s.py' % path


    def writeNSContents(self, ns, contentMap):
    
        for imp in self.findAndUpdate(ns, self.Import, contentMap):
            self.writeImport(imp)

        for pkg in self.findAndUpdate(ns, self.Package, contentMap):
            self.writePackage(pkg)

        for klass in self.findAndUpdate(ns, self.Class, contentMap):
            self.writeClass(klass)

        for dtype in self.findAndUpdate(ns, self.DataType, contentMap):
            self.writeDataType(dtype)

        posn = 0
        for feature in self.findAndUpdate(
                ns, self.StructuralFeature, contentMap
            ): 
            self.writeFeature(feature,posn)
            posn += 1

        # XXX constant, type alias, ...?


    def findAndUpdate(self, ns, findType, contentMap):

        for ob in ns.findElementsByType(findType):
            if ob.name in contentMap: continue
            contentMap[ob.name] = ob
            yield ob


    def writeImport(self, imp):

        pkgName = self.getImportName(imp.importedNamespace)
        self.write('%-20s = __lazy(%r)\n' % (imp.name, pkgName))

    writeImport = oncePerObject(writeImport)



    def writeClass(self, klass):

        myPkg = klass.container

        for c in klass.supertypes:
            if c.container is myPkg:
                self.writeClass(c)

        self.beginObject(klass, '__model.Element')

        if klass.isAbstract:
            self.write('mdl_isAbstract = True\n\n')
            
        contentMap = {}
        self.writeNSContents(klass, contentMap)

        if not contentMap and not klass.isAbstract:
            self.write('pass\n\n\n')

        self.pop()

    writeClass = oncePerObject(writeClass)



















    def writeDataType(self,dtype):

        tc = dtype.typeCode

        if tc.kind == TCKind.tk_enum:
            self.writeEnum(dtype, tc.member_names)

        elif tc.kind == TCKind.tk_struct:
            self.writeStruct(dtype, zip(tc.member_names,tc.member_types))
            
        else:
            self.beginObject(dtype,'__model.PrimitiveType')
            self.write("pass   # XXX Don't know how to handle %s!!!\n\n"
                % tc.kind
            )
            self.pop()


    writeDataType = oncePerObject(writeDataType)


    def writeStruct(self,dtype,memberInfo):

        self.beginObject(dtype,'__model.DataType')

        posn = 0
        for mname, mtype in memberInfo:
            self.writeStructMember(mname, mtype, posn)
            posn += 1
            
        self.push(1)
        self.pop()









    def writeStructMember(self,mname,mtype,posn):

        self.write('class %s(__model.structField):\n\n' % mname)
        self.push(1)

        self.write('referencedType = %r # XXX \n' % repr(mtype))
        self.write('sortPosn = %r\n\n' % posn)

        self.pop()


    def writeEnum(self,dtype,members):
    
        self.beginObject(dtype,'__model.Enumeration')

        for m in members:
            self.write('%s = __model.enum()\n' % m)

        if members:
            self.write('\n')

        self.pop()


    def getRelativeName(self, element, package):

        if element.container is package:
            return element.name

        return '%s.%s' % (
            self.nameInPackage(element.container,package),
            element.name
        )








    def writeFeature(self,feature,posn):

        self.beginObject(feature,'__model.StructuralFeature')

        if not feature.isChangeable:
            self.write('isChangeable = False\n')

        self.write('referencedType = %r\n'
            % str('/'.join(self.getRelativePath(feature,feature.type)))
        )

        if isinstance(feature,self.Reference):

            inverseRef = self.findInverse(feature)

            if inverseRef is not None:
                self.write('referencedEnd = %r\n' % str(inverseRef.name))
                
            self.write('isReference = True\n')

        elif feature.isDerived:
            self.write('isDerived = True\n')


        m = feature.multiplicity 

        if m.upper<>UNBOUNDED:
            self.write('upperBound = %r\n' % m.upper)

        if m.lower<>0:
            self.write('lowerBound = %r\n' % m.lower)

        self.write('sortPosn = %r\n\n' % posn)
        self.pop()







    def findInverse(self, feature):

        ae = feature.referencedEnd.otherEnd()

        for ref in feature.type.findElementsByTypeExtended(self.Reference):
            if ref.referencedEnd is ae:
                return ref



    def externalize(klass, metamodel, package, format, **options):

        s = StringIO()

        klass(
            package,
            MOFModel=metamodel,
            stream=IndentedStream(s),
            **options
        ).writePackage(package)

        return s.getvalue()


    externalize = classmethod(externalize)
















class MOFFileSet(MOFGenerator):

    def externalize(klass, metamodel, package, format, **options):

        def doExt(package, parent):
        
            g = klass(
                package, MOFModel=metamodel, **options
            )
            
            filename = g.pkgFileName(package)

            if g.writeFiles:

                d = dirname(filename)
                if not exists(d):
                    makedirs(d)

                g.fileObject = open(filename,'w')               
                g.writePackage(package)
                contents = None

            else:
                g.writePackage(package)
                contents = g.fileObject.getvalue()
                
            outfiles = [ (filename, contents) ]

            for pkg in package.findElementsByType(metamodel.Package):
                outfiles.extend(doExt(pkg, g))
            

            return outfiles

        return doExt(package,package)


    externalize = classmethod(externalize)



class MOFOutline(MOFGenerator):

    def writePackage(self, package):

        self.write('package %s:\n' % package.name)
        self.push(1)
        self.write('# %s\n' % self.pkgFileName(package))
        self.writeNSContents(package, {})
        self.pop()


    def writeImport(self, imp):
        self.write(
            'import %s'
                % self.getImportName(imp.importedNamespace)
        )
        if imp.name!=imp.importedNamespace.name:
            self.write(' as %s' % imp.name)

        self.write('\n')


    def writeClass(self, klass):
        baseNames = [
            self.getRelativeName(c,klass.container) for c in klass.supertypes
        ]
        self.write(
            'class %s(%s):\n'
                % (klass.name, ','.join(baseNames))
        )
        self.push(1)
        self.writeNSContents(klass, {})
        self.pop()

    def writeDataType(self,dtype):
        pass

    def writeFeature(self,feature,posn):
        pass







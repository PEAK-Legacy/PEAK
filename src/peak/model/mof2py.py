"""Python code generation from MOF model

    This is just a rough draft that's still missing a few important things:

    * Relative names for 'referencedType' links: we only generate a simple
      name reference right now, but we really need to import the package where
      the type comes from, or at least use '"import:"' links to reference the
      right module location.

    * Full type support: we need 'peak.model.datatypes' to offer reusable
      base types for CORBA primitive types, otherwise we can't generate
      types like 'Boolean', 'String', and so on.

    * A suitable mechanism for indexing the created model, such that it can
      be used as a metamodel for 'peak.storage.xmi'.

    Other issues:

    - Python built-ins and 'peak.*' object names

    - package prefixes

    - Need to import 'peak.model' and include 'config.setupModule()' epilogue

    Cosmetics

    - Should generate all imports at top

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

    NameNotFound = binding.bindTo("MOFModel/NameNotFound")

    StructuralFeature = binding.bindTo("MOFModel/StructuralFeature")

    def stream(self,d,a):
        return IndentedStream(StringIO())

    stream = binding.Once(stream)
    write  = binding.bindTo('stream/write')
    push   = binding.bindTo('stream/push')
    pop    = binding.bindTo('stream/pop')

    objectsWritten = binding.New(dict)

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


    def beginObject(self, element, metatype='model.Element'):

        ns = element.container
        relName = self.getRelativeName

        if hasattr(element,'supertypes'):

            baseNames = [relName(m,ns) for m in element.supertypes]    # XXX

            if not baseNames:
                baseNames.append(metatype)

        else:
            baseNames = [metatype]

        self.writeClassHeader(element, baseNames)











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
                'from %s import %s' % (
                    str('.'.join(element.container.qualifiedName)),
                    str(element.name)
                )
            )
            if element.name <> name:
                self.write('as '+name)
            self.write('\n')

        pim[package,element] = name
        return name

                
    def writeFileHeader(self, package):
        self.write('# --------------------------------------------------\n')
        self.write('# Package: %s\n' % str('.'.join(package.qualifiedName)))
        self.write('# File:    %s\n' % self.pkgFileName(package))
        if package.supertypes:
            self.write('# Bases:   %s\n'
                % ', '.join(
                    [str('.'.join(p.qualifiedName))
                        for p in package.supertypes]
                )
            )
        self.write('# --------------------------------------------------\n\n')


    def writeFileFooter(self, package):
        self.write('\n# --------------------------------------------------\n')
        self.write('\n\n\n')
























    def writePackage(self, package):

        for subPkg in package.findElementsByType(self.Package):
            self.objectsWritten[subPkg] = True

        self.writeFileHeader(package)

        for imp in package.findElementsByType(self.Import):
            self.writeImport(imp)

        self.writeNSContents(package,{})

        for subPkg in package.findElementsByType(self.Package):
            self.write('import %s\n' % subPkg.name)
            
        self.writeFileFooter(package)


    writePackage = oncePerObject(writePackage)






















    def pkgFileName(self,package):

        name = str('/'.join(package.qualifiedName))
        
        for ob in package.findElementsByType(self.Package):
            return '%s/__init__.py' % name
        else:
            return '%s.py' % name
       
            
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

        pkgName = '.'.join(imp.importedNamespace.qualifiedName)
        self.write('# import %s as %s\n\n' % (pkgName, imp.name) )

    writeImport = oncePerObject(writeImport)


    def writeClass(self, klass):

        myPkg = klass.container

        for c in klass.supertypes:
            if c.container is myPkg:
                self.writeClass(c)

        self.beginObject(klass, 'model.Element')

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
            self.beginObject(dtype,'model.PrimitiveType')
            self.write("pass   # XXX Don't know how to handle %s!!!\n\n"
                % tc.kind
            )
            self.pop()


    writeDataType = oncePerObject(writeDataType)


    def writeStruct(self,dtype,memberInfo):

        self.beginObject(dtype,'model.DataType')

        posn = 0
        for mname, mtype in memberInfo:
            self.writeStructMember(mname, mtype, posn)
            posn += 1
            
        self.push(1)
        self.pop()









    def writeStructMember(self,mname,mtype,posn):

        self.write('class %s(model.structField):\n\n' % mname)
        self.push(1)

        self.write('referencedType = %r # XXX \n' % repr(mtype))
        self.write('sortPosn = %r\n\n' % posn)

        self.pop()


    def writeEnum(self,dtype,members):
    
        self.beginObject(dtype,'model.Enumeration')

        for m in members:
            self.write('%s = model.enum()\n' % m)

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

        self.beginObject(feature,'model.StructuralFeature')

        if not feature.isChangeable:
            self.write('isChangeable = False\n')

        self.write('referencedType = %r\n' % str(feature.type.name))

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



    def externalize(klass, metamodel, package, format):

        s = StringIO()

        klass(
            package,
            MOFModel=metamodel,
            stream=IndentedStream(s)
        ).writePackage(package)

        return s.getvalue()


    externalize = classmethod(externalize)

















class MOFFileSet(MOFGenerator):

    def externalize(klass, metamodel, package, format):

        outfiles = []
        
        for pkg in package.findElementsByType(metamodel.Package):
            outfiles.extend(klass.externalize(metamodel, pkg, format))
            
        s = StringIO()
        g = klass(package, MOFModel=metamodel, stream=IndentedStream(s))
        g.writePackage(package)

        outfiles.append(
            (g.pkgFileName(package), s.getvalue())
        )

        return outfiles


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
                % str('.'.join(imp.importedNamespace.qualifiedName))
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







"""Python code generation from MOF model

    This is just a first draft that's missing a few important things:

    * Relative name handling: superclass references in class definitions
      may refer to names that Python won't be able to find because of
      the "only two namespaces" constraint.  So code generated for a
      multi-package model might compile, but not run.

    * Interpackage dependencies: this tries to make sure that superclasses
      are written before their subclasses, but it doesn't check to ensure
      that they're actually in the same package, so it might not be
      generating the class in the right package!

    * Full type support: we need 'peak.model.datatypes' to offer reusable
      base types for CORBA primitive types, otherwise we can't generate
      types like 'Boolean', 'String', and so on.

    * Docstring formatting is a bit "off"; notably, we're not wrapping
      paragraphs, and something seems wrong with linespacing, at least
      in my tests with the CWM metamodel.
"""

from __future__ import generators

from peak.api import *
from MOF131 import MOFModel
from peak.model.datatypes import TCKind, UNBOUNDED













class MOFGenerator(binding.Component):

    MOFModel  = binding.bindTo("import:peak.metamodels.MOF131:MOFModel")
    Package   = binding.bindTo("MOFModel/Package")
    Import    = binding.bindTo("MOFModel/Import")
    Class     = binding.bindTo("MOFModel/Class")
    DataType  = binding.bindTo("MOFModel/DataType")
    Attribute = binding.bindTo("MOFModel/Attribute")
    Reference = binding.bindTo("MOFModel/Reference")

    StructuralFeature = binding.bindTo("MOFModel/StructuralFeature")

    def stream(self,d,a):
        from peak.util.IndentedStream import IndentedStream
        from cStringIO import StringIO
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

        self.objectsWritten[element] = True

        if hasattr(element,'supertypes'):

            baseNames = [m.name for m in element.supertypes]    # XXX

            if not baseNames:
                baseNames.append(metatype)

        else:
            baseNames = [metatype]

        self.writeClassHeader(element, baseNames)












    def writePackage(self, package):

        if package in self.objectsWritten:
            return

        for pkg in package.supertypes:
            self.writePackage(pkg)

        self.beginObject(package, 'model.Package')
        
        pkgtype = self.Import

        containers = [
            imp.importedNamespace
            for imp in package.contents if isinstance(imp,pkgtype)
        ]
        containers.insert(0,package)

        contentMap = {}
        for ns in containers:
            self.writeNSContents(ns, contentMap)

        self.pop()


















    def writeNSContents(self, ns, contentMap):
    
        for subPkg in self.findAndUpdate(ns, self.Package, contentMap):
            self.writePackage(subPkg)

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














    def writeClass(self, klass):

        if klass in self.objectsWritten:
            return

        for c in klass.supertypes:
            self.writeClass(c)

        self.beginObject(klass, 'model.Element')

        if klass.isAbstract:
            self.write('mdl_isAbstract = True\n\n')
            
        contentMap = {}
        self.writeNSContents(klass, contentMap)

        if not contentMap and not klass.isAbstract:
            self.write('pass\n\n\n')

        self.pop()


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






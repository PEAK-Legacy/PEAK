from peak.api import *
from shlex import shlex
from cStringIO import StringIO
from peak.storage.files import EditableFile
from peak.util.FileParsing import AbstractConfigParser
from peak.running.commands import AbstractCommand
import os.path
safe_globals = {'__builtins__':{}}

# TODO: partdefs, formats, EditableFile constructor, app, txns

class IPartDef(protocols.Interface):

    name = protocols.Attribute(
        """Name of the part"""
    )

    independent = protocols.Attribute(
        """If true, part should not be reset when a parent is incremented"""
    )

    def incr(value):
        """Return the successor of value"""

    def reset(value):
        """Return the reset of value"""

    def validate(value):
        """Return the internal form of the string 'value', or raise error"""

class IFormat(protocols.Interface):

    def compute(version):
        """Return the formatted value of 'version' for this format"""







def tokenize(s):
    return list(iter(shlex(StringIO(s)).get_token,''))

def unquote(s):
    if s.startswith('"') or s.startswith("'"):
        s = s[1:-1]
    return s


































class VersionStore(EditableFile, AbstractConfigParser):
    """Simple writable config file for version data"""

    txnAttrs = EditableFile.txnAttrs + ('parsedData',)

    def add_setting(self, section, name, value, lineInfo):
        self.data.setdefault(section,{})[name] = eval(
            value,safe_globals,{}
        )

    def parsedData(self,d,a):
        self.data = {}
        if self.text:
            self.readString(self.text, self.filename)
        return self.data

    parsedData = binding.Once(parsedData)

    def getVersion(self,name):
        try:
            return self.parsedData[name]
        except KeyError:
            raise ValueError(
                "Missing version info for %r in %s" % (name,self.filename)
            )

    def setVersion(self,name,data):
        self.parsedData[name] = data
        self.text = ''.join(
            [
                ("[%s]\n%s\n" %
                    (k,
                    ''.join(
                            [("%s = %r\n" % (kk,vv)) for kk,vv in v.items()]
                        )
                    )
                )
                for k,v in self.parsedData.items()
            ]
        )

class Scheme(binding.Component):

    parts = binding.requireBinding("IPartDefs of the versioning scheme")
    formats = binding.requireBinding("dictionary of formats")
    defaultFormat = None

    partMap = binding.Once(
        lambda s,d,a: dict([(part.name,part) for part in self.parts])
    )

    def __getitem__(self,key):
        try:
            return self.partMap[key]
        except KeyError:
            return self.formats[key]

    def incr(self,data,part):

        d = data.copy()
        partsIter = iter(self.parts)
        for p in partsIter:
            if p.name == part:
                d[part] = p.incr(d[part])
                break
        else:
            return d

        # Reset digits to the right of the incremented digit

        for p in partsIter:
            if not p.independent:
                d[p.name] = p.reset(d[p.name])

        return d







class Version(binding.Component):

    data = _cache = binding.New(dict)
    scheme = binding.requireBinding("Versioning scheme")

    def __getitem__(self, key):
        cache = self._cache
        if key in cache:
            value = cache[key]
            if value is NOT_FOUND:
                raise ValueError("Recursive attempt to compute %r" % key)
            return cache[key]

        data = self.data
        if key in data:
            value = cache[key] = data[key]
            return value

        cache[key] = NOT_FOUND
        try:
            scheme = self.scheme
            if key in scheme:
                value = cache[key] = scheme[key].compute(self)
            return value
        except:
            del cache[key]
            raise

        raise KeyError, key


    def withIncr(self, part):
        return self.__class__(
            self.getParentComponent(), self.getComponentName(),
            data   = self.scheme.incr(self.data, part),
            scheme = self.scheme
        )




    def withParts(self, partItems):

        scheme = self.scheme
        data = self.data.copy()

        for k,v in partItems:
            if k in scheme:
                data[k] = scheme[k].validate(v)
            else:
                raise KeyError("Version has no part %r" % k)

        return self.__class__(
            self.getParentComponent(), self.getComponentName(),
            data = data, scheme = scheme
        )


    def __cmp__(self, other):
        return cmp(self.data, other)

    def __str__(self):
        fmt = self.scheme.defaultFormat
        if fmt:
            return self[fmt]
        return '[%s]' % ', '.join(
            [('%s=%r' % (p.name, self[p.name])) for p in self.scheme.parts]
        )














class VersionConfig(AbstractCommand):

    """A version configuration, comprising version schemes and modules"""

    modules = binding.requireBinding('modules for versioning')
    schemes = binding.requireBinding('list of version schemes used by modules')

    schemeMap = binding.Once(
        lambda s,d,a: dict(
            [(scheme.name.lower(), scheme) for scheme in s.schemes]
        )
    )

    datafile = binding.Once(
        lambda s,d,a: os.path.join(os.path.dirname(s.argv[0]),'version.dat')
    )

    versionStore = binding.Once(
        lambda self,d,a: VersionStore(self, filename = self.datafile)
    )





















class Module(binding.Component):

    """A versionable entity, comprising files that need version strings"""

    name = binding.requireBinding('name of this module')
    editors = binding.requireBinding('list of Editors to use')

    schemeName = 'default'
    schemeMap = binding.bindTo('../schemeMap')
    versionStore = binding.bindTo('../versionStore')

    def versionScheme(self,d,a):
        try:
            return s.schemeMap[self.schemeName.lower()]
        except KeyError:
            raise ValueError(
                "Unrecognized version scheme '%r'" % self.schemeName
            )
    versionScheme = binding.Once(versionScheme)

    currentVersion = binding.Once(
        lambda self,d,a:
            Version(
                scheme = self.versionScheme,
                data =   self.versionStore.getVersion(self.name)
            )
    )

    def setVersion(self, partItems):
        old = self.currentVersion
        new = old.withParts(partItems)
        self._editVersion(old,new)

    def incrVersion(self, part):
        old = self.currentVersion
        new = old.withIncr(part)
        self._editVersion(old,new)

    def checkFiles(self):
        self._editVersion(self.currentVersion, self.currentVersion)

    def _editVersion(self, old, new):
        for editor in self.editors:
            editor.editVersion(old,new)
        if old<>new:
            self.currentVersion = new
            self.versionStore.setVersion(self.name, new.data)




class Editor(binding.Component):

    """Thing that applies a set of edits to a set of files"""

    files = binding.requireBinding('list of EditableFile instances to edit')
    edits = binding.requireBinding('list of IEdit instances to apply')

    def editVersion(self, old, new):
        for file in self.files:
            text = file.text
            if text is None:
                raise ValueError("File %s does not exist" % file.filename)

            posn = 0
            buffer = []
            for edit in self.edits:
                posn = edit.editVersion(
                    text, posn, old, new, buffer.append, file.filename
                )

            buffer.append(text[posn:])
            file.text = ''.join(buffer)









class Match(binding.Component):
    """Thing that finds/updates version strings"""

    matchString = binding.requireBinding('string to match')
    isOptional = False

    def editVersion(self, text, posn, old, new, write, filename):
        old = self.matchString % old
        new = self.matchString % new
        foundOld = text.find(old,posn)
        foundNew = text.find(new,posn)
        if foundOld==-1:
            if foundNew==-1:
                if isOptional:
                    return posn
                else:
                    raise ValueError(
                        "Couldn't find %r or %r in %s" % (old,new,filename)
                    )
            else:
                newPosn = foundNew + len(new)
                write(text[posn:newPosn])
                return newPosn
        else:
            write(text[posn:foundOld])
            write(new)
            newPosn = foundOld + len(old)
            return newPosn

    def fromString(klass, text):
        """ZConfig constructor for 'Match' operator"""
        return klass(matchString=text)

    fromString = classmethod(fromString)

    def fromOptional(klass, text):
        """ZConfig constructor for 'OptionalMatch' operator"""
        return klass(matchString=text, isOptional=True)

    fromOptional = classmethod(fromOptional)


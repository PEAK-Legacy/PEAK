"""URL parsing and formatting tools"""

import re, sys
from types import StringTypes
from urllib import unquote

from peak.api import exceptions, NOT_GIVEN
from peak.binding.once import classAttr, Once, Activator
from peak.model.elements import Struct
from peak.model.features import structField
from peak.model.datatypes import String, Integer
from peak.model.interfaces import IType
from peak.interface import adapt, implements, classProvides
from interfaces import *
from arithmetic import *
from names import CompoundName

__all__ = [
    'Base', 'Field', 'RequiredField', 'IntField', 'NameField', 'Collection',
    'ParseError', 'MissingData', 'Syntax', 'Sequence', 'Repeat', 'Optional',
    'Tuple', 'Named', 'Extract', 'Conversion', 'Alternatives', 'Text', 'Set',
    'Match', 'parse', 'format',
]


class ParseError(exceptions.InvalidName): pass
class MissingData(Exception): pass














class Syntax(object):

    """Translator between data and strings"""

    __slots__ = ()

    def parse(self, aStr, visitor, startAt=0):
        """Parse 'aStr' at 'startAt', call 'visitor(result)', return next pos

        Return a 'ParseError' instance if no match"""
        raise NotImplementedError

    def format(self, data, visitor):
        """Pass formatted 'data' to 'visitor()'"""
        raise NotImplementedError

    def withTerminators(self, terminators):
        """Return a version of this syntax using the specified terminators"""
        raise NotImplementedError

    def getOpening(self,closing):
        """Possible opening characters for this match, based on 'closing'"""
        raise NotImplementedError

    def __adapt__(klass, ob):
        if isinstance(ob,str):
            return Text(ob)
        elif isinstance(ob,tuple):
            return Optional(*ob)

    __adapt__ = classmethod(__adapt__)










class Sequence(Syntax):

    __metaclass__ = Activator

    closingChars = ''

    def __init__(self, *__args, **__kw):
        self.initArgs = __args
        self.__dict__.update(__kw)
        self.actualSyntax   # force computation

    def parse(self, aStr, visitor, startAt=0):

        pos = startAt
        data = []

        for parser in self.actualSyntax:
            pos = parser.parse(aStr, data.append, pos)
            if isinstance(pos,ParseError):
                return pos

        map(visitor, data)
        return pos


    def format(self, data, visitor):
        for parser in self.actualSyntax:
            parser.format(data,visitor)


    def withTerminators(self, terminators):
        return self.__class__(*self.initArgs, **{'closingChars':terminators})


    def getOpening(self,closing):
        return self.openingChars





    def actualSyntax(self, d, a):

        obs = [adapt(ob,Syntax) for ob in self.initArgs]
        obs.reverse()

        closeAll = self.closingChars
        closeCtx = ''

        syn = []
        for ob in obs:
            ob = ob.withTerminators(closeAll+closeCtx)
            closeCtx = ob.getOpening(closeCtx)
            syn.append(ob)

        self.openingChars = closeCtx
        syn.reverse()
        return syn

    actualSyntax = Once(actualSyntax)






















class Optional(Sequence):

    """Wrapper that makes a construct optional"""

    def parse(self, aStr, visitor, startAt=0):
        pos = super(Optional,self).parse(aStr,visitor,startAt)
        if isinstance(pos,ParseError):
            return startAt
        return pos

    def format(self, data, visitor):

        """Return a value if any non-empty non-constant parts"""

        out = []
        tc = 0

        for parser in self.actualSyntax:

            isText = adapt(parser,Text,None)

            if isText:
                parser.format(data,out.append)
                tc +=1
            else:
                try:
                    parser.format(data,out.append)
                except MissingData:
                    out.append('')

        if len(filter(None,out))>tc:
            map(visitor,out)

    def getOpening(self,closing):
        return self.openingChars+closing






class Text(Syntax, str):

    def __new__(klass,value,sensitive=False):
        self=super(Text,klass).__new__(klass,value)
        self.sensitive = sensitive
        return self

    def parse(self, aStr, visitor, startAt=0):

        pos = startAt+len(self)
        if self.sensitive:
            if aStr[startAt:pos]==self:
                return pos
        elif aStr[startAt:pos].lower()==self.lower():
            return pos

        return ParseError(
            "Expected %r, found %r at position %d in %r" %
            (self, aStr[startAt:pos], startAt, aStr)
        )


    def format(self,data,visitor):
        visitor(self)


    def withTerminators(self,terminators):
        return self


    def getOpening(self,closing):
        if self:
            if self.sensitive:
                return self[0]
            else:
                return self[0].lower()+self[0].upper()
        return closing

    def __adapt__(klass,ob):
        pass

class Repeat(Sequence):

    minCt = 0
    maxCt = None
    sepMayTerm = False  # is separator allowed as terminator?

    separator = Text('')

    def parse(self, aStr, visitor, startAt=0):

        parser = super(Repeat,self)
        pos = startAt
        data = []

        pos = parser.parse(aStr, data.append, pos)

        if isinstance(pos,ParseError):
            if self.minCt>0:
                return pos  # it's an error
            else:
                return startAt  # non-error empty match

        ct = 1; maxCt = self.maxCt
        while pos<len(aStr) and (maxCt is None or ct<maxCt):

            pos = self.sep.parse(aStr, data.append, pos)
            if isinstance(pos,ParseError):
                break   # no more items

            pos = parser.parse(aStr, data.append, pos)
            if isinstance(pos,ParseError):
                if self.sepIsTerm:
                    break   # if sep can be term, it's okay to end here
                return pos  # otherwise pass the error up

            ct += 1

        visitor(data)   # treat repeat as a list
        return pos


    def format(self, data, visitor):

        if not data:
            return

        parser = super(Repeat,self)

        for d in data[:-1]:
            parser.format(d,visitor)
            self.sep.format(d,visitor)

        parser.format(data[-1],visitor)


    def withTerminators(self,terminators):

        kw = self.__dict__.copy()
        if 'actualSyntax' in kw:
            del kw['actualSyntax']

        kw['closingChars'] = terminators + self.sep.getOpening('')

        del kw['initArgs']
        return self.__class__(*self.initArgs, **kw)


    sep = Once(lambda self,d,a: adapt(self.separator, Syntax))














class Tuple(Sequence):

    """Sequence of unnamed values, rendered as a tuple (e.g. key/value)"""

    def parse(self, aStr, visitor, startAt=0):

        out = []
        pos = super(Tuple,self).parse(aStr, out.append, startAt)

        if isinstance(pos,ParseError):
            return pos

        visitor( tuple(out) )
        return pos


    def format(self, data, visitor):
        p = 0
        for parser in self.actualSyntax:
            v = adapt(parser,Text,None)
            if v is None:
                parser.format(data[p],visitor)
                p+=1
            else:
                parser.format(None,visitor)
















class Match(Syntax):

    """Match a regex, or longest string that doesn't include a terminator"""

    output = ''
    openingChars = ''
    terminators = ''

    def __init__(self,pattern=None,**kw):
        self.__dict__.update(kw)
        if isinstance(pattern,str):
            pattern = re.compile(pattern)
        self.pattern = pattern

    def parse(self, aStr, visitor, startAt=0):
        if self.pattern is None:
            pos = startAt
            while pos<len(aStr) and aStr[pos] not in self.terminators:
                pos += 1
        else:
            m = self.pattern.match(aStr, startAt)
            if not m:
                return ParseError(
                    "Failed match for %r at position %d in %r" %
                    (self.re.pattern, startAt, aStr)
                )
            pos = m.end()
        return pos

    def withTerminators(self,terminators):
        ob = self.__class__(**self.__dict__)
        ob.terminators = terminators
        return ob

    def getOpening(self,closing):
        return self.openingChars





    def format(self,data,visitor):

        if self.pattern is None:
            visitor(data)
        elif self.output is not None:
            visitor(self.output)
        else:
            raise MissingData   # we don't know how to format!

































class Extract(Syntax):

    """Return matched subitem as a string, possibly handling quote/unquote"""

    __slots__ = 'item', 'unquote', 'terminators'

    def __init__(self, item=Match(), unquote=True, terminators=''):
        self.item = adapt(item,Syntax)
        self.unquote = unquote
        self.terminators = terminators

    def parse(self, aStr, visitor, startAt=0):
        out = []
        pos = self.item.parse(aStr, out.append, startAt)
        if isinstance(pos,ParseError):
            return pos

        if self.unquote:
            visitor(unquote(aStr[startAt:pos]))
        else:
            visitor(aStr[startAt:pos])
        return pos


    def withTerminators(self,terminators):
        return self.__class__(
            self.item.withTerminators(terminators), self.unquote, terminators
        )

    def getOpening(self,closing):
        return self.item.getOpening(closing)

    def format(self,data,visitor):
        if self.unquote:
            for t in self.terminators:
                data = data.replace(t, '%'+hex(256+ord(t))[-2:].upper())
        visitor(data)




class Named(Syntax):

    """Named value - converts to/from dictionary/items"""

    __slots__ = 'name', 'item'

    def __init__(self, name, item=Extract()):
        self.name = name
        self.item = adapt(item,Syntax)

    def withTerminators(self,terminators):
        return self.__class__(
            self.name, self.item.withTerminators(terminators)
        )

    def getOpening(self,closing):
        return self.item.getOpening(closing)


    def parse(self, aStr, visitor, startAt=0):
        def visit(value):
            visitor( (self.name,value) )
        return self.item.parse(aStr, visit, startAt)

    def format(self, data, visitor):
        try:
            value = data[self.name]
        except KeyError:
            raise MissingData(self.name)
        return self.item.format(value, visitor)











class Conversion(Syntax):

    formatter = str
    converter = str
    canBeEmpty = False
    defaultValue = NOT_GIVEN


    def __init__(self, item=Extract(), **kw):
        self.__dict__.update(kw)
        self.item = adapt(item, Syntax)


    def parse(self, aStr, visitor, startAt=0):

        out = []
        pos = self.item.parse(aStr, out.append, startAt)
        if isinstance(pos,ParseError):
            return pos

        out, = out
        value = self.converter(out)

        visitor(value)
        return pos


    def withTerminators(self, terminators):

        kw = self.__dict__.copy()
        kw['item'] = self.item.withTerminators(terminators)
        return self.__class__(**kw)


    def getOpening(self,closing):
        return self.item.getOpening(closing)





    def format(self, data, visitor):

        if self.defaultValue is not NOT_GIVEN and data==self.defaultValue:
            if self.canBeEmpty:
                return
            else:
                raise MissingData

        value = self.formatter(data)
        if not value and not self.canBeEmpty:
            raise MissingData

        self.item.format(value, visitor)




























class Alternatives(Syntax):

    """Match one out of many alternatives"""

    __slots__ = 'alternatives'

    def __init__(self, *alternatives):
        self.alternatives = [adapt(a,Syntax) for a in alternatives]

    def withTerminators(self,terminators):
        return self.__class__(
            *tuple([a.withTerminators(terminators) for a in self.alternatives])
        )

    def getOpening(self,closing):
        return ''.join([a.getOpening('') for a in self.alternatives])

    def parse(self, aStr, visitor, startAt=0):
        for parser in self.alternatives:
            pos = parser.parse(aStr,visitor,startAt)
            if not isinstance(pos,ParseError):
                return pos
        else:
            return ParseError(
                "Parse error at position %d in %r" % (startAt,aStr)
            )

    def format(self, data, visitor):
        for parser in self.alternatives:
            try:
                out = []
                parser.format(data,out.append)
            except MissingData:
                continue
            if out:
                map(visitor,out)
                return
        else:
            raise MissingData


class Set(Alternatives):

    def parse(self, aStr, visitor, startAt=0):

        targets = list(self.alternatives)
        pos = startAt

        while targets and pos<len(aStr):
            for parser in targets:
                newPos = parser.parse(aStr,visitor,pos)
                if isinstance(newPos,ParseError):
                    continue
                else:
                    pos = newPos    # XXX handle separator?
                    targets.remove(parser)
                    break
            else:
                return ParseError(
                    "No match found at position %d in %r" % (pos,aStr)
                )

        return pos

    def format(self, data, visitor):

        for parser in self.alternatives:
            try:
                out = []
                parser.format(data,out.append)
            except MissingData:
                continue
            if out:
                map(visitor,out)

    def withTerminators(self,terminators):
        # make sure alternatives consider each other as possible terminators
        return super(Set,self).withTerminators(
            terminators+''.join([a.getOpening('') for a in self.alternatives])
        )


def parse(aStr, syntax):

    out = []
    pos = syntax.parse(aStr, out.append)

    if isinstance(pos,ParseError):
        raise pos

    if pos<len(aStr):
        raise ParseError(
            "Expected EOF, found %r at position %d in %r" %
            (aStr[pos:], pos, aStr)
        )

    return dict(out)


def format(aDict, syntax):
    out = []
    syntax.format(aDict, out.append)
    return ''.join(out)




















class Field(structField):
    referencedType = String
    defaultValue = None
    unquote = True
    syntax = None
    separator = ''
    sepMayTerm = False
    canBeEmpty = False

    def _syntax(feature,d,a):

        syntax = feature.syntax

        if syntax is None:
            syntax = getattr(feature.typeObject, 'mdl_syntax', None)

        if syntax is None:
            syntax = Conversion(
                Extract(unquote = feature.unquote),
                converter = feature.fromString, # XXX need toString also
                defaultValue = feature._defaultValue,
                canBeEmpty = feature.canBeEmpty
            )

        if feature.isMany:
            syntax = Repeat(
                syntax,
                minCt = feature.lowerBound,
                maxCt = feature.upperBound,
                separator = feature.separator,
                sepMayTerm = feature.sepMayTerm
            )

        return Named( feature.attrName, syntax )

    _syntax = classAttr(Once(_syntax))

    def __conform__(feature,protocol):
        if protocol is Syntax:
            return feature._syntax

class Collection(Field):
    upperBound = None
    separator  = ''


class RequiredField(Field):
    lowerBound = 1
    defaultValue = NOT_GIVEN


class IntField(Field):
    referencedType = Integer


class NameField(RequiredField):
    unquote = False

























class Base(Struct):

    """Basic scheme/body URL"""

    implements(IAddress)
    classProvides(IAddressFactory, IType)

    pattern          = None
    syntax           = None
    nameKind         = URL_KIND
    nameAttr         = None
    supportedSchemes = ()

    def supportsScheme(klass, scheme):
        return scheme in klass.supportedSchemes or not klass.supportedSchemes

    supportsScheme = classmethod(supportsScheme)

    def __init__(self, scheme=None, body=None, **__kw):
        scheme = scheme or self.__class__.defaultScheme
        if not self.supportsScheme(scheme):
            raise exceptions.InvalidName(
                "Unsupported scheme %r for %r" % (scheme, self.__class__)
            )
        if body:
            data = self.parse(scheme,body)
            data.update(__kw)
            __kw = data

        __kw['scheme']=scheme
        __kw['body']=body

        for f in self.__class__.mdl_features:
            if f.isRequired and not f.attrName in __kw:
                raise InvalidName("Missing %s field in %r" % f.attrName, __kw)

        super(Base,self).__init__(**__kw)
        self.__class__.body._setup(self, self.getCanonicalBody())



    class scheme(structField):
        referencedType = String
        sortPosn = 1

    class body(structField):
        referencedType = String
        sortPosn = 2
        defaultValue = ''

    def retrieve(self, refInfo, name, context, attrs=None):
        pass

    def __str__(self):
        return "%s:%s" % (self.scheme, self.body)



























    __add__  = name_add
    __sub__  = name_sub
    __radd__ = name_radd
    __rsub__ = name_rsub


    def addName(self,other):

        if not other:
            return self

        if not isName(other):
            raise TypeError(
                "Only names can be added to URLs", self, other
            )

        if other.nameKind==URL_KIND:
            return other

        na = self.nameAttr

        if not na:
            raise TypeError(
                "Addition not supported for pure address types", self, other
            )

        d = dict(self._hashAndCompare)
        d['body'] = None    # before the below in case 'na' is "body"
        d[na] = getattr(self,na,CompoundName(())) + other

        res = self.__class__(**d)
        return res









    def __split(self,d,a):

        d = dict(self._hashAndCompare)
        na = self.nameAttr

        if na:
            if na in d:
                nic = d[na]; del d[na]
            else:
                nic = getattr(self,na)
        else:
            nic = CompoundName(())

        d['body'] = ''
        auth = self.__class__(**d)
        return auth, nic

    __split = Once(__split)

    def getAuthorityAndName(self):
        return self.__split


    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
            ','.join(
                ['%s=%r' % (k,v) for (k,v) in self._hashAndCompare]
            )
        )

    def _hashAndCompare(self,d,a):
        klass = self.__class__
        omitBody = klass.mdl_featureNames != ('scheme','body')
        return tuple(
            [(f,getattr(self,f)) for f in self.__class__.mdl_featureNames
                if (not omitBody or f!='body')
            ]
        )

    _hashAndCompare = Once(_hashAndCompare)

    def parse(klass,scheme,body):
        if klass.syntax is not None:
            return parse(body, klass.syntax)

        p = klass.pattern
        if isinstance(p,str):
            p = klass.pattern = re.compile(p)

        if p is not None:
            m = p.match(body)
            if m:
                na = klass.nameAttr
                d=m.groupdict(NOT_GIVEN)
                for k,v in d.items():
                    f = getattr(klass,k)
                    if v is NOT_GIVEN:
                        del d[k]
                        continue
                    if k!=na and f.unquote:
                        d[k] = v = unquote(v)
                    d[k] = f.fromString(v)
                return d
            else:
                raise exceptions.InvalidName("%s:%s" % (scheme,body))

        return {}

    parse = classmethod(parse)

    def getCanonicalBody(self):
        if self.syntax is not None:
            return format(dict(self._hashAndCompare),self.syntax)
        return self.body

    defaultScheme = classAttr(
        Once(
            lambda s,d,a: s.supportedSchemes and s.supportedSchemes[0]
                or None
        )
    )

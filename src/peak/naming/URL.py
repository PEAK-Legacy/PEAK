"""URL parsing and formatting tools"""

from types import StringTypes
from urllib import unquote

from peak.api import exceptions, NOT_GIVEN
from peak.binding.once import classAttr, Once
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
    'ParseError', 'MissingData', 'Rule', 'Sequence', 'Repeat', 'Optional',
    'Tuple', 'Named', 'ExtractString', 'Conversion', 'Alternatives',
    'Set', 'MatchString', 'parse', 'format', 'ExtractQuoted', 'StringConstant'
]

from peak.util.fmtparse import *

















class ExtractQuoted(Rule):

    """Return matched subrule as a string, possibly handling quote/unquote"""

    __slots__ = 'rule', 'unquote', 'terminators'

    def __init__(self, rule=MatchString(), unquote=True, terminators=''):
        self.rule = adapt(rule,Rule)
        self.unquote = unquote
        self.terminators = terminators

    def parse(self, inputStr, produce, startAt):
        out = []
        pos = inputStr.parse(self.rule, out.append, startAt)
        if isinstance(pos,ParseError):
            return pos

        if self.unquote:
            produce(unquote(inputStr[startAt:pos]))
        else:
            produce(inputStr[startAt:pos])
        return pos


    def withTerminators(self,terminators):
        return self.__class__(
            self.rule.withTerminators(terminators), self.unquote, terminators
        )

    def getOpening(self,closing):
        return self.rule.getOpening(closing)

    def format(self,data,write):
        if self.unquote:
            for t in self.terminators:
                data = data.replace(t, '%'+hex(256+ord(t))[-2:].upper())
        write(data)




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
                ExtractQuoted(unquote = feature.unquote),
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
        if protocol is Rule:
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
                raise exceptions.InvalidName(
                    "Missing %s field in %r" % f.attrName, __kw
                )

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


"""URL parsing and formatting tools"""

import re
from types import StringTypes
from urllib import unquote

from peak.api import exceptions, NOT_GIVEN
from peak.binding.once import classAttr, Once, Activator
from peak.model.elements import Struct
from peak.model.features import structField
from peak.model.datatypes import String, Integer
from peak.model.interfaces import IType
from peak.interface import implements, classProvides
from interfaces import *
from arithmetic import *
from names import CompoundName

__all__ = [
    'Base', 'Field',
]


class MissingField(Exception):
    pass


class Field(structField):
    referencedType = String
    defaultValue = None

class RequiredField(structField):
    referencedType = String
    lowerBound = 1

class IntField(structField):
    referencedType = Integer









class Base(Struct):
    """Basic scheme/body URL"""

    implements(IAddress)
    classProvides(IAddressFactory, IType)

    pattern          = None
    nameKind         = URL_KIND
    nameAttr         = None
    dont_unquote     = ()
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

        super(Base,self).__init__(scheme=scheme, body=body, **__kw)
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

        # XXX check delegate to URLSyntax first

        p = klass.pattern

        if isinstance(p,str):
            p = klass.pattern = re.compile(p)

        if p is not None:
            m = p.match(body)
            if m:
                no_unquote = klass.dont_unquote
                na = klass.nameAttr
                d=m.groupdict(NOT_GIVEN)
                for k,v in d.items():
                    if v is NOT_GIVEN:
                        del d[k]
                        continue
                    elif k not in no_unquote and k!=na:
                        d[k] = v = unquote(v)
                    d[k] = getattr(klass,k).fromString(v)
                return d
            else:
                raise exceptions.InvalidName("%s:%s" % (scheme,body))

        return {}

    parse = classmethod(parse)

    def getCanonicalBody(self):
        # XXX recompute body from other fields, if present
        return self.body

    defaultScheme = classAttr(
        Once(
            lambda s,d,a: s.supportedSchemes and s.supportedSchemes[0]
                or None
        )
    )

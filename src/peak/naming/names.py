from __future__ import generators

"""Name, Syntax, and Reference Objects"""

from peak.api import *

import re
from types import StringTypes
from urllib import unquote

from interfaces import *
from syntax import *
from arithmetic import *

from peak.binding.once import Activator, Once
from peak.interface import implements, classProvides

__all__ = [
    'AbstractName', 'toName', 'CompositeName', 'CompoundName',
    'NNS_NAME', 'ParsedURL', 'URLMatch',
    'LinkRef', 'NNS_Reference', 'isBoundary', 'crossesBoundaries',
]


def isBoundary(name):
    return name and name.nameKind==COMPOSITE_KIND and len(name)<3 \
           and not name[-1]

def crossesBoundaries(name):
    return name and name.nameKind==COMPOSITE_KIND and ( len(name)>1
        or name and not name[0] )










class AbstractName(tuple):

    implements(IPath)

    nameKind    = None

    def __new__(klass, *args):

        if args:

            s = args[0]

            if isinstance(s,klass):
                return s

            elif isinstance(s,StringTypes):
                return klass.parse(s)

        return super(AbstractName,klass).__new__(klass,*args)

    def __str__(self):
        return self.format()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, list(self))

    __add__  = name_add
    __sub__  = name_sub
    __radd__ = name_radd
    __rsub__ = name_rsub

    def __getslice__(self, *args):
        return self.__class__(
            super(AbstractName,self).__getslice__(*args)
        )






    # syntax-based methods

    syntax = UnspecifiedSyntax

    def format(self):
        return self.syntax.format(self)

    def parse(klass, name):
        return klass(klass.syntax.parse(name))

    parse = classmethod(parse)


    # IType methods

    def mdl_fromString(klass,aString):
        return klass.parse(aString)

    mdl_fromString = classmethod(mdl_fromString)


    def mdl_toString(klass,instance):
        return instance.format()

    mdl_toString = classmethod(mdl_toString)


    def mdl_normalize(klass, value):
        return klass(value)

    mdl_normalize = classmethod(mdl_normalize)


    mdl_syntax       = None       # XXX?
    mdl_defaultValue = NOT_GIVEN






URLMatch = re.compile('([-+.a-z0-9]+):',re.I).match

class URLMeta(Activator):

    def __init__(klass, name, bases, classDict):

        if 'pattern' in classDict:

            pattern = classDict['pattern']

            if isinstance(pattern,str):
                klass.pattern = re.compile(pattern)

        return super(URLMeta,klass).__init__(name, bases, classDict)



























class ParsedURL(object):

    __metaclass__    = URLMeta

    implements(IAddress)
    classProvides(IAddressFactory)

    nameKind         = URL_KIND

    nameAttr = None
    supportedSchemes = ()

    pattern      = ''
    dont_unquote = ()

    scheme = None
    body   = None


    defaultScheme = Once(
        lambda s,d,a: s.supportedSchemes and s.supportedSchemes[0]
            or None
    )

    def __init__(self, scheme=None, body=None):
        self.setup(locals())















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

        d = dict(self.__state)
        d[na] = getattr(self,na,CompoundName(())) + other

        res = self.__new__(self.__class__)
        res.__dict__.update(d)

        return res








    def parse(self, scheme, body):

        if self.pattern:
            m = self.pattern.match(body)

            if m:
                d=m.groupdict(NOT_GIVEN)
                for k,v in d.items():
                    if v is NOT_GIVEN:
                        del d[k]
                    elif k not in self.dont_unquote and k!=self.nameAttr:
                        d[k] = unquote(v)
                d['scheme'] = scheme
                d['body']   = body
                return d

            else:
                raise exceptions.InvalidName(str(self))

        return locals()

    def retrieve(self, refInfo, name, context, attrs=None):
        pass

    def __str__(self):
        return "%s:%s" % (self.scheme, self.body)

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__,
            ','.join(['%s=%r' % (k,v) for (k,v) in self.__state])
        )

    def supportsScheme(klass, scheme):
        return scheme in klass.supportedSchemes or not klass.supportedSchemes

    supportsScheme = classmethod(supportsScheme)





    def setup(self, initargs):

        def update(d):
            for k in d.keys():
                if k.startswith('_') or k=='self':
                    del d[k]

            self.__dict__.update(d)

        update(initargs)

        d = self.__dict__
        scheme = d.get('scheme')
        body   = d.get('body')

        if not scheme:
            scheme = self.defaultScheme
            d['scheme'] = scheme

        if not self.supportsScheme(scheme):
            raise exceptions.InvalidName(
                "Unsupported scheme", scheme
            )

        if body is not None:
            update(self.parse(scheme, body))

    def __setattr__(self, n, v):
        raise AttributeError, "Immutable object"

    def __state(self,d,a):
        is_descr = self.__class__.__all_descriptors__.__contains__
        keys = [k for k in d if not is_descr(k)]
        keys.sort()
        if 'body' in d and keys<>['body','scheme']:
            keys.remove('body')

        return tuple([(k,d[k]) for k in keys])

    __state = Once(__state)

    __hash  = Once( lambda s,d,a: hash(s.__state) )

    def __hash__(self):
        return self.__hash

    def __cmp__(self,other):
        return cmp(self.__state, other)

    def __split(self,d,a):

        d = dict(self.__state)
        na = self.nameAttr

        if na:
            if na in d:
                nic = d[na]; del d[na]
            else:
                nic = getattr(self,na)
        else:
            nic = CompoundName(())

        auth = self.__new__(self.__class__)
        auth.__dict__.update(d)
        return auth, nic

    __split = Once(__split)

    def getAuthorityAndName(self):
        return self.__split












class CompositeName(AbstractName):

    """A name whose parts may belong to different naming systems

        Composite name strings consist of name parts separated by forward
        slashes.  URL-encoding (%2F) is used to quote any slashes in each
        part.  Subclasses of 'CompositeName' may define a different
        'separator' attribute instead of '"/"', to use a different syntax."""

    nameKind = COMPOSITE_KIND
    separator = '/'

    def format(self):
        sep = self.separator
        enc = "%%%02X" % ord(sep)
        n = [str(s).replace(sep,enc) for s in self]

        if not filter(None,n):
            n.append('')

        return '/'.join(n)


    def parse(klass, name, firstPartType=None):

        # XXX Should we unescape anything besides separator?
        sep = klass.separator
        en1 = "%%%02X" % ord(sep)
        en2 = en1.lower()
        parts = [p.replace(en1,sep).replace(en2,sep) for p in name.split(sep)]

        if not filter(None,parts):
            parts.pop()

        if parts and firstPartType is not None:
            parts[0] = firstPartType(parts[0])
            if len(parts)==1: return parts[0]
        return klass(parts)

    parse = classmethod(parse)

class CompoundName(AbstractName):

    """A multi-part name with all parts in the same naming system"""

    nameKind = COMPOUND_KIND
    syntax   = FlatSyntax

    def asCompositeType(klass):

        """Get a 'CompositeName' subclass using this as first-element parser"""

        class _CompositeName(CompositeName):

            def mdl_fromString(_CNClass,aString):
                # Parse plain composite name, using this as compound parser
                name = CompositeName.parse(aString, klass)
                if isinstance(name, klass):
                    return CompositeName([name])
                return name

            mdl_fromString = classmethod(mdl_fromString)


            def mdl_normalize(_CNClass, value):
                if isinstance(value, klass):
                    # normalize compound as part of Composite
                    return CompositeName([value])
                return CompositeName(value)

            mdl_normalize = classmethod(mdl_normalize)


        return _CompositeName


    asCompositeType = classmethod(asCompositeType)





def toName(aName, nameClass=CompoundName, acceptURL=1):

    """Convert 'aName' to a Name object

        If 'aName' is already a 'Name', return it.  If it's a string or
        Unicode object, attempt to parse it.  Returns an 'OpaqueURL' if
        'acceptURL' is set and the string is a URL (per RFC 1738).  Otherwise,
        use 'nameClass' to construct a Name object from the string.

        If 'aName' is neither a Name nor a string/Unicode object, an
        'exceptions.InvalidName' is raised.
    """

    if isinstance(aName,StringTypes):

        if acceptURL and URLMatch(aName):
            import URL
            return URL.Base.mdl_fromString(aName)

        return (nameClass or CompoundName)(aName)

    elif IName.isImplementedBy(aName):
        return aName

    else:
        raise exceptions.InvalidName(aName)


NNS_NAME = CompositeName.parse('/',CompoundName)












class LinkRef(object):

    """Symbolic link"""

    __slots__ = 'linkName'

    def __init__(self, linkName):
        self.linkName = linkName

    def __repr__(self):
        return "LinkRef(%s)" % `self.linkName`


class NNS_Reference(object):

    """Next Naming System reference"""

    __slots__ = 'relativeTo'

    def __init__(self, relativeTo):
        self.relativeTo = relativeTo

    def __repr__(self):
        return "NNS_Reference(%s)" % `self.relativeTo`


















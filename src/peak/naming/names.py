from __future__ import generators

"""Name, Syntax, and Reference Objects"""

from peak.api import *

import re
from types import StringTypes
from urllib import quote,unquote

from interfaces import *

from peak.util.Struct import struct, structType
from peak.binding.once import Activator, Once

__all__ = [
    'AbstractName', 'toName', 'CompositeName', 'CompoundName',
    'Syntax', 'UnspecifiedSyntax', 'NNS_NAME', 'ParsedURL', 'URLMatch',
    'LinkRef', 'NNS_Reference', 'FlatSyntax', 'isBoundary',
    'crossesBoundaries',
]

class UnspecifiedSyntax(object):

    """Dummy (null) Syntax"""

    def parse(*args):
        raise NotImplementedError

    def format(self,name):
        return "%s(%r)" % (name.__class__.__name__, list(name))


def isBoundary(name):
    return name and name.nameKind==COMPOSITE_KIND and len(name)<3 \
           and not name[-1]

def crossesBoundaries(name):
    return name and name.nameKind==COMPOSITE_KIND and ( len(name)>1
        or name and not name[0] )

def any_plus_url(n1,n2):
    return n2


def compound_plus_compound(n1,n2):
    return n1.__class__(list(n1)+list(n2))


def composite_plus_composite(n1,n2):

    l = list(n1)
    last = l.pop()
    
    if not last:
        l.extend(list(n2))
    else:
        l.append(last + n2[0])
        l.extend(list(n2)[1:])

    if len(l)==1 and l[0]:
        return l[0]

    return CompositeName(l)


def composite_plus_compound(n1,n2):

    l = list(n1)
    last = l.pop()

    if not last:
        l.append(n2)
    else:
        l.append(last+n2)

    if len(l)==1 and l[0]:
        return l[0]

    return CompositeName(l)


def compound_plus_composite(n1,n2):

    l = list(n2)
    first = l[0]

    if first:
        l[0] = n1+first
    else:
        l[0] = n1
        
    if len(l)==1 and l[0]:
        return l[0]

    return CompositeName(l)

def url_plus_other(n1,n2):
    return n1.addName(n2)

_name_addition = {
    (COMPOSITE_KIND,      URL_KIND): any_plus_url,
    (COMPOUND_KIND,       URL_KIND): any_plus_url,
    (URL_KIND,            URL_KIND): any_plus_url,
    (URL_KIND,       COMPOUND_KIND): url_plus_other,
    (URL_KIND,      COMPOSITE_KIND): url_plus_other,

    (COMPOSITE_KIND,COMPOSITE_KIND): composite_plus_composite,
    (COMPOUND_KIND,  COMPOUND_KIND): compound_plus_compound,
    (COMPOSITE_KIND, COMPOUND_KIND): composite_plus_compound,
    (COMPOUND_KIND, COMPOSITE_KIND): compound_plus_composite,
}

def _name_add(self, other):
    if self and other:
        return _name_addition[self.nameKind,other.nameKind](self,other)
    return self or other

def _name_radd(self, other):
    if self and other:
        return _name_addition[other.nameKind,self.nameKind](other,self)
    return self or other

def same_minus_same(n1,n2):
    if n1.startswith(n2):
        return n1[len(n2):]


def compound_minus_composite(n1,n2):
    if len(n2)==1:
        return n1-n2[0]


def composite_minus_compound(n1,n2):
    if n1:
        p = n1[0]-n2
        if p is not None:
            return CompositeName([p]+list(n1)[1:])


_name_subtraction = {
    (COMPOSITE_KIND,COMPOSITE_KIND): same_minus_same,
    (COMPOUND_KIND,  COMPOUND_KIND): same_minus_same,
    (COMPOSITE_KIND, COMPOUND_KIND): composite_minus_compound,
    (COMPOUND_KIND, COMPOSITE_KIND): compound_minus_composite,
}


def _name_sub(self, other):
    if other:
        return _name_subtraction[self.nameKind,other.nameKind](self,other)
    return self


def _name_rsub(self, other):
    if self:
        return _name_subtraction[other.nameKind,self.nameKind](other,self)
    return other






class AbstractName(tuple):

    __implements__ = IName
    
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

    __add__  = _name_add
    __sub__  = _name_sub
    __radd__ = _name_radd
    __rsub__ = _name_rsub

    def __getslice__(self, *args):
        return self.__class__(
            super(AbstractName,self).__getslice__(*args)
        )

    def startswith(self, ob):
        return not ob or self[:len(ob)] == ob



    # syntax-based methods

    syntax = UnspecifiedSyntax()

    def format(self):
        return self.syntax.format(self)

    def parse(klass, name):
        return klass(klass.syntax.parse(name))

    parse = classmethod(parse)






























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
    __implements__   = IAddress

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

















    __add__  = _name_add

    __radd__ = _name_radd


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












class Syntax(object):

    """Name parser"""

    def __init__(self,

         direction=0,
         separator='',
         escape='',

         ignorecase=None,
         trimblanks=None,
         
         beginquote='',
         endquote='',
         beginquote2='',
         endquote2='',

         multi_quotes = False,
         decode_parts = True,

    ):

        self.multi_quotes = multi_quotes
        self.decode_parts = decode_parts
        self.direction    = direction
        self.separator    = separator

        if direction not in (-1,0,1):
            raise ValueError, "Direction must be 1, 0 (flat), or -1 (reverse)"

        if direction and not separator:
            raise ValueError, "Separator required for hierarchical syntax"

        if separator and not direction:
            raise ValueError, "Separator not meaningful for flat syntax"

        if endquote and not beginquote:
            raise ValueError, "End quote supplied without begin quote"


        if endquote2 and not beginquote2:
            raise ValueError, "End quote 2 supplied without begin quote 2"

        if beginquote2 and not beginquote:
            raise ValueError, "Begin quote 2 supplied without begin quote 1"

        endquote = endquote or beginquote    
        endquote2 = endquote2 or beginquote2

        quotes = beginquote,endquote,beginquote2,endquote2
        quotes = dict(zip(quotes,quotes)).keys()    # unique strings only

        self.metachars = filter(None,[escape] + quotes)
        
        if escape and quotes:
            self.escapeFunc = re.compile(
                "(" + '|'.join(
                    map(re.escape,
                        filter(None,self.metachars+[separator])
                    )
                ) + ")"
            ).sub
            self.escapeTo = re.escape(escape)+'\\1'

        self.escape = escape
        self.trimblanks = trimblanks
        self.ignorecase = ignorecase
        
        if beginquote2:
            self.quotes = (beginquote,endquote), (beginquote2,endquote2)
        elif beginquote:
            self.quotes = (beginquote,endquote),
        else:
            self.quotes = ()

        if escape:
            escapedChar = re.escape(escape)+'.|'
        else:
            escapedChar = ''


        quotedStrs = ''
        bqchars = ''
        
        for bq,eq in self.quotes:
            bq_ = re.escape(bq[:1])
            eq_ = re.escape(eq[:1])
            bq = re.escape(bq)
            eq = re.escape(eq)
            quotedStrs += \
                "%(bq)s(?:%(escapedChar)s[^%(eq_)s])*%(eq)s|" % locals()
            bqchars += bq_

        if separator:
            sep         = re.escape(separator)
            optionalSep = "(?:%s)?" % sep
            sepOrEof    = "(?:%s)|$" % sep
        else:
            sep, optionalSep, sepOrEof = '', '', '$'

        if sep or bqchars:
            charpat = "[^%s%s]" % (sep,bqchars)
        else:
            charpat = '.'

        if multi_quotes:
            content = "( (?: %(quotedStrs)s %(escapedChar)s %(charpat)s )* )"
        else:
            content = "( %(quotedStrs)s (?:%(escapedChar)s%(charpat)s)*    )"

        content = content % locals()        
        PS = """
            %(optionalSep)s
            %(content)s         # Contents in the middle
            (?=%(sepOrEof)s)    # separator or EOF last
        """ % locals()

        self.parseRe = re.compile(PS,re.X)

        if escape:
            self.unescape = re.compile(re.escape(escape)+'(.)').sub

    def format(self, seq):
    
        """Format a sequence as a string in this syntax"""
        
        if self.escape and self.decode_parts:
            n = [self.escapeFunc(self.escapeTo,part) for part in seq]
        else:
            n = [part for part in seq]

        if not filter(None,n):
            n.append('')

        if self.direction<0:
            n.reverse()

        return self.separator.join(n)

























    def parse(self, aStr):
    
        """Parse a string according to defined syntax"""

        startStr = aStr
        
        sep = self.separator

        for m in self.metachars:
            if aStr.find(m)>=0: break
            
        else:

            if sep:
                n = aStr.split(sep)
                if self.trimblanks:
                    n=[s.strip() for s in n]
                if not filter(None,n): n.pop()
                if self.direction<0:
                    n.reverse()
                return n

            else:
                return [aStr]

        n = []
        ps = self.parseRe
        quotes = self.quotes
        escape = self.escape
        unescape = self.unescape
        tb = self.trimblanks
        do_unescape = self.decode_parts and escape
        use_quotes  = self.decode_parts and quotes and not self.multi_quotes

        if aStr.startswith(sep):
            n.append('')
            aStr=aStr[len(sep):]




        while aStr:
            m = ps.match(aStr)

            if m:
                s = m.group(1)  # get the content of the path segment

                if use_quotes:
                    for bq,eq in quotes:
                        if s.startswith(bq):
                            # strip off surrounding quotes
                            s=s[len(bq):-len(eq)]
                            break

                if do_unescape and escape in s:
                    # unescape escaped characters
                    s = unescape('\\1',s)

                if tb:
                    s = s.strip()
                    
                n.append(s)
                aStr = aStr[m.end():]

            else:
                raise exceptions.InvalidName(startStr)

        if self.direction<0:
            n.reverse()

        return n











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

        if firstPartType is not None:
            parts[0] = firstPartType(parts[0])
            if len(parts)==1: return parts[0]
        return klass(parts)

    parse = classmethod(parse)

FlatSyntax = Syntax()

class CompoundName(AbstractName):

    """A multi-part name with all parts in the same naming system"""

    nameKind = COMPOUND_KIND
    syntax   = FlatSyntax


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
            m = URLMatch(aName)
            scheme, body = m.group(1), aName[m.end():]
            return ParsedURL(scheme,body)

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


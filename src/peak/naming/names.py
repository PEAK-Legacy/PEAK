from __future__ import generators

"""Name, Syntax, and Reference Objects"""

import re
from interfaces import *
from types import StringTypes
from peak.util.Struct import struct, structType
from peak import exceptions

__all__ = [
    'Name', 'toName', 'CompositeName', 'CompoundName', 'OpaqueURL',
    'Syntax', 'UnspecifiedSyntax', 'NNS_NAME', 'ParsedURL', 'URLMatch',
    'PropertyName', 'LinkRef', 'NNS_Reference'
]


class UnspecifiedSyntax(object):

    """Dummy (null) Syntax"""

    def parse(*args):
        raise NotImplementedError

    def format(self,name):
        return "%s(%r)" % (name.__class__.__name__, list(name))















class Name(tuple):

    __implements__ = IName
    
    isComposite = 0
    isCompound  = 0
    isURL       = 0

    def __new__(klass, *args):

        if args:

            s = args[0]

            if isinstance(s,klass):
                return s

            elif isinstance(s,StringTypes):
                return klass.parse(s)
                
        return super(Name,klass).__new__(klass,*args)


    def __str__(self):
        return self.format()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, list(self))

    def __add__(self, other):
        return self.__class__(
            super(Name,self).__add__(other)
        )

    def __getslice__(self, *args):
        return self.__class__(
            super(Name,self).__getslice__(*args)
        )



    # syntax-based methods

    syntax = UnspecifiedSyntax()

    def format(self):
        return self.syntax.format(self)

    def parse(klass, name):
        return klass(klass.syntax.parse(name))

    parse = classmethod(parse)






























class URLMeta(structType):

    classmethods = structType.classmethods + (
        'fromURL', 'supportsScheme'
    )

    def __new__(meta, name, bases, classDict):

        if 'pattern' in classDict:
            pattern = classDict['pattern']
            if isinstance(pattern,str):
                classDict['pattern']=re.compile(pattern)

        return super(URLMeta,meta).__new__(meta, name, bases, classDict)



























URLMatch = re.compile('([-+.a-z0-9]+):',re.I).match

class OpaqueURL(struct):

    __metaclass__ = URLMeta

    __implements__ = IName

    __fields__ = 'scheme', 'body'
    
    _supportedSchemes = ()

    isComposite = 0
    isCompound  = 0
    isURL       = 1

    def fromString(klass, name):

        m = URLMatch(name)

        if m:
            scheme, body = m.group(1), name[m.end():]            
            return tuple.__new__(klass,(scheme, body))
            
        raise exceptions.InvalidName(name)
        

    def __str__(self):
        return '%s:%s' % (self.scheme, self.body)

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, str(self))

    def supportsScheme(klass, scheme):
        return scheme in klass._supportedSchemes or not klass._supportedSchemes


    



class ParsedURL(OpaqueURL):

    __implements__ = IAddress

    def retrieve(self, refInfo, name, context, attrs=None):
        pass

    pattern = ''


    def fromString(klass, name):

        m = URLMatch(name)
        if m: return klass.fromURL(OpaqueURL(name))
        raise exceptions.InvalidName(name)


    def fromOther(klass, url):
        if IName.isImplementedBy(url) and url.isURL:
            return klass.fromURL(url)
            
        raise exceptions.InvalidName(name)


    def fromURL(klass, url):

        if klass.supportsScheme(url.scheme):

            m = klass.pattern.match(url.body)

            if m:
                d=m.groupdict()
                d['scheme'] = url.scheme
                d['body']   = url.body
                
                return klass(**d)
                
        raise exceptions.InvalidName(url)
        


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
                 
                 #ava_separator=None,
                 #typeval_separator=None,
        ):

        self.direction = direction
        self.separator = separator

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
                "%(bq)s(?:%(escapedChar)s[^%(eq_)s])%(eq)s|" % locals()
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

        PS = """
            # Each path segment begins with an optional separator:
            %(optionalSep)s

            # Which is followed by either:
            (   %(quotedStrs)s                      # a quoted string
                (?:%(escapedChar)s%(charpat)s)*     # or a string w/no unescaped quotes or slashes
            )           
            # And it must be followed by a separator or EOF:
            (?=%(sepOrEof)s)
        """ % locals()

        self.parseRe = re.compile(PS,re.X)
        
        if escape:
            self.unescape = re.compile(re.escape(escape)+'(.)').sub

    def format(self, seq):
    
        """Format a sequence as a string in this syntax"""
        
        if self.escape:
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
        
        if aStr.startswith(sep):
            n.append('')
            aStr=aStr[len(sep):]






        while aStr:
            m = ps.match(aStr)

            if m:
                s = m.group(1)  # get the content of the path segment

                for bq,eq in quotes:
                    if s.startswith(bq):
                        # strip off surrounding quotes
                        s=s[len(bq):-len(eq)]
                        break

                if escape and escape in s:
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












class CompositeName(Name):

    """A name whose parts may belong to different naming systems

        Composite name strings consist of name parts separated by forward
        slashes.  Each part can be double or single-quoted, and any enclosed
        slashes or quotes of the opposite kind are ignored as separators.
        Backslashes can be used to escape quotes, backslashes, and forward
        slashes.
    """

    syntax = Syntax(
        direction=1,
        separator='/',
        beginquote='"',
        beginquote2="'",
        escape="\\"
    )

    isComposite = 1


class CompoundName(Name):

    """A multi-part name with all parts in the same naming system"""

    isCompound = 1

    def __new__(klass, name, syntax=Syntax() ):

        if isinstance(name,StringTypes):
            name = syntax.parse(name)
            
        name = super(CompoundName,klass).__new__(klass,name)
        name.syntax = syntax       
        return name





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
            return OpaqueURL.fromString(aName)

        return nameClass(aName)

    elif IName.isImplementedBy(aName):
        return aName

    else:
        raise exceptions.InvalidName(aName)


NNS_NAME = CompositeName('/')













pnameValidChars = re.compile( r"([-+*?!:._a-z0-9]+)", re.I ).match

class PropertyName(str):

    def __new__(klass, *args):

        self = super(PropertyName,klass).__new__(klass,*args)

        valid = pnameValidChars(self)

        if not valid or valid.end()<len(self):
            raise exceptions.InvalidName(
                "Invalid characters in property name", self
            )

        parts = self.split('.')

        if '' in parts or not parts:
            raise exceptions.InvalidName(
                "Empty part in property name", self
            )

        if '*' in self:
            if '*' not in parts or parts.index('*') < (len(parts)-1):
                raise exceptions.InvalidName(
                    "'*' must be last part of wildcard property name", self
                )
            
        if '?' in self:
            if '?' in parts or self.index('?') < (len(self)-1):
                    raise exceptions.InvalidName(
                        "'?' must be at end of a non-empty part", self
                    )

        return self






    def isWildcard(self):
        return self.endswith('*')

    def isDefault(self):
        return self.endswith('*')

    def isPlain(self):
        return self[-1:] not in '?*'


    def matchPatterns(self):

        if not self.isPlain():
            raise exceptions.InvalidName(
                "Can't match patterns against special property names", self
            )

        yield self

        name = self
        
        while '.' in name:
            name = name[:name.rindex('.')]
            yield name+'.*'

        yield '*'
        yield self
        yield self+'?'


    def getBases(self):
        return ()


    def extends(self, other, strict=1):
        return not strict and self==other





    def asPrefix(self):

        p = self

        if p.endswith('*'):
            p=p[:-1]

        if p and not p.endswith('.'):
            p=p+'.'

        return p


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


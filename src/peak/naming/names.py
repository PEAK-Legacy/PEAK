from __future__ import generators

"""Name, Syntax, and Reference Objects"""

from peak.api import *

import re
from types import StringTypes
from urllib import unquote

from interfaces import *

from peak.util.Struct import struct, structType

__all__ = [
    'Name', 'toName', 'CompositeName', 'CompoundName',
    'Syntax', 'UnspecifiedSyntax', 'NNS_NAME', 'ParsedURL', 'URLMatch',
    'LinkRef', 'NNS_Reference'
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






























URLMatch = re.compile('([-+.a-z0-9]+):',re.I).match

class URLMeta(type):

    def __init__(klass, name, bases, classDict):

        if 'pattern' in classDict:

            pattern = classDict['pattern']

            if isinstance(pattern,str):
                klass.pattern = re.compile(pattern)

        return super(URLMeta,klass).__init__(name, bases, classDict)


class ParsedURL(object):

    __metaclass__  = URLMeta
    __implements__ = IAddress

    isComposite = 0
    isCompound  = 0
    isURL       = 1

    _defaultScheme = None
    _supportedSchemes = ()
    
    pattern = ''

    dont_unquote = ()

    scheme = None
    body   = None







    def __init__(self, scheme=None, body=None):
        self.setup(locals())
    
    def parse(self, scheme, body):

        if self.pattern:
            m = self.pattern.match(body)

            if m:
                d=m.groupdict(NOT_GIVEN)
                for k,v in d.items():
                    if v is NOT_GIVEN:
                        del d[k]
                    elif k not in self.dont_unquote:
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
        return "%s(%r)" % (self.__class__.__name__, str(self))

    def supportsScheme(klass, scheme):
        return scheme in klass._supportedSchemes or not klass._supportedSchemes
        
    supportsScheme = classmethod(supportsScheme)



    def setup(self, initargs):

        def update(d):
            for k in d.keys():
                if k.startswith('_') or k=='self':
                    del d[k]

            self.__dict__.update(d)

        update(initargs)

        scheme = initargs.get('scheme') or self._defaultScheme
        body   = initargs.get('body')

        if not self.supportsScheme(scheme):
            raise exceptions.InvalidName(
                "Unsupported scheme", scheme
            )

        if body is not None:
            update(self.parse(scheme, body))


    def __setattr__(self, n, v):
        raise AttributeError, "Immutable object"

















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
            m = URLMatch(aName)
            scheme, body = m.group(1), aName[m.end():]
            return ParsedURL(scheme,body)

        return (nameClass or CompoundName)(aName)

    elif IName.isImplementedBy(aName):
        return aName

    else:
        raise exceptions.InvalidName(aName)


NNS_NAME = CompositeName('/')











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


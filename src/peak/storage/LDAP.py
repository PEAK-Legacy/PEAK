from __future__ import generators
from peak.api import *
from connections import ManagedConnection, AbstractCursor
from urllib import quote, unquote
from interfaces import *
from peak.util.Struct import makeStructType

__all__ = [
    'LDAPConnection', 'LDAPCursor', 'ldapURL'
]


try:
    import ldap
    from ldap import SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE

except:
    ldap = None
    SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE = range(3)


scope_map = {'one': SCOPE_ONELEVEL, 'sub': SCOPE_SUBTREE, '': SCOPE_BASE}



















class LDAPCursor(AbstractCursor):

    """LDAP pseudo-cursor"""

    timeout      = -1
    msgid        = None
    bulkRetrieve = False

    disconnects = binding.bindSequence('import:ldap.SERVER_DOWN',)

    def close(self):

        if self.msgid is not None:
            self._conn.abandon(self.msgid)
            self.msgid = None

        super(LDAPCursor,self).close()


    def execute(self,dn,scope,filter='objectclass=*',attrs=None,dnonly=0):

        try:
            self.msgid = self._conn.search(dn,scope,filter,attrs,dnonly)

        except self.disconnects:
            self.errorDisconnect()


    def errorDisconnect(self):
        self.close()
        self.getParentComponent().close()
        raise
    

    def nextset(self):
        """LDAP doesn't do multi-sets"""
        return False




    def __iter__(self, onlyOneSet=True):

        msgid, timeout = self.msgid, self.timeout

        if msgid is None:
            raise ValueError("No operation in progress")

        getall = self.bulkRetrieve and 1 or 0
        fetch = self._conn.result

        ldapEntry = makeStructType('ldapEntry',
            [], __implements__ = IRow, __module__ = __name__,
        )

        newEntry = ldapEntry.fromMapping; restype = None

        while restype != 'RES_SEARCH_RESULT':

            try:
                restype, data = fetch(msgid, getall, timeout)

            except self.disconnects:
                self.errorDisconnect()

            if restype is None:               
                yield None  # for timeout errors

            for dn,m in data:

                m['dn']=dn

                try:
                    yield newEntry(m)                

                except ValueError:
                    map(ldapEntry.addField, m.keys())
                    yield newEntry(m)        

        # Mark us as done with this query
        self.msgid = None

class LDAPConnection(ManagedConnection):

    cursorClass = LDAPCursor

    def _open(self):

        address = self.address
        ext = address.extensions

        conn = ldap.open(address.host, address.port)

        if 'bindname' in ext and 'x-bindpw' in ext:
            conn.simple_bind_s(
                ext['bindname'][1], ext['x-bindpw'][1]
            )

        return conn


    def __getattr__(self, attr):
        return getattr(self.connection, attr)




















class ldapURL(naming.ParsedURL):

    """RFC2255 LDAP URLs, with the following changes:
    
    1) Additionally supports ldaps and ldapi (TLS and Unix Domain variants).

    2) Supports familiar (http, ftp-like) [user[:pass]@] syntax before
    the hostport part of the URL. These are translated into critical bindname
    and x-bindpw extensions. That is:
    
        ldap://foo:bar@localhost
    
    is treated as:
    
        ldap://localhost/????!bindname=foo,!x-bindpw=bar

    We do this for backwards compatability with some applications which
    used the old AppUtils LDAP module, and because the standard
    second syntax is quite unpleasant, especially when the bindname
    DN contains commas that have to be quoted as %2C.

    Attributes provided:

    host            hostname of server (or empty string)
    port            port number (integer, default 389)
    basedn          the dn provided (or empty string)
    attrs           tuple of attributes to retrieve, None if unspecified
    scope           SCOPE_BASE (default), SCOPE_ONELEVEL, or SCOPE_SUBTREE
    filter          search filter (or empty string)
    extensions      dictionary mapping extension names to tuples of
                    (critical, value) where critical is 0 or 1, and
                    value is a string.
    critical        a list of extension names that are critical, so
                    code may easily check for unsupported extenstions
                    and throw an error.        
    """
    
    _supportedSchemes = ('ldap', 'ldaps', 'ldapi')



    def __init__(self, scheme=None, body=None,
                 host='', port=389, basedn='', attrs=None, 
                 scope=SCOPE_BASE, filter=None, extensions=None,
    ):
        extensions = extensions or {}
        self.setup(locals())


    def parse(self, scheme, body):

        _bindinfo = None
        extensions = self.extensions
        
        _hostport = body

        if _hostport[:2] == '//':
            _hostport = _hostport[2:]
        else:
            raise exceptions.InvalidName(self.url)

        if '/' in _hostport:
            _hostport, _rest = hostport.split('/', 1)
        else:
            _rest = ''

        if _hostport:

            if '@' in _hostport:
                _bindinfo, _hostport = _hostport.split('@', 1)

            if ':' in _hostport:
                host, port = map(unquote, _hostport.split(':', 1))
                try:
                    port = int(port)
                except:
                    raise exceptions.InvalidName(self.url)
            else:
                host = unquote(_hostport)



        if _bindinfo:

            if ':' in _bindinfo:
                _bindinfo, _bindpw = map(unquote, _bindinfo.split(':', 1))
                extensions['x-bindpw'] = (1, _bindpw)

            else:
                _bindinfo = unquote(_bindinfo)

            extensions['bindname'] = (1, _bindinfo)
        
        if _rest:

            if '?' in _rest:
                basedn, _rest = rest.split('?', 1)
                basedn = unquote(basedn)

            else:
                basedn = unquote(_rest)
                rest = ''

        _rest = (_rest.split('?') + ['']*3)[:4]

        if _rest[0]:
            attrs = tuple(map(unquote, _rest[0].split(',')))
            
        scope = scope_map.get(unquote(_rest[1]).lower())

        if scope is None:
            raise exceptions.InvalidName(self.url)

        if _rest[2]:
            filter = unquote(_rest[2])








        if _rest[3]:

            _exts = map(unquote, _rest[3].split(','))

            for _e in _exts:

                _crit = 0

                if _e[0] == '!':
                    _crit = 1; _e = e[1:]

                _k, _v = _e.split('=', 1)
                extensions[_k.lower()] = (_crit, _v)

        critical = [_k for (_k, (_crit, _v)) in extensions.items() if _crit]
        critical = tuple(critical)
        
        return locals()


    def retrieve(self, refInfo, name, context, attrs=None):

        return LDAPConnection(
            context.creationParent,
            address = self
        )



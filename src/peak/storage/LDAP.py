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



    __fields__ = 'scheme', 'body', 'host', 'port', 'basedn', 'attrs', \
                'scope', 'filter', 'extensions', 'critical'
    
    def fromURL(klass, url):

        bindinfo = None
        host = basedn = ''
        port = 389
        extensions = {}
        
        scheme, body = url.scheme, url.body
        
        hostport = url.body
        if hostport[:2] == '//':
            hostport = hostport[2:]
        else:
            raise exceptions.InvalidName(url)

        if '/' in hostport:
            hostport, rest = hostport.split('/', 1)
        else:
            rest = ''

        if hostport:
            if '@' in hostport:
                bindinfo, hostport = hostport.split('@', 1)

            if ':' in hostport:
                host, port = map(unquote, hostport.split(':', 1))
                try:
                    port = int(port)
                except:
                    raise exceptions.InvalidName(url)
            else:
                host = unquote(hostport)

        if bindinfo:
            if ':' in bindinfo:
                bindinfo, bindpw = map(unquote, bindinfo.split(':', 1))
                extensions['x-bindpw'] = (1, bindpw)
            else:
                bindinfo = unquote(bindinfo)
            extensions['bindname'] = (1, bindinfo)
        
        if rest:
            if '?' in rest:
                basedn, rest = rest.split('?', 1)
                basedn = unquote(basedn)
            else:
                basedn = unquote(rest)
                rest = ''

        rest = (rest.split('?') + ['']*3)[:4]

        if rest[0]:
            attrs = tuple(map(unquote, rest[0].split(',')))
        else:
            attrs = None
            
        scope = unquote(rest[1]).lower()
        if scope == 'one':
            scope = SCOPE_ONELEVEL
        elif scope == 'sub':
            scope = SCOPE_SUBTREE
        else:
            scope = SCOPE_BASE

        filter = unquote(rest[2])

        if rest[3]:
            exts = map(unquote, rest[3].split(','))
            for e in exts:
                crit = 0
                if e[0] == '!':
                    crit = 1; e = e[1:]
                k, v = e.split('=', 1)
                extensions[k.lower()] = (crit, v)

        critical = a = []; a = a.append
        for k, (crit, v) in extensions.items():
            if crit:
                a(k)
        critical = tuple(critical)
        
        return klass.extractFromMapping(locals())


    def retrieve(self, refInfo, name, context, attrs=None):

        return LDAPConnection(
            context.creationParent,
            address = self
        )



from peak.naming.api import *
from urllib import quote, unquote

try:
    from ldap import SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE
except:
    SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE = range(3)



class ldapURL(ParsedURL):
    """RF2255 LDAP URLs, with the following changes:
    
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
    attrs           list of attributes to retrieve, [] if unspecified
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
    
    def _fromURL(self, url):
        bindinfo = None
        self.host = self.basedn = ''
        self.port = 389
        self.extensions = {}
        
        hostport = self.body
        if hostport[:2] == '//':
            hostport = hostport[2:]
	else:
            raise InvalidNameException(url)

        if '/' in hostport:
            hostport, rest = hostport.split('/', 1)
        else:
            rest = ''

        if hostport:
            if '@' in hostport:
                bindinfo, hostport = hostport.split('@', 1)

            if ':' in hostport:
                self.host, port = map(unquote, hostport.split(':', 1))
                try:
                    self.port = int(port)
                except:
                    raise InvalidNameException(url)
            else:
                self.host = unquote(hostport)

        if bindinfo:
            if ':' in bindinfo:
                bindinfo, bindpw = map(unquote, bindinfo.split(':', 1))
                self.extensions['x-bindpw'] = (1, bindpw)
            else:
                bindinfo = unquote(bindinfo)
            self.extensions['bindname'] = (1, bindinfo)
        
        if rest:
            if '?' in rest:
                basedn, rest = rest.split('?', 1)
                self.basedn = unquote(basedn)
            else:
                self.basedn = unquote(rest)
                rest = ''

        rest = (rest.split('?') + ['']*3)[:4]

        if rest[0]:
            self.attrs = map(unquote, rest[0].split(','))
        else:
            self.attrs = []
            
        scope = unquote(rest[1]).lower()
        if scope == 'one':
            self.scope = SCOPE_ONELEVEL
        elif scope == 'sub':
            self.scope = SCOPE_SUBTREE
        else:
            self.scope = SCOPE_BASE

        self.filter = unquote(rest[2])

        if rest[3]:
            exts = map(unquote, rest[3].split(','))
            for e in exts:
                crit = 0
                if e[0] == '!':
                    crit = 1; e = e[1:]
                k, v = e.split('=', 1)
                self.extensions[k.lower()] = (crit, v)

        self.critical = a = []; a = a.append
        for k, (crit, v) in self.extensions.items():
            if crit:
                a(k)

from peak.naming.api import *
from urllib import quote, unquote

try:
    import ldap
    from ldap import SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE
except:
    ldap = None
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
            raise InvalidNameException(url)

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
                    raise InvalidNameException(url)
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

    fromURL = classmethod(fromURL)

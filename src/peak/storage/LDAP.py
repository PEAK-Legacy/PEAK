from __future__ import generators
from peak.api import *
from connections import ManagedConnection, AbstractCursor
from urllib import unquote
from interfaces import *
from peak.util.Struct import makeStructType
from peak.util.imports import importObject

__all__ = [
    'LDAPConnection', 'LDAPCursor', 'ldapURL', 'SCHEMA_PREFIX'
]

SCHEMA_PREFIX = PropertyName('peak.ldap.field_converters.*')

try:
    import ldap
    from ldap import SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE

except:
    ldap = None
    SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE = range(3)


scope_map = {'one': SCOPE_ONELEVEL, 'sub': SCOPE_SUBTREE, '': SCOPE_BASE}


def NullConverter(descr,value):
    return value













class LDAPCursor(AbstractCursor):

    """LDAP pseudo-cursor"""

    timeout      = -1
    msgid        = None
    bulkRetrieve = False
    attrs        = None

    disconnects = binding.bindSequence('import:ldap.SERVER_DOWN',)

    def close(self):

        if self.msgid is not None:
            self._conn.abandon(self.msgid)
            self.msgid = None

        super(LDAPCursor,self).close()


    def execute(self,dn,scope,filter='objectclass=*',attrs=None,dnonly=0):
        try:
            self.msgid = self._conn.search(dn,scope,filter,attrs,dnonly)
            if attrs:
                if 'dn' not in attrs:
                    attrs = ('dn',)+tuple(attrs)
                self.attrs = attrs

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

        attrs  = self.attrs or ()
        schema = SCHEMA_PREFIX.of(self)

        def getConverter(field):
            return importObject(schema.get(field,NullConverter), globals())

        conv = [(getConverter(f), f) for f in attrs]

        ldapEntry = makeStructType('ldapEntry',
            attrs, __implements__ = IRow, __module__ = __name__,
        )

        mkTuple  = tuple.__new__
        fieldMap = ldapEntry.__fieldmap__

















        restype = None

        while restype != 'RES_SEARCH_RESULT':

            try:
                restype, data = fetch(msgid, getall, timeout)

            except self.disconnects:
                self.errorDisconnect()

            if restype is None:
                yield None  # for timeout errors

            for dn,m in data:

                m['dn']=dn

                fm=fieldMap.copy()
                fm.update(m)

                if len(fm)>len(fieldMap):
                    for k in m.keys():
                        if k not in fieldMap:
                            ldapEntry.addField(k)
                            conv.append( (getConverter(k),k) )

                yield mkTuple(ldapEntry,
                    [ c(f,m.get(f)) for (c,f) in conv ]
                )


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




















class distinguishedName(naming.CompoundName):

    syntax = naming.PathSyntax(

        direction    = -1,      # DN's go right-to-left
        separator    = ',',     # are comma-separated
        trimblanks   = True,    # and blanks are ignored

        beginquote   = '"',     # LDAP uses double quotes for quoting, and
        multi_quotes = True,    #   can have multiple quoted strings per RDN.

        escape       = '\\',    # Escape character is backslash, but
        decode_parts = False,   #   don't try to unquote/unescape RDNs!

    )


























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

    supportedSchemes = ('ldap', 'ldaps', 'ldapi')
    nameAttr = 'basedn'


    class host(model.structField):
        referencedType=model.String
        defaultValue=None

    class port(model.structField):
        referencedType=model.Integer
        defaultValue=389

    class basedn(model.structField):
        referencedType=model.String
        defaultValue=''

    class attrs(model.structField):
        referencedType=model.Any    # XXX
        defaultValue=None

    class scope(model.structField):
        referencedType=model.Integer
        defaultValue=SCOPE_BASE

    class filter(model.structField):
        referencedType=model.String
        defaultValue=None

    class extensions(model.structField):
        referencedType=model.Any    # XXX
        defaultValue={}

    class critical(model.structField):
        referencedType=model.Any    # XXX
        defaultValue = ()










    def parse(_self, _scheme, _body):

        _bindinfo = None
        _hostport = _body
        extensions = {}

        if _hostport[:2] == '//':
            _hostport = _hostport[2:]
        else:
            raise exceptions.InvalidName('%s:%s' % (_scheme,_body))

        if '/' in _hostport:
            _hostport, _rest = _hostport.split('/', 1)
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
                    raise exceptions.InvalidName('%s:%s' % (_scheme,_body))
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
                basedn = naming.CompositeName.parse(basedn,distinguishedName)

            else:
                basedn = naming.CompositeName.parse(_rest,distinguishedName)
                _rest = ''

        else:
            basedn = naming.CompositeName('')

        _rest = (_rest.split('?') + ['']*3)[:4]

        if _rest[0]:
            attrs = tuple(map(unquote, _rest[0].split(',')))

        scope = scope_map.get(unquote(_rest[1]).lower())

        if scope is None:
            raise exceptions.InvalidName(str(self))

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

        return dict(
            [(k,v) for (k,v) in locals().items()
                if not k.startswith('_')
            ]
        )


    def retrieve(self, refInfo, name, context, attrs=None):

        return LDAPConnection(
            context.creationParent, context.creationName,
            address = self
        )

    # XXX def getCanonicalBody(self):
























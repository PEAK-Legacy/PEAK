from protocols import Interface, Attribute
from peak.api import *
from interfaces import *
import sys, socket


def getConstants(module,prefix):
    p = len(prefix)
    d = module.__dict__
    return [(k[p:].lower(),v) for k,v in d.items() if k.startswith(prefix)]


class ExtendedEnum(model.Enumeration):

    def mdl_toString(klass,x):
        if x in klass: return klass[x].name
        return str(int(x))

    def mdl_fromString(klass,x):
        if x.lower() in klass:
            return klass[x.lower()]
        return klass._convert(x)

    def _convert(klass,x):
        return int(x)

    _convert = classmethod(_convert)

    def __int__(self):
        return self._hashAndCompare











class SocketFamily(ExtendedEnum):

    __values = model.enumDict( getConstants(socket,'AF_') )


class SocketType(ExtendedEnum):

    __values = model.enumDict( getConstants(socket, 'SOCK_') )


class SocketProtocol(ExtendedEnum):

    __values = model.enumDict( getConstants(socket, 'IPPROTO_') )

    def _convert(klass,x):
        try:
            return int(x)
        except ValueError:
            return socket.getprotobyname(x)

    _convert = classmethod(_convert)


class FileDescriptor(ExtendedEnum):

    stdin = model.enum(0)
    stdout = model.enum(1)
    stderr = model.enum(2)













class socketURL(naming.URL.Base):

    def listen_sockets(self, maxsocks=sys.maxint):
        sockets = []

        for res in self.listen_addrs():
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
                s.bind(sa)
                s.listen(5) # should will be made configurable
                sockets.append(s)
                if len(sockets) >= maxsocks:
                    break
            except socket.error, msg:
                pass

        if not sockets:
            raise socket.error, msg

        return sockets




















class tcpudpURL(socketURL):

    protocols.advise(
        instancesProvide = [IClientSocketAddr, IListenSocketAddr]
    )

    supportedSchemes = {
        'tcp' : socket.SOCK_STREAM,
        'udp' : socket.SOCK_DGRAM
    }

    class host(naming.URL.RequiredField): pass

    class port(naming.URL.Field): pass

    syntax = naming.URL.Sequence(
        '//', host, (':', port), ('/',)
    )

    def connect_addrs(self):
        return socket.getaddrinfo(self.host, self.port,
            0, self.supportedSchemes[self.scheme])

    def listen_addrs(self):
        host = self.host
        if not host or host == '*':
            host = None

        return socket.getaddrinfo(host, self.port,
            0, self.supportedSchemes[self.scheme], 0, socket.AI_PASSIVE)











class unixURL(socketURL):

    protocols.advise(
        instancesProvide = [IClientSocketAddr, IListenSocketAddr]
    )

    supportedSchemes = {
        'unix' : socket.SOCK_STREAM,
        'unix.dg' : socket.SOCK_DGRAM
    }

    class path(naming.URL.RequiredField): pass

    syntax = naming.URL.Sequence(path)

    def connect_addrs(self):
        return [
            (socket.AF_UNIX, self.supportedSchemes[self.scheme], 0, None, self.path)
        ]

    listen_addrs = connect_addrs




















def ClientConnect(addr):
    """Attempt to connect to an IClientSocketAddr"""

    sock = None
    for res in addr.connect_addrs():
        af, socktype, proto, canonname, sa = res
        try:
            sock = socket.socket(af, socktype, proto)
            sock.connect(sa)
        except socket.error, msg:
            if sock:
                sock.close()
            sock = None
            continue
        break

    if sock is None:
        raise socket.error, msg

    return sock



protocols.declareAdapter(
    lambda o,p: ClientConnect(o),
    provides=[IClientSocket],
    forProtocols=[IClientSocketAddr]
)


protocols.declareAdapter(
    lambda o,p: o.listen_sockets(maxsocks=1)[0],
    provides=[IListeningSocket],
    forProtocols=[IListenSocketAddr]
)






class fdURL(naming.URL.Base):
    """fd:fileno[,type=af[/kind[/protocol]]]

    'fileno' can be an integer, or one of 'stdin', 'stdout', 'stderr'

    'af' can be the lowercase form of any 'socket.AF_*' constant, e.g.
    'unix', 'inet', 'inet6', etc.  ('inet' is the default if unspecified.)

    'kind' can be the lowercase form of any 'socket.SOCK_*' constant, e.g.
    'stream', 'dgram', 'raw', etc.  ('stream' is the default if unspecified.)

    'protocol' can be an integer, or the lowercase form of any
    'socket.IPPROTO_*' constant, e.g. 'ip', 'icmp', 'udp', etc.  It can also
    be the name of a protocol that will be looked up using
    'socket.getprotobyname()'.  ('ip' is the default if unspecified.)

    Example::

        fd:stdin,type=inet6/dgram/udp
    """

    supportedSchemes = 'fd',

    class fileno(naming.URL.IntField):
        referencedType = FileDescriptor

    class af(naming.URL.IntField):
        referencedType = SocketFamily
        defaultValue   = SocketFamily.inet
        canBeEmpty     = True

    class stype(naming.URL.Field):
        referencedType = SocketType
        defaultValue   = SocketType.stream
        canBeEmpty     = True

    class proto(naming.URL.IntField):
        referencedType = SocketProtocol
        defaultValue   = SocketProtocol.ip
        canBeEmpty     = True

    syntax = naming.URL.Sequence(
        fileno, (',type=', af, ('/', stype, ('/', proto)))
    )

    def asSocket(self):
        return socket.fromfd(self.fileno, self.af, self.stype, self.proto)


protocols.declareAdapter(
    lambda o,p: o.asSocket(),
    provides=[IClientSocket,IListeningSocket],
    forTypes=[fdURL]
)





























from protocols import Interface, Attribute
from peak.api import *
from interfaces import *
import sys, socket

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
    supportedSchemes = {
        'tcp' : socket.SOCK_STREAM,
        'udp' : socket.SOCK_DGRAM
    }
    
    class host(naming.URL.RequiredField): pass

    class port(naming.URL.Field): pass
        
    syntax = naming.URL.Sequence(
        ('//',), host, (':', port), ('/',)
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
        
    protocols.advise(
        instancesProvide = [IClientSocketAddr, IListenSocketAddr]
    )
                


class unixURL(socketURL):
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
    
    protocols.advise(
        instancesProvide = [IClientSocketAddr, IListenSocketAddr]
    )

    

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



protocols.declareAdapterForProtocol(
    IClientSocket,
    lambda o,p: ClientConnect(o),
    IClientSocketAddr
)


protocols.declareAdapterForProtocol(
    IListeningSocket,
    lambda o,p: o.listen_sockets(maxsocks=1)[0],
    IListenSocketAddr
)


fd_map = {'stdin': '0', 'stdout': '1', 'stderr': '2'}
fd_fmt = {0: 'stdin', 1: 'stdout', 2: 'stderr'}

class fdURL(naming.URL.Base):
    """
    fd:fileno[,type=af/kind]
    
    example:
        fd:stdin,type=inet6/dgram
    fileno can be an integer, or one of "stdin", "stdout", "stderr"
    """

    supportedSchemes = 'fd',
    
    class fileno(naming.URL.IntField):
        syntax = naming.URL.Conversion(
            converter = lambda x: int(fd_map.get(x.lower(), x)),
            formatter = lambda x: fd_fmt.get(x, str(x)),
        )

    class af(naming.URL.Field):
        defaultValue = getattr(socket, 'AF_UNIX', socket.AF_INET)
        syntax = naming.URL.Conversion(
            converter = lambda x: getattr(socket, 'AF_' + x.upper())
        )
        
    class stype(naming.URL.Field):
        defaultValue = socket.SOCK_STREAM
        syntax = naming.URL.Conversion(
            converter = lambda x: getattr(socket, 'SOCK_' + x.upper())
        )

    syntax = naming.URL.Sequence(
        fileno, (',type=', af, '/', stype)
    )

    def asSocket(self):
        print self.fileno, self.af
        return socket.fromfd(self.fileno, self.af, self.stype)


protocols.declareAdapterForType(
    IClientSocket, lambda o,p: o.asSocket(), fdURL
)

protocols.declareAdapterForType(
    IListeningSocket, lambda o,p: o.asSocket(), fdURL
)

from protocols import Interface, Attribute
from peak.api import *
import socket, time


class ICB_URL(naming.URL.Base):
    supportedSchemes = {
        'icb' : 'peak.network.icb.ICBConnection'
    }
    
    defaultFactory = property(
        lambda self: self.supportedSchemes[self.scheme]
    )
    
    class user(naming.URL.Field): pass

    class passwd(naming.URL.Field): pass

    class server(naming.URL.RequiredField): pass

    class port(naming.URL.IntField):
        defaultValue = 7326
        
    class nick(naming.URL.Field): pass

    syntax = naming.URL.Sequence(
        ('//',), (user, (':', passwd), '@'), server, (':', port), ('/', (nick,))
    )

   

class ICBConnection(binding.Component):
    address = binding.requireBinding(
        "Address used to create the actual connection",
        suggestParent=False
    )


    target = binding.requireBinding(
        "an IICBListener we'll tell what's happening")

        
    def addToReactor(self, reactor):
        reactor.addReader(self)
        reactor.addWriter(self)

        
    def setTarget(self, target):
        self.target = adapt(target, IICBListener)
        self.target.connection = self
        
        
    def socket(self, d, a):
        a = self.address
        
        sock = None
        for res in socket.getaddrinfo(a.server, a.port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                sock = socket.socket(af, socktype, proto)
                sock.connect(sa)                        
            except socket.error, msg:
                # XXX log msg at DEBUG
                if sock:
                    sock.close()
                sock = None
                continue
            break

        if sock is None:
            raise socket.error, msg

        sock.setblocking(0)

        self._i_buf = ''; self._i_queue = []; self._o_queue = []
        self.sendPacket('a', self.address.user, self.address.nick,
            '', 'login', self.address.passwd or '')

        return sock

    socket = binding.Once(socket)
    

    def fileno(self):
        return self.socket.fileno()

        
    def sendPacket(self, cmd, *args):
        packet = cmd + '\x01'.join(args) + '\0'
        self._o_queue.append(chr(len(packet)) + packet)


    def sendPing(self, message=''):
        self.sendPacket('l', message)
        
        
    def sendPong(self, message):
        self.sendPacket('m', message)
        
        
    def gotoGroup(self, group):
        self.sendPacket('h', 'g', group)
        
        
    def publicMessage(self, msg):
        self.sendPacket('b', msg)

        
    def privateMessage(self, rcpt, msg):
        self.sendPacket('c', rcpt, msg)

        
    def brick(self, rcpt):
        self.sendPacket('c', 'brick', rcpt)
        
       
    def doWrite(self):
        oq = self._o_queue
        while oq:
            d = oq.pop(0)
            l = len(d)
            sl = self.socket.send(d)
            if sl < l:
                # push back remainder of packet
                oq.insert(0, d[sl:])
                return

                
    def doRead(self):
        d = self.socket.recv(2048)
        if not d:
            # XXX Socket closed!
            pass
            
        self._i_buf = self._i_buf + d
        pl = ord(self._i_buf[0])
        while self._i_buf and pl <= len(self._i_buf):
            pkt, self._i_buf = self._i_buf[:pl+1], self._i_buf[pl+1:]
            
            if pkt[-1] == '\0':
                self.receivePacket(pkt[1:-1])
            else:
                self.receivePacket(pkt[1:])

            if self._i_buf:
                pl = ord(self._i_buf[0])
            else:
                return

            
    def receivePacket(self, p):
        target = self.target
        kind, data = p[0], p[1:].split('\x01')
        if kind == 'a':
            target.loginOK()
        elif kind == 'b':
            target.publicMessage(*data)
        elif kind == 'c':
            target.privateMessage(*data)
        elif kind == 'd':
            target.Status(*data)
        elif kind == 'e':
            target.Error(data[0])
        elif kind == 'f':
            target.importantMessage(*data)
        elif kind == 'g':
            target.serverExit()
        elif kind == 'i' and data[0] == 'co':
            target.commandOutput(data[1])
        elif kind == 'j':
            target.protocolLevel(int(data[0]), data[1], data[2])
        elif kind == 'k':
            target.beepFrom(data[0])
        elif kind == 'l':
            target.gotPinf(data[0])
        else:
            target.unknownPacket(kind, data)


        
    def getObjectInstance(klass, context, refInfo, name, attrs=None):
        addr, = refInfo.addresses   # only 1 address supported for now
        return klass(address = addr)

    getObjectInstance = classmethod(getObjectInstance)
    

                
    protocols.advise(
        classProvides = [naming.IObjectFactory]
    )



class IICBListener(Interface):
    connection = Attribute("Connection we're listening to")
    
    def loginOK():
        """Login was successful"""
        
    def publicMessage(nick, message):
        """Public message was sent by nick"""
        
    def privateMessage(nick, message):
        """Private message was sent to us by nick"""
        
    def Status(category, message):
        """Status message in a given category"""
        
    def Error(message):
        """Report an error message"""
        
    def importantMessage(category, message):
        """Report an important message in category"""
        
    def serverExit(self):
        """Server Exiting"""
        
    def commandOutput(data):
        """Output resulting (maybe) from a command"""
        
    def protocolLevel(protover, host, server):
        """Initial protocol information"""
        
    def beepFrom(nick):
        """We got beeped by nick"""
        
    def gotPing(message):
        """We were pinged by the server"""

    def unknownPacket(kind, data):
        """We got an unknown packet"""



class ICBListenerBase(binding.Component):
    connection = binding.requireBinding(
        "Connection we're listening to",
        suggestParent=False
    )

    def loginOK(self):
        pass
        
    def publicMessage(self, nick, message):
        pass
        
    def privateMessage(self, nick, message):
        pass
        
    def Status(self, category, message):
        pass
        
    def Error(self, message):
        pass
        
    def importantMessage(self, category, message):
        pass
        
    def serverExit(self):
        pass
        
    def commandOutput(self, data):
        pass
        
    def protocolLevel(self, protover, host, server):
        pass
        
    def beepFrom(self, nick):
        pass
        
    def gotPing(self, message):
        self.connection.sendPong(message)

    def unknownPacket(self, kind, data):
        pass

    protocols.advise(
        instancesProvide = [IICBListener]
    )



class ICBCaptureToFile(ICBListenerBase):
    """Demonstration class that simply logs a history to a file"""

    file = binding.requireBinding("File to log to")
    
    def loginOK(self):
        self.file.write('Logged in.\n')
        
    def publicMessage(self, nick, message):
        self._logMessage('<%s>' % nick, message)
        
    def privateMessage(self, nick, message):
        self._logMessage('*%s*' % nick, message)
        
    def _logMessage(self, nick, msg):
        msg = "%s %s %s" % (time.strftime("[%H:%M]"), nick, msg)
        w = self.file.write
        while len(msg) > 79:
            l, msg = msg[:79] + '\n', '+' + msg[79:]
            w(l)
        w(msg + '\n')
                        
    def Status(self, category, message):
        self.file.write("*** info %s: %s\n" % (category, message))
        
    def Error(self, message):
        self.importantMessage("ERROR", message)
        
    def importantMessage(self, category, message):
        self.file.write(">>> %s %s\n" % (category, message))
        
    def serverExit(self):
        self.importantMessage("SERVER", "Exiting")
        
    def commandOutput(self, data):
        self.file.write("*** %s\n" % data)
        
    def protocolLevel(self, protover, host, server):
        self.file.write("Protocol Version %d\nHost: %s\nServer: %s\n" \
            % (protover, host, server))
        
    def beepFrom(self, nick):
        self.Status("BEEP", "beeped by %s" % nick)
        
    def unknownPacket(self, kind, data):
        self.importantMessage("UNKNOWN PACKET", `(kind, data)`)

from peak.api import *

import win32ui, dde, os, sys
from time import sleep


class DDEConnectionError(Exception):
    """Problem connecting to a DDE Server"""


class ServerManager(object):

    """This ensures that 'Shutdown()' gets called when the server is GC'd"""

    def __init__(self,name):
        server = self.server = dde.CreateServer()
        self.name = name
        server.Create(name)
        return server

    def __call__(self, serviceName, topicName):

        conn = dde.CreateConversation(self.server)

        LOG_DEBUG("Attempting DDE connection to (%s,%s) for %s" %
            (serviceName, topicName, self.name)
        )

        conn.ConnectTo(serviceName, topicName)
        return conn

    def __del__(self):
        if self.server is not None:
            LOG_DEBUG("Shutting down DDE server for %s" % self.name)
            self.server.Shutdown()
            self.server = None

    close = __del__



class ddeURL(naming.ParsedURL):

    """PEAK Win32 DDE URL

    Example::

        "win32.dde:service::topic;file=c:\\foo;retries=5;sleep=5"

    Syntax is 'service::topic' followed by semicolon-separated
    parameters, which may be 'file' to designate a file to be launched
    if the initial connection attempt is unsuccessful, 'retries' to
    indicate how many retries should occur if the initial attempt is
    unsuccessful, and 'sleep' to set the number of seconds to wait between
    retry attempts.

    These parameters are all available as attributes of the same names,
    including 'service' and 'topic'."""

    supportedSchemes = 'win32.dde',

    def __init__(self, scheme=None, body=None,
        service=None, topic=None, file=None, retries=10, sleep=1
    ):
        self.setup(locals())


    def retrieve(self, refInfo, name, context, attrs=None):
        return DDEConnection(
            context.creationParent,
            serviceName=self.service,
            topicName=self.topic,
            launchFile=self.file,
            retries=self.retries,
            sleepFor=self.sleep,
        )






    def parse(self, scheme, body):

        _l = body.split(';')
        _svct = _l[0].split('::',1)

        if len(_svct)<2:
            raise exceptions.InvalidName("Must contain 'service::topic'", body)

        service, topic = _svct

        _other = dict( [tuple(_x.split('=', 1)) for _x in _l[1:]] )

        for _x in 'retries', 'sleep':
            if _x in _other:
                _other[_x] = int(_other[_x])

        for _x in _other:
            if _x not in ('file','retries','sleep'):
                raise exceptions.InvalidName(
                    "Unrecognized parameter %s=%s" % (_x,_other[_x])
                )

        _other.update(locals())

        return _other
















class DDEConnection(storage.ManagedConnection):

    """Managed DDE connection"""

    serviceName = binding.requireBinding("Service name for DDE conversation")
    topicName   = binding.requireBinding("Topic name for DDE conversation")
    launchFile  = None

    retries  = 10
    sleepFor = 1


    def ddeServer(self,d,a):
        return ServerManager(str(binding.getComponentPath(self)))

    ddeServer = binding.Once(ddeServer)


    def __call__(self, requestStr):
        """Issue a DDE request (requestStr -> responseStr)"""
        return self.connection.Request(requestStr)

    def execute(self, commandStr):
        """Execute a DDE command"""
        return self.connection.Exec(commandStr)

    def poke(self, commandStr, data=None):
        """DDE Poke of command string and optional data buffer"""
        return self.connection.Poke(commandStr, data)












    def _open(self):

        attemptedLaunch = False

        for i in range(self.retries+1):

            try:
                conn = self.ddeServer(self.serviceName, self.topicName)
            except:
                t,v,tb = sys.exc_info()
                if (t,v) != ('error','ConnectTo failed'):
                    del t,v,tb,conn
                    raise
            else:
                return conn

            if attemptedLaunch:
                sleep(self.sleepFor)
            else:
                if self.launchFile:
                    LOG_DEBUG(("Launching %s" % self.launchFile), self)
                    os.startfile(self.launchFile)

                attemptedLaunch = True


        else:
            raise DDEConnectionError(
                "ConnectTo failed", self.serviceName, self.topicName
            )

    def _close(self):
        self.ddeServer.close()
        del self.ddeServer  # force shutdown








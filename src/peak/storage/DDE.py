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
        LOG_DEBUG("Shutting down DDE server for %s" % self.name)
        self.server.Shutdown()







class DDEConnection(storage.ManagedConnection):

    """Managed DDE connection"""

    # XXX there really should be an address class for these parameters...

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
        del self.ddeServer  # force shutdown









"""Start-on-busy-children plugin for ProcessSupervisor"""

from peak.api import *
from interfaces import *
from peak.running.process import ChildProcess

__all__ = ['BusyProxy', 'BusyStarter']


































class BusyProxy(ChildProcess):

    """Proxy for process that communicates its "busy" status"""
    log        = binding.Obtain('logging.logger:supervisor.busy-monitor')
    reactor    = binding.Obtain(running.IBasicReactor)
    busyStream = binding.Require("readable pipe from child")
    fileno     = binding.Obtain('busyStream/fileno')
    isBusy     = False

    def doRead(self):
        if self.isFinished:
            return

        try:
            # We need this try block because the pipe could close at any time
            byte = self.busyStream.read(1)
        except ValueError:
            # already closed
            return

        if byte=='+':
            self.log.log(logs.TRACE,"Child process %d is now busy", self.pid)
            self.isBusy = True
            self._notify()
        elif byte=='-':
            self.log.log(logs.TRACE,"Child process %d is now free", self.pid)
            self.isBusy = False
            self._notify()

    def _setStatus(self,status):
        super(BusyProxy,self)._setStatus(status)
        if self.isFinished:
            self.reactor.removeReader(self)
            self.busyStream.close()

    __onStart = binding.Make(
        lambda self: self.reactor.addReader(self),
        uponAssembly = True
    )


class BusyStarter(binding.Component):

    """Start processes for incoming connections if all children are busy"""

    children = binding.Make(dict)
    template = binding.Obtain(running.IProcessTemplate, suggestParent=False)
    stream   = binding.Obtain('./template/stdin')
    fileno   = binding.Obtain('./stream/fileno')
    reactor  = binding.Obtain(running.IBasicReactor)

    supervisor = binding.Obtain('..')

    def processStarted(self, proxy):
        proxy.addListener(self.statusChanged)
        self.children[proxy.pid] = proxy.isBusy
        self._delBinding('allBusy')

    def statusChanged(self, proxy):
        if not proxy.isRunning:
            if proxy.pid in self.children:
                del self.children[proxy.pid]
        else:
            self.children[proxy.pid] = proxy.isBusy

        self._delBinding('allBusy')

    allBusy = binding.Make(
        # not one is available
        lambda self: False not in self.children.values()
    )

    def doRead(self):
        if self.allBusy:
            self.supervisor.requestStart()

    __onStart = binding.Make(
        lambda self: self.reactor.addReader(self),
        uponAssembly = True
    )



"""Start-on-busy-children plugin for ProcessSupervisor"""
from __future__ import generators
from peak.api import *
from interfaces import *
from peak.running.process import ChildProcess

__all__ = ['BusyProxy', 'BusyStarter']


































class BusyProxy(ChildProcess):

    """Proxy for process that communicates its "busy" status"""
    log        = binding.Obtain('logger:supervisor.busy-monitor')
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
            self.log.trace("Child process %d is now busy", self.pid)
            self.isBusy = True
            self._notify()
        elif byte=='-':
            self.log.trace("Child process %d is now free", self.pid)
            self.isBusy = False
            self._notify()

    __onStart = binding.Make(
        lambda self: self.reactor.addReader(self),
        uponAssembly = True
    )

    def close(self):
        super(BusyProxy,self).close()
        self.reactor.removeReader(self)
        self.busyStream.close()



class BusyStarter(binding.Component):

    """Start processes for incoming connections if all children are busy"""

    children = binding.Make(dict)
    template = binding.Obtain(running.IProcessTemplate, suggestParent=False)
    stream   = binding.Obtain('./template/stdin')
    fileno   = binding.Obtain('./stream/fileno')
    reactor  = binding.Obtain(running.IBasicReactor)
    log      = binding.Obtain('logger:supervisor.busy-stats')
    busyCount = binding.Make(lambda self: events.Value(self._busy()) )
    supervisor = binding.Obtain('..')

    def monitorUsage(self):

        from time import time
        trace = self.log.trace
        maxChildren = self.supervisor.maxChildren

        busy = self.busyCount()

        while True:

            # wait until all children are started and busy
            while busy<len(self.children) or len(self.children)<maxChildren:
                yield self.busyCount; busy = events.resume()

            start = time()  # then begin timing

            # Time while N or N-1 children are busy
            while busy and busy>=len(self.children)-1 and len(self.children)==maxChildren:
                yield self.busyCount; busy = events.resume()

            duration = time()-start
            trace("All children were busy for: %s seconds", duration)

    monitorUsage = binding.Make(
        events.threaded(monitorUsage), uponAssembly = True
    )


    def _busy(self):
        return len(filter(None,self.children.values()))


    def processStarted(self, proxy):
        proxy.addListener(self.statusChanged)
        self.children[proxy.pid] = proxy.isBusy
        self.busyCount.set(self._busy())


    def statusChanged(self, proxy):
        if not proxy.isRunning:
            if proxy.pid in self.children:
                del self.children[proxy.pid]
        else:
            self.children[proxy.pid] = proxy.isBusy
        self.busyCount.set(self._busy())


    def doRead(self):
        if self.busyCount()==len(self.children):
            self.supervisor.requestStart()


    __onStart = binding.Make(
        lambda self: self.reactor.addReader(self),
        uponAssembly = True
    )


















from peak.api import *
from interfaces import *
import os
from weakref import WeakValueDictionary, ref
from commands import EventDriven

try:
    import signal

except ImportError:
    SIG_DFL = None
    signals = {}
    signal_names = {}
    signal = lambda *args: None

else:
    SIG_DFL = signal.SIG_DFL

    signals = dict(
        [(name,number)
            for (name,number) in signal.__dict__.items()
                if name.startswith('SIG') and not name.startswith('SIG_')
        ]
    )

    signal_names = dict(
        [(signum,signame) for signame,signum in signals.items()]
    )

    signal = signal.signal











class SignalManager(binding.Singleton):

    """Global signal manager"""

    protocols.advise(
        classProvides = [ISignalManager]
    )

    signal_handlers = dict(
        [(num,WeakValueDictionary()) for (name,num) in signals.items()]
    )

    all_handlers = {}

    def addHandler(self, handler):
        hid = id(handler)
        for signame, signum in signals.items():
            if hasattr(handler,signame):
                self.signal_handlers[signum][hid] = handler
                signal(signum, self._handle)
        self.all_handlers[hid] = ref(handler, lambda ref: self._purge(hid))

    def removeHandler(self, handler):
        self._purge(id(handler))

    def _purge(self, hid):
        if hid in self.all_handlers:
            del self.all_handlers[hid]
        for signum, handlers in self.signal_handlers.items():
            if hid in handlers:
                del handlers[hid]
            if not handlers:
                signal(signum, SIG_DFL)

    def _handle(self, signum, frame):
        signame = signal_names[signum]
        for hid, handler in self.signal_handlers[signum].items():
            getattr(handler,signame)(signum, frame)

    def __call__(self,*args): return self

class ChildProcess(binding.Component):

    protocols.advise(
        instancesProvide = [IProcessProxy]
    )

    isStopped  = False
    isFinished = False
    isRunning  = True

    exitStatus     = None
    stoppedBecause = None
    exitedBecause  = None

    listeners     = binding.Make(list)
    signalManager = binding.Obtain(ISignalManager)

    import os

    __onStart = binding.Make(
        lambda self: self.signalManager.addHandler(self),
        uponAssembly = True
    )

    def SIGCHLD(self, signum, frame):
        self.checkStatus()


    def sendSignal(self, signal):

        if signal in signals:
            # convert signal name to numeric signal
            signal = signals[signal]

        elif signal not in signal_names:
            raise ValueError,"Unsupported signal", signal

        self.os.kill(self.pid, signal)



    def checkStatus(self):
        # Check for process exited
        p, s = self.os.waitpid(self.pid, self.os.WNOHANG)
        if p==self.pid:
            self._setStatus(s)
            self._notify()

    def _setStatus(self,status):

        self.exitStatus = None
        self.exitedBecause = None
        self.stoppedBecause = None

        self.isStopped = self.os.WIFSTOPPED(status)

        if self.os.WIFEXITED(status):
            self.exitStatus = self.os.WEXITSTATUS(status)

        if self.isStopped:
            self.stoppedBecause = self.os.WSTOPSIG(status)

        if self.os.WIFSIGNALED(status):
            self.exitedBecause = self.os.WTERMSIG(stauts)

        self.isFinished = (
            self.exitedBecause is not None or self.exitStatus is not None
        )
        if self.isFinished:
            self.signalmanager.removeHandler(self)

        self.isRunning = not self.isFinished and not self.isStopped

    def _notify(self):
        # Notify listeners of status change
        for listener in self.listeners:
            listener(self)

    def addListener(self,func):
        self.listeners.append(func)


class ProcessSupervisor(EventDriven):

    # log         = logger (to where?)

    pidFile       = binding.Require("Filename where process ID is kept")
    minChildren   = 1
    maxChildren   = 4
    startInterval = 15      # seconds between forks

    template = binding.Require(
        "IProcessTemplate for child processes", adaptTo=IProcessTemplate,
        offerAs=[IProcessTemplate], suggestParent=False
    )

    startLockURL = binding.Make(
        lambda self: "flockfile:%s.start" % self.pidFile
    )

    pidLockURL = binding.Make(
        lambda self: "flockfile:%s.lock" % self.pidFile
    )

    startLock = binding.Make(
        lambda self: self.lookupComponent(self.startLockURL),
        adaptTo = ILock
    )

    pidLock = binding.Make(
        lambda self: self.lookupComponent(self.pidLockURL),
        adaptTo = ILock
    )

    lastStart = None    # last time a fork occurred
    nextStart = None    # next scheduled fork

    processes = binding.Make(dict)
    plugins   = binding.Make(list)




    reactor = binding.Make(
        'peak.running.scheduler:UntwistedReactor', offerAs=[IBasicReactor]
    )

    taskQueue = binding.Make(
        'peak.running.daemons.TaskQueue', offerAs=[ITaskQueue]
    )

    _no_twisted = binding.Require(
        "ProcessSupervisor subcomponents may not depend on Twisted",
        offerAs = [ITwistedReactor]
    )

    import os

    from time import time

























    def _run(self):

        if not self.startLock.attempt():
            # self.log.warn("Another process is starting")
            return 1        # exit with errorlevel 1

        try:
            self.template   # ensure template is ready first
            self.killPredecessor()
            self.writePidFile()
        finally:
            self.startLock.release()

        self.requestStart()

        retcode = super(ProcessSupervisor,self)._run()

        if adapt(retcode,IExecutable,None) is not None:
            # child process, drop out to the trampoline
            return retcode

        self.killProcesses()
        self.removePidFile()

        return retcode


    def requestStart(self):

        if self.nextStart is None:

            if self.lastStart is None:
                self.nextStart = self.time()
            else:
                self.nextStart = max(
                    self.lastStart + self.startInterval, self.time()
                )

            self.reactor.callLater(self.nextStart-self.time(), self._doStart)


    def _doStart(self):

        if len(self.processes)>=self.maxChildren:
            return

        self.lastStart = self.time()
        self.nextStart = None

        proxy, stub = self.template.spawn(self)
        if proxy is None:
            self.mainLoop.childForked(stub)
            return

        # XXX log started
        proxy.addListener(self._childChange)
        self.processes[proxy.pid] = proxy

        for plugin in self.plugins:
            plugin.processStarted(proxy)

        if len(self.processes)<self.minChildren:
            self.requestStart()


    def _childChange(self,proxy):
        if proxy.isFinished:
            # XXX log exited
            del self.processes[proxy.pid]


    def killProcesses(self):
        for pid,proxy in self.processes.items():
            proxy.sendSignal('SIGTERM')








    def writePidFile(self):
        self.pidLock.obtain()
        try:
            pf = open(self.pidFile,'w')
            pf.write('%d\n', self.os.getpid())
            pf.close()
        finally:
            self.pidLock.release()


    def readPidFile(self, func):
        self.pidLock.obtain()
        try:
            if self.os.path.exists(self.pidFile):
                pf = open(self.pidFile,'r')
                func(int(pf.readline().strip()))
                pf.close()
        finally:
            self.pidLock.release()


    def removePidFile(self):

        def removeIfMe(pid):
            if pid==self.os.getpid():
                self.os.unlink(self.pidFile)

        self.readPidFile(removeIfMe)


    def killPredecessor(self):

        def doKill(pid):
            try:
                self.os.kill(pid,signals['SIGTERM'])
            except:
                pass # XXX

        self.readPidFile(doKill)


class BusyProxy(ChildProcess):

    """Proxy for process that communicates its "busy" status"""

    reactor    = binding.Obtain(IBasicReactor)
    busyStream = binding.Require("readable pipe from child")
    fileno     = binding.Obtain('busyStream/fileno')
    isBusy     = False


    def doRead(self):
        byte = self.busyStream.read()[-1]
        if byte=='+':
            self.isBusy = True
            self._notify()
        elif byte=='-':
            self.isBusy = False
            self._notify()
        else:
            return


    def _setStatus(status):
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
    template = binding.Obtain(IProcessTemplate, suggestParent=False)
    stream   = binding.Obtain('./template/stdin')
    fileno   = binding.Obtain('./stream/fileno')
    reactor  = binding.Obtain(IBasicReactor)

    supervisor = binding.Obtain('..')

    def processStarted(self, proxy):
        proxy.addListener(self.statusChanged)
        self.children[proxy.pid] = proxy.isBusy
        self._delBinding('allBusy')

    def statusChanged(self, proxy):
        if not proxy.isRunning:
            if proxy.pid in self.allChildren:
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


class AbstractProcessTemplate(binding.Component):

    protocols.advise(
        instancesProvide = [IProcessTemplate],
        asAdapterForProtocols = [IExecutable],
        factoryMethod = 'templateForCommand'
    )

    import os

    proxyClass = ChildProcess   # default factory for proxy
    readPipes  = ()             # sequence of attribute names for p<-c pipes
    writePipes = ()             # sequence of attribute names for p->c pipes

    def spawn(self, parentComponent):

        parentPipes, childPipes = {}, {}

        for name in self.readPipes:
            parentPipes[name], childPipes[name] = self._mkPipe()
        for name in self.writePipes:
            childPipes[name], parentPipes[name] = self._mkPipe()

        pid = self.os.fork()

        if pid:
            # Parent process
            [f.close() for f in childPipes.values()]
            del childPipes
            return self._makeProxy(parentComponent,pid,parentPipes), None

        else:
            # Child process
            [f.close() for f in parentPipes.values()]
            del parentPipes
            self.__dict__.update(childPipes)    # set named attrs w/pipes
            return None, self._redirectWrapper(self._makeStub())




    def _mkPipe(self):
        r,w = self.os.pipe()
        return self.os.fdopen(r,'r',0), self.os.fdopen(w,'w',0)


    def _makeProxy(self,parentComponent,pid,pipes):

        proxy = self.proxyClass(pid=pid)

        for name, stream in pipes.items():
            setattr(proxy, name, stream)

        # Set parent component *after* the pipes are set up, in case
        # the proxy has assembly events that make use of the pipes.
        proxy.setParentComponent(parentComponent)


    def _redirect(self):
        pass


    def _redirectWrapper(self, cmd):
        """Wrap 'cmd' so that it's run after doing our redirects"""

        def runner():
            self._redirect()
            return cmd

        return runner












    def _makeStub(self):
        return self.command


    command = binding.Require(
        "Command to run in subprocess", suggestParent=False
    )


    def templateForCommand(klass, ob, proto):
        return klass(ob, command = ob)

    templateForCommand = classmethod(templateForCommand)





























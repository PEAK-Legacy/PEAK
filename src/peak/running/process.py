from peak.api import *
from interfaces import *
from weakref import WeakValueDictionary, ref


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

    pid        = None
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
        return proxy


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





























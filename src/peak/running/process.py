from peak.api import *
from interfaces import *
import os
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

class ProcessManager(binding.Component):

    processes     = binding.Make(dict)
    signalManager = binding.Obtain(ISignalManager)

    fork    = binding.Obtain('import:os.fork')
    waitpid = binding.Obtain('import:os.waitpid')
    WNOHANG = binding.Obtain('import:os.WNOHANG')

    def invoke(self,cmd):

        factory = adapt(cmd,IProcessFactory)
        pid     = self.fork()

        if pid:
            # Parent process
            proxy = factory.makeProxy(self, pid)
            self.processes[pid] = proxy
            self.signalManager.addHandler(self)
            return proxy
        else:
            # Child process
            sys.exit( factory.runChild() )


    def SIGCHLD(self, signum, frame):
        self.reap()


    def reap(self):
        """Scan for terminated child processes"""
        for pid, proxy in self.processes.items():
            p, s = self.waitpid(pid, self.WNOHANG)
            if p==pid:
                proxy.setStatus(s)
                if proxy.isFinished:
                    del self.processes[pid]





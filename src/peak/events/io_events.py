from peak.core import protocols, adapt, binding, NOT_GIVEN
from interfaces import *
from peak.util.EigenData import AlreadyRead
from weakref import WeakValueDictionary, ref
import sources

try:
    import signal

except ImportError:
    SIG_DFL = None
    signals = {}
    signal_names = {}
    signal = lambda *args: None
    original_signal_handlers = {}

else:
    SIG_DFL = signal.SIG_DFL

    signals = dict(
        [(name,number)
            for (name,number) in signal.__dict__.items()
                if name.startswith('SIG') and not name.startswith('SIG_')
        ]
    )

    signal_names = {}
    for signame,signum in signals.items():
        signal_names.setdefault(signum,[]).append(signame)

    original_signal_handlers = dict(
        [(signum,signal.getsignal(signum)) for signum in signal_names.keys()]
    )

    signal = signal.signal






class SignalEvents(binding.Singleton):

    """Global signal manager"""

    protocols.advise( classProvides = [ISignalSource] )

    _events = {}

    def signals(self,*signames):
        """'IEventSource' that triggers whenever any of named signals occur"""

        if len(signames)==1:
            signum = signals[signames[0]]
            try:
                return self._events[signum]()
            except KeyError:
                e = sources.Broadcaster()
                self._events[signum] = ref(
                    e, lambda ref: self._rmSignal(signum)
                )
                signal(signum, self._fire)
                return e
        else:
            return sources.AnyOf(*[self.signals(n) for n in signames])


    def haveSignal(self,signame):
        """Return true if signal named 'signame' exists"""
        return signame in signals

    def _fire(self, signum, frame):
        if signum in self._events:
            self._events[signum]().send((signum,frame))

    def __call__(self,*args):
        return self

    def _rmSignal(self,signum):
        del self._events[signum]
        signal(signum, original_signal_handlers[signum])


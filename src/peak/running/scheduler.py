"""Event-driven Scheduling"""

from peak.api import *
from interfaces import *
from time import time, sleep
from peak.util.EigenData import EigenCell, AlreadyRead
from peak.util.imports import lazyModule
select = lazyModule('select')

from bisect import insort_right


__all__ = [
    'setReactor', 'getReactor', 'getTwisted',
    'MainLoop', 'UntwistedReactor',
]

























class MainLoop(binding.Base):

    """Top-level application event loop, with timeout management"""

    __implements__ = IMainLoop


    reactor      = binding.bindTo(IBasicReactor)

    lastActivity = None


    def activityOccurred(self):
        self.lastActivity = time()


    def run(self, stopAfter=0, idleTimeout=0, runAtLeast=0):

        """Loop polling for IO or GUI events and calling scheduled funcs"""

        self.lastActivity = time()

        reactor = self.reactor
        
        try:
            if stopAfter:
                reactor.callLater(stopAfter, reactor.stop)

            if idleTimeout:
                reactor.callLater(runAtLeast, self._checkIdle, idleTimeout)

            reactor.run()

        finally:
            del self.lastActivity






    def _checkIdle(self, timeout):

        # Check whether we've been idle long enough to stop
        idle = time() - self.lastActivity
        
        if idle >= timeout:
            self.reactor.stop()

        else:
            # reschedule check for the earliest point at which
            # we could have been idle for the requisite amount of time
            self.reactor.callLater(timeout - idle, self._checkIdle, timeout)





























_reactor = EigenCell()
_twisted = False

def setReactor(reactor):
    """Set the system reactor to 'reactor', if not already used"""
    _reactor.set(reactor)


def getReactor(appConfig):
    """Get system reactor -- default to our "dirt simple" reactor"""

    if not hasattr(_reactor,'value'):   # XXX ugh
        setReactor(UntwistedReactor(appConfig))

    return _reactor.get()


def getTwisted(appConfig):

    """Get system reactor -- but only if it's twisted!"""

    if not _twisted:

        if _reactor.locked:
            # I guess we're just not twisted enough!
            raise AlreadyRead("Another reactor is already in use")

        try:
            from twisted.internet import reactor
        except ImportError:
            raise exceptions.PropertyNotFound(
                """twisted.internet.reactor could not be imported"""
            )
        
        _reactor.set(reactor)
        # XXX do twisted setups like threadable.init, wxSupport.install, etc.
        _twisted = True

    return _reactor.get()


class UntwistedReactor(binding.Base):

    """Primitive partial replacement for 'twisted.internet.reactor'"""

    __implements__ = IBasicReactor

    running = False
    writers = binding.New(list)
    readers = binding.New(list)
    laters  = binding.New(list)

    def run(self):

        self.running = True

        while self.running:
            self.iterate()

        # clear selectables
        self._delBinding('readers')
        self._delBinding('writers')


    def stop(self):
        self.running = False

    def callLater(self, delay, callable, *args, **kw):
        insort_right(self.laters, _Appt(time()+delay, callable, args, kw))

    def addReader(self, reader):
        if reader not in self.readers: self.readers.append(reader)
        
    def addWriter(self, writer):
        if writer not in self.writers: self.writers.append(writer)

    def removeReader(self, reader):
        if reader in self.readers: self.readers.remove(reader)

    def removeWriter(self, writer):
        if writer in self.writers: self.writers.remove(writer)

    def iterate(self, delay=None):

        now = time()

        while self.laters and self.laters[0].time <= now:
            try:
                self.laters.pop(0)()
            except:
                LOG_ERROR(
                    "Error executing scheduled callback", self, exc_info=True
                )

        if delay is None:
            delay = self.laters and self.laters[0].time - time() or 0

        delay = max(delay, 0)

        if self.readers or self.writers:

            r, w, e = select.select(self.readers, self.writers, [], delay)

            for reader in r: r.doRead()
            for writer in w: w.doWrite()

        elif delay:
            sleep(delay)


class _Appt(object):

    """Simple "Appointment" for doing 'callLater()' invocations"""

    __slots__ = 'time','func','args','kw'

    def __init__(self,t,f,a,k):
        self.time = t; self.func = f; self.args = a; self.kw = k

    def __call__(self): return self.func(*self.args, **self.kw)
    def __cmp__(self):  return cmp(self.time, other.time)




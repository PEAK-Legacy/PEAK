"""Event-driven Scheduling"""

from peak.api import *
from interfaces import *
from peak.util.EigenData import EigenCell, AlreadyRead

from bisect import insort_right


__all__ = [
    'setReactor', 'getReactor', 'getTwisted',
    'MainLoop', 'UntwistedReactor',
]




























class MainLoop(binding.Component):

    """Top-level application event loop, with timeout management"""

    implements(IMainLoop)

    reactor      = binding.bindTo(IBasicReactor)
    time         = binding.bindTo('import:time.time')

    lastActivity = None

    def activityOccurred(self):
        self.lastActivity = self.time()


    def run(self, stopAfter=0, idleTimeout=0, runAtLeast=0):

        """Loop polling for IO or GUI events and calling scheduled funcs"""

        self.lastActivity = self.time()

        reactor = self.reactor

        try:
            if stopAfter:
                reactor.callLater(stopAfter, reactor.stop)

            if idleTimeout:
                reactor.callLater(runAtLeast, self._checkIdle, idleTimeout)

            reactor.run()

        finally:
            del self.lastActivity


        # XXX we should probably log start/stop events




    def _checkIdle(self, timeout):

        # Check whether we've been idle long enough to stop
        idle = self.time() - self.lastActivity

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
    return _reactor.get(lambda: UntwistedReactor(appConfig))

def getTwisted(appConfig):

    """Get system reactor -- but only if it's twisted!"""

    global _twisted

    if _twisted:
        return _reactor.get()

    try:
        from twisted.internet import reactor
    except ImportError:
        raise exceptions.PropertyNotFound(
            """twisted.internet.reactor could not be imported"""
        )

    def _getTwisted():
        # XXX do twisted setups like threadable.init, wxSupport.install, etc.
        return reactor

    peak_reactor = _reactor.get(_getTwisted)

    if peak_reactor is not reactor:
        # I guess we're just not twisted enough!
        raise AlreadyRead("Another reactor is already in use")

    _twisted = True
    return peak_reactor


class UntwistedReactor(binding.Component):

    """Primitive partial replacement for 'twisted.internet.reactor'"""

    implements(IBasicReactor)

    running = False
    writers = binding.New(list)
    readers = binding.New(list)
    laters  = binding.New(list)
    time    = binding.bindTo('import:time.time')
    sleep   = binding.bindTo('import:time.sleep')
    select  = binding.bindTo('import:select.select')

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
        insort_right(self.laters, _Appt(self.time()+delay, callable, args, kw))

    def addReader(self, reader):
        if reader not in self.readers: self.readers.append(reader)

    def addWriter(self, writer):
        if writer not in self.writers: self.writers.append(writer)

    def removeReader(self, reader):
        if reader in self.readers: self.readers.remove(reader)

    def removeWriter(self, writer):
        if writer in self.writers: self.writers.remove(writer)

    logger = binding.bindToProperty('peak.logs.reactor')

    def iterate(self, delay=None):

        now = self.time()

        while self.laters and self.laters[0].time <= now:
            try:
                self.laters.pop(0)()
            except:
                self.logger.exception(
                    "%s: error executing scheduled callback:", self
                )

        if delay is None:
            delay = self.laters and self.laters[0].time - self.time() or 0

        delay = max(delay, 0)

        if not self.running:
            delay = 0

        if self.readers or self.writers:

            r, w, e = self.select(self.readers, self.writers, [], delay)

            for reader in r: reader.doRead()
            for writer in w: writer.doWrite()

        elif delay:
            self.sleep(delay)










class _Appt(object):

    """Simple "Appointment" for doing 'callLater()' invocations"""

    __slots__ = 'time','func','args','kw'

    def __init__(self,t,f,a,k):
        self.time = t; self.func = f; self.args = a; self.kw = k

    def __call__(self):
        return self.func(*self.args, **self.kw)

    def __cmp__(self, other):
        return cmp(self.time, other.time)




























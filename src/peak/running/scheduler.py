"""Event-driven Scheduling"""

from peak.api import *
from interfaces import *
from peak.util.EigenData import EigenCell, AlreadyRead
from errno import EINTR

__all__ = [
    'setReactor', 'getReactor', 'getTwisted',
    'MainLoop', 'UntwistedReactor', 'StopOnStandardSignals'
]

class StopOnStandardSignals(binding.Component):

    # We hook up to the reactor as soon as possible (i.e. activate upon
    # assembly), to avoid having to do the lookup during signal handling.

    reactor = binding.Obtain(IBasicReactor, activateUponAssembly=True)

    def SIGINT(self, num, frame):
        self.reactor.stop()

    SIGTERM = SIGBREAK = SIGINT


class ReactorCrash(Exception):
    """Signal that the reactor needs to crash/exit NOW"""














class MainLoop(binding.Component):
    """Top-level application event loop, with timeout management"""

    protocols.advise(
        instancesProvide=[IMainLoop]
    )
    exitCode      = 0
    reactor       = binding.Obtain(IBasicReactor)
    time          = binding.Obtain('import:time.time')
    lastActivity  = None
    signalManager = binding.Obtain(ISignalManager)
    signalHandler = binding.Obtain(
        PropertyName('peak.running.mainLoop.signalHandler')
    )

    def activityOccurred(self):
        self.lastActivity = self.time()

    def run(self, stopAfter=0, idleTimeout=0, runAtLeast=0):
        """Loop polling for IO or GUI events and calling scheduled funcs"""

        self.lastActivity = self.time()
        self.signalManager.addHandler(self.signalHandler)
        self.exitCode = 0

        try:
            if stopAfter:
                self.reactor.callLater(stopAfter, self.reactor.stop)

            if idleTimeout:
                self.reactor.callLater(runAtLeast,self._checkIdle,idleTimeout)

            self.reactor.run(False)
            return self.exitCode

        finally:
            del self.lastActivity
            self.signalManager.removeHandler(self.signalHandler)

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


    def setExitCode(self, exitCode):
        self.exitCode = exitCode


    def childForked(self, stub):
        self.setExitCode(stub)
        self.reactor.crash()




















_reactor = EigenCell()
_twisted = False

def setReactor(reactor):
    """Set the system reactor to 'reactor', if not already used"""
    _reactor.set(reactor)

def getReactor():
    """Get system reactor -- default to our "dirt simple" reactor"""
    return _reactor.get(lambda: UntwistedReactor())

def getTwisted():

    """Get system reactor -- but only if it's twisted!"""

    global _twisted

    if _twisted:
        return _reactor.get()

    try:
        from twisted.internet import reactor
    except ImportError:
        raise exceptions.NameNotFound(
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


class TwistedScheduler(binding.Component,events.Scheduler):

    """'events.IScheduler' that uses a Twisted reactor for timing"""

    reactor = binding.Obtain(ITwistedReactor)
    now     = binding.Obtain('import:time.time')

    def time_available(self):
        return 0    # no way to find this out from a reactor :(

    def tick(self):
        self.reactor.runUntilCurrent()

    def _callAt(self, what, when):
        self.reactor.callLater(when-self.now(), what, self, when)


























class UntwistedReactor(binding.Component):

    """Primitive partial replacement for 'twisted.internet.reactor'"""

    protocols.advise(
        instancesProvide=[IBasicReactor]
    )

    running = False
    writers = binding.Make(list)
    readers = binding.Make(list)
    sleep   = binding.Obtain('import:time.sleep')
    select  = binding.Obtain('import:select.select')
    _error  = binding.Obtain('import:select.error')
    logger  = binding.Obtain('logger:peak.reactor')
    sigMgr  = binding.Obtain(ISignalManager)
    scheduler = binding.Obtain(events.IScheduler)

    checkInterval = binding.Obtain(
        PropertyName('peak.running.reactor.checkInterval')
    )

    def callLater(self, delay, callable, *args, **kw):
        self.scheduler.sleep(delay).addCallback(
            lambda s,e: callable(*args,**kw) or True
        )

    def addReader(self, reader):
        if reader not in self.readers: self.readers.append(reader)

    def addWriter(self, writer):
        if writer not in self.writers: self.writers.append(writer)

    def removeReader(self, reader):
        if reader in self.readers: self.readers.remove(reader)

    def removeWriter(self, writer):
        if writer in self.writers: self.writers.remove(writer)



    def run(self, installSignalHandlers=True):

        if installSignalHandlers:
            self.sigMgr.addHandler(self)

        try:
            self.running = True
            log = self.logger

            while self.running:
                try:
                    self.iterate()
                except:
                    log.exception("Unexpected error in reactor.run():")

        finally:
            self.running = False

            if installSignalHandlers:
                self.sigMgr.removeHandler(self)

            # clear selectables (XXX why???)
            self._delBinding('readers')
            self._delBinding('writers')


    def stop(self):
        self.callLater(0, self.crash)

    def crash(self):
        self.running = False
        raise ReactorCrash

    def SIGINT(self, num, frame):
        self.stop()

    SIGTERM = SIGBREAK = SIGINT




    def iterate(self, delay=None):

        wasRunning = self.running

        try:
            self.scheduler.tick()
        except ReactorCrash:
            return
        except:
            self.logger.exception(
                "%s: error executing scheduled callback:", self
            )

        if delay is None:
            if not self.running:
                delay = 0
            else:
                delay = self.scheduler.time_available()
                if delay is None:
                    delay = self.checkInterval

        delay = max(delay, 0)

        if (self.readers or self.writers) and (self.running or not wasRunning):
            try:
                r, w, e = self.select(self.readers, self.writers, [], delay)
            except self._error,v:
                if v.args[0]==EINTR:    # signal received during select
                    return
                raise

            for reader in r: reader.doRead()
            for writer in w: writer.doWrite()

        elif delay and self.running:
            self.sleep(delay)






from __future__ import generators
from peak.api import *
from interfaces import *
import io_events
from twisted.internet import defer
from twisted.python import failure


def getTwisted():

    """Get Twisted reactor, or die trying"""

    try:
        from twisted.internet import reactor
    except ImportError:
        raise exceptions.NameNotFound(
            """twisted.internet.reactor could not be imported"""
        )
    else:
        return reactor

Reactor = getTwisted  # for easy reference in peak.ini



















class DeferredAsEventSource(protocols.Adapter):

    protocols.advise(
        instancesProvide=[ITaskSwitch],
        asAdapterForTypes=[defer.Deferred],
    )

    def nextAction(self, thread=None, state=None):

        if state is not None:

            def handler():
                v = events.resume()
                if isinstance(v,failure.Failure):
                    raise v
                else:
                    yield v

            state.CALL(handler())
                
            if self.subject.called:
                state.YIELD(self.subject.result)
            else:
                cb = lambda v: (thread.step(self,v),v)[1]
                self.subject.addCallbacks(cb,cb)

        return self.subject.called
            













class Scheduler(binding.Component,events.Scheduler):

    """'events.IScheduler' that uses a Twisted reactor for timing"""

    reactor = binding.Obtain(running.ITwistedReactor)
    now     = binding.Obtain('import:time.time')

    def time_available(self):
        return 0    # no way to find this out from a reactor :(

    def tick(self,stop=False):
        self.reactor.iterate()

    def _callAt(self, what, when):
        self.isEmpty.set(False)
        self.reactor.callLater(when-self.now(), what, self, when)

























class EventLoop(io_events.EventLoop):

    """Implement an event loop using reactor.run()"""

    reactor = binding.Obtain(running.ITwistedReactor)

    def runUntil(self, eventSource, suppressErrors=False, idle=None):

        if not suppressErrors:
            raise NotImplementedError(
                "Twisted reactors always suppress errors"
            )

        exit = []   # holder for exit event

        # When event fires, record it for our return
        adapt(eventSource,IEventSource).addCallback(
            lambda s,e: [exit.append(e), self.reactor.crash()]
        )

        self.reactor.run()

        if exit:
            return exit.pop()
        else:
            raise StopIteration("Unexpected reactor exit")















class TwistedReadEvent(events.Broadcaster):

    __slots__ = '_add','_remove','_registered','fd'

    def __init__(self,reactor,fileno):
        self.fd = fileno
        self._add = reactor.addReader
        self._remove = reactor.removeReader
        self._registered = False
        super(TwistedReadEvent,self).__init__()

    def _register(self):
        if self._callbacks and not self._registered:
            self._add(self); self._registered = True

        elif self._registered:
            self._remove(self); self._registered = False

    def _fire(self,event):
        try:
            super(TwistedReadEvent,self)._fire(event)
        finally:
            self._register()

    def addCallback(self,func):
        super(TwistedReadEvent,self).addCallback(func)
        self._register()

    def fileno(self):
        return fd

    def doRead(self):
        self._fire(True)








class TwistedWriteEvent(TwistedReadEvent):

    __slots__ = ()

    def __init__(self,reactor,fileno):
        super(TwistedWriteEvent,self).__init__(reactor,fileno)
        self._add = reactor.addWriter
        self._remove = reactor.removeWriter

    def doWrite(self):
        self._fire(True)


class Selector(io_events.Selector):

    """Implement ISelector using a reactor"""

    reactor = binding.Obtain(running.ITwistedReactor)
    monitor = None  # don't run a monitoring thread!

    def _mkEvent(self,rwe,key):
        if rwe==2:
            return sources.Broadcaster()    # XXX reactor doesn't allow this
        else:
            return [TwistedReadEvent, TwistedWriteEvent][rwe](self.reactor,key)

















from peak.api import *
from interfaces import *
from types import GeneratorType
from sys import exc_info
import traceback
from sources import State, Value, EventSource, OneShot

__all__ = ['resume', 'Clock', 'Thread']


no_exc = None, None, None

def resume():
    if exc_info()<>no_exc:
        try:
            t,v,tb = sys.exc_info()
            raise t,v,tb
        finally:
            t=v=tb=None


class GeneratorAsTaskSwitch(protocols.Adapter):

    protocols.advise(
        instancesProvide=[ITaskSwitch],
        asAdapterForTypes=[GeneratorType]
    )

    def shouldSuspend(self,thread):
        thread.call(self.subject)
        return False










class Clock(binding.Component):

    protocols.advise(
        instancesProvide=[IClock]
    )

    now      = binding.Make(lambda: Value(None))
    stopping = binding.Make(EventSource)
    starting = binding.Make(EventSource)

    log = binding.Obtain('logger:events.clock')
    _time = binding.Make('time.time')
    _appointments = binding.Make(list)
    _stopped = False

    def run(self):

        self._stopped = False
        self.starting.fire()

        while self._appointments:
            self.tick()

        if not self._stopped:
            self.stop()
            self.tick()

    def stop(self):
        self.stopping.fire()
        self.schedule(self.crash)

    def crash(self):
        self._appointments = ()
        self._stopped = True

    def idleFor(self):
        if self._appointments:
            return max(0, self._appointments[0].time - self.now())



    def tick(self):
        now = self._time()
        self.now.set(now)

        while self._appointments and self._appointments[0].time <= now:
            try:
                self._appointments.pop(0)[1]()
            except:
                self.log.exception(
                    "Unexpected error executing callback:"
                )


    def schedule(self, what, delay=0):
        self._callAt(what, self._time()+delay)


    def _callAt(self, what, when):
        if self._stopped:
            self.log.warn(
                "Ignoring attempt to schedule %r after clock stopped",
                (what, when)
            )
            return

        appts = self._appointments
        lo = 0
        hi = len(appts)

        while lo < hi:
            mid = (lo+hi)//2
            if when < appts[mid][0]:
                hi = mid
            else:
                lo = mid+1

        appts.insert(lo, (when,what))




    appThreads = 0


    def spawn(iterator, background=True):
        thread = Thread(self)
        thread.schedule(iterator)
        thread.enable()
        if not background:
            self.appThreads += 1
            thread.isFinished.addSubscriber(
                self._appThreadDied()
            )
        return thread


    def _appThreadDied(self):
        self.appThreads -= 1
        if self.appThreads <=0 and not self._stopped:
            self.stop()


    def sleep(self, secs=0):
        """Get 'IEventSource' that fires 'secs' from now"""
        es = OneShot()
        self._callAt(es.fire, self._time()+secs)
        return es


    def until(self,time):
        """Get 'IEventSource' that fires when 'clock.now() >= time'"""
        es = OneShot()
        self._callAt(es.fire, max(time,self._time()))
        return es








class Thread(object):

    __slots__ = 'isFinished', '_clock', '_stack', '_inIterator'

    protocols.advise(
        instancesProvide=[IThread]
    )

    def __init__(self,clock):
        self.isFinished = State(False)
        self._clock = clock
        self._stack = []
        self._inIterator  = False


    def enable(self):
        self._clock.schedule(self.step)


    def call(self,iterator):
        if self._inIterator:
            # The right way to run code from inside a thread is
            # to yield the iterator; don't call back into 'call()'!
            raise "AlreadyRunning"  # XXX
        else:
            self._stack.append(iterator)















    def step(self):

        stack = self._stack

        while stack:
            try:
                self._inIterator = True
                try:
                    for switch in stack[-1]:
                        break
                    else:
                        stack.pop() # No switch; topmost iterator is finished!
                        continue    # resume the next iterator down, or exit
                finally:
                    self._inIterator = False
            except:
                # Remove the current iterator, since it can't be resumed
                stack.pop()

                if stack:
                    continue    # delegate the error to the next iterator
                else:
                    # nobody to delegate to, pass the buck to our caller
                    self._clock.schedule(
                        # But first, ensure that we'll be logged as finishing
                        lambda: self.isFinished.set(True)
                    )
                    try:
                        raise
                    except SystemExit,v:
                        return  # thread's over, just exit

            # Perform the task switch
            try:
                if adapt(switch,ITaskSwitch).shouldSuspend(self):
                    return  # suspend execution
            except:
                continue    # push the error back into the current iterator

        self.isFinished.set(True)


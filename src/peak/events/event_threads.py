from __future__ import generators
from peak.core import protocols, adapt, NOT_GIVEN
from interfaces import *
from types import GeneratorType
from sys import exc_info, _getframe
import traceback
from sources import Condition, Value, AnyOf
import time
from peak.util.advice import advice

__all__ = [
    'resume', 'threaded', 'Scheduler', 'Thread', 'ThreadState', 'Interrupt',
]

def resume():
    """Call this after every task/task switch 'yield' in a thread

    This function returns the event that caused the thread to resume, or
    reraises any exceptions thrown by a nested generator in the thread.  It
    should be called after every 'yield' statement in a thread, if the
    statement yields a generator or an 'ITaskSwitch' or 'IEventSource'.
    (If the statement simply yields a value to its calling generator, it need
    not be followed by an 'events.resume()' call.)

    Note that you should still call this function even if you don't need its
    return value.  Otherwise, errors from other generators will be silently
    lost."""

    state = _getframe(2).f_locals['state']

    if state.handlingError:
        try:
            t,v,tb = exc_info()
            raise t,v,tb
        finally:
            t=v=tb=None

    # No exception, try to pass event data back into the frame
    return state.lastEvent


class threaded(advice):

    """Wrap a generator function to return a 'Thread'

    Usage::

        def someMethod(self, whatever):
            yield whatever; events.resume()
            # ...

        someMethod = events.threaded(someMethod)

    When called, 'ob.someMethod(whatever)' will return an 'events.Thread' that
    executes 'someMethod'.  Note that this may also be used in conjunction with
    'binding.Make', e.g.::

        def aThread(self):
            yield self.something; events.resume()
            # ...

        aThread = binding.Make( events.threaded(aThread) )

    In this case, 'ob.aThread' will be an 'events.Thread' that runs the
    'aThread' method.  This is often convenient to use with 'uponAssembly=True',
    so that the thread is started as soon as the component is assembled."""

    def __call__(self,*__args,**__kw):
        return Thread(self._func(*__args,**__kw))













class Interrupt(object):

    """Interrupt a thread with an error if specified event occurs

    Usage::

        try:
            yield events.Interrupt( stream.readline(), scheduler.timeout(5) )
            line = events.resume()

        except events.Interruption:
            print "readline() took more than 5 seconds"

    An 'Interrupt' object is an 'events.ITaskSwitch', so you can only use it
    within a thread, and you cannot set callbacks on it.  If the supplied
    generator/iterator exits for any reason, the interruption is cancelled.

    Also note that because generator objects are not reusable, neither are
    'Interrupt' objects.  You must create an 'Interrupt' for each desired
    invocation of the applicable generator.  However, the called generator
    need not create an additional 'Interrupt' for any nested generator calls,
    even though multiple interrupts may be active at the same time.  This
    allows you to do things like e.g. set one timeout for each line of data
    being received, and another timeout for receiving an entire email.
    """

    __slots__ = 'iterator','source','errorType'

    protocols.advise(
        instancesProvide=[ITaskSwitch],
    )










    def __init__(self,iterator,eventSource,errorType=Interruption):

        """'Interrupt(iterator,eventSource,errorType=Interruption)'

        Wrap execution of 'iterator' so that it will raise 'errorType' if
        'eventSource' fires before 'iterator' exits (or aborts), assuming that
        the 'Interrupt' is yielded to a thread."""

        self.iterator = adapt(iterator,ITask)
        self.source  =  adapt(eventSource,IEventSource)
        self.errorType = errorType


    def nextAction(self,thread=None,state=None):

        if state is not None:

            cancelled = Condition(False)

            def canceller():
                yield self.iterator; cancelled.set(True); yield resume()

            def interrupt(source,event):
                if not cancelled():
                    state.CALL(doInterrupt()); thread.step(source,event)

            def doInterrupt():
                raise self.errorType(resume())
                yield None

            state.CALL(canceller()); self.source.addCallback(interrupt)

        return True








class TaskAsTaskSwitch(protocols.Adapter):

    protocols.advise(
        instancesProvide=[ITaskSwitch],
        asAdapterForProtocols=[ITask]
    )

    def nextAction(self,thread=None,state=None):
        if state is not None:
            state.CALL(self.subject)
        return True

protocols.declareImplementation(GeneratorType, [ITask])




























class Scheduler(object):

    """Time-based event sources; see 'events.IScheduler' for interface"""

    protocols.advise( instancesProvide=[IScheduler] )

    def __init__(self, time = time.time):
        self.now = time
        self._appointments = []
        self.isEmpty = Condition(True)

    def time_available(self):
        if self._appointments:
            return max(0, self._appointments[0][0] - self.now())


    def tick(self,stop=None):
        now = self.now()
        while self._appointments and self._appointments[0][0] <= now and not stop:
            self._appointments.pop(0)[1](self,now)
        self.isEmpty.set(not self._appointments)

    def sleep(self, secs=0):
        return _Sleeper(self,secs)

    def until(self,time):
        c = Condition()
        if time <= self.now():
            c.set(True)
        else:
            self._callAt(lambda s,e: c.set(True), time)
        return c

    def timeout(self,secs):
        return self.until(self.now()+secs)


    def spawn(self, iterator):
        return _SThread(iterator, self)


    def alarm(self, iterator, timeout, errorType=TimeoutError):
        return Interrupt(iterator, self.timeout(timeout), errorType)

    def _callAt(self, what, when):
        self.isEmpty.set(False)
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


class _Sleeper(object):

    protocols.advise(
        instancesProvide=[IEventSource]
    )

    def __init__(self,scheduler,delay):
        self.scheduler = scheduler
        self.delay = delay

    def nextAction(self,thread=None,state=None):
        if thread is not None:
            self.addCallback(thread.step)

    def addCallback(self,func):
        self.scheduler._callAt(
            lambda s,e: func(self,e), self.scheduler.now() + self.delay
        )




class ThreadState(object):

    """Tracks the state of a thread; see 'events.IThreadState' for details"""

    __slots__ = 'lastEvent', 'handlingError', 'stack'

    protocols.advise(
        instancesProvide=[IThreadState]
    )

    def __init__(self):
        self.lastEvent = NOT_GIVEN
        self.handlingError = False
        self.stack = []

    def CALL(self,iterator):
        self.stack.append( adapt(iterator,ITask) )

    def YIELD(self,value):
        self.lastEvent = value

    def RETURN(self):
        self.stack.pop()

    def THROW(self):
        self.handlingError = True
        self.lastEvent = NOT_GIVEN

    def CATCH(self):
        self.handlingError = False











class Thread(object):
    """Lightweight "thread" that responds to events, using generator/iterators

    Usage::

        def aGenerator(someArg):
            yield untilSomeCondition; events.resume()
            # ... do something ...

        events.Thread(aGenerator(someValue))    # create the thread

    When created, threads run until the first 'yield' operation yielding an
    'ITaskSwitch' results in the thread being suspended.  The thread will
    then be resumed when the waited-on event fires its callbacks, and so on.

    Threads offer an 'isFinished' 'ICondition' that can be waited on, or checked
    to find out whether the thread has successfully completed.  See
    'events.IThread' for more details."""

    __slots__ = 'isFinished', '_state'

    protocols.advise( instancesProvide=[IThread] )

    def __init__(self, iterator):
        self.isFinished = Condition()
        self._state = ThreadState()
        self._state.CALL(iterator)
        self._start()

    def _start(self):
        """Hook for subclasses to start the thread"""
        self.step()

    def _uncaughtError(self):
        """Hook for subclasses to catch exceptions that escape the thread"""
        try:
            raise
        except SystemExit,v:
            self.isFinished.set(True)
            return True

    def step(self, source=None, event=NOT_GIVEN):
        """See 'events.IThread.step'"""
        state = self._state; state.YIELD(event)

        while state.stack:
            switch = event = None   # avoid holding previous references
            try:
                for event in state.stack[-1]:
                    state.CATCH()
                    break
                else:
                    state.RETURN() # No switch; topmost iterator is finished!
                    state.CATCH()
                    continue    # resume the next iterator down, or exit
            except:
                # Remove the current iterator, since it can't be resumed
                state.RETURN()
                state.THROW()

                if state.stack:
                    continue    # delegate the error to the next iterator
                else:
                    # nobody to delegate to, pass the buck to our caller
                    return self._uncaughtError()

            # Perform the task switch, if any
            try:
                switch = adapt(event,ITaskSwitch,None)
                if switch is not None:
                    if not switch.nextAction(self,state):
                        state.YIELD(switch) # save reference until we resume
                        return True
                else:
                    state.YIELD(event)
            except:
                state.THROW()
                continue    # push the error back into the current iterator

        self.isFinished.set(True)
        return True

class _SThread(Thread):

    """'events.Thread' that handles errors better, by relying on a scheduler"""

    __slots__ = 'scheduler','aborted'

    protocols.advise( instancesProvide=[IScheduledThread] )

    def __init__(self, iterator, scheduler):
        self.scheduler = scheduler
        self.aborted = Condition()
        Thread.__init__(self,iterator)


    def _start(self):
        super(_SThread,self).step()


    def _uncaughtError(self):
        condition = self.aborted
        try:
            try:
                raise
            except SystemExit,v:
                condition = self.isFinished
                return True
        finally:
            self.scheduler._callAt(
                lambda e,s: condition.set(True), self.scheduler.now()
            )


    def step(self, source=None, event=NOT_GIVEN):
        """See 'events.IScheduledThread.step'"""
        self.scheduler._callAt(
            lambda e,s: super(_SThread,self).step(source,event),
            self.scheduler.now()
        )




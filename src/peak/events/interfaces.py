from peak.api import *

__all__ = [
    'ITaskSwitch', 'IEventSource', 'ISubscription', 'IValue', 'IState',
    'IQueue', 'IThread', 'IClock' , 'ISelector',
]

class ITaskSwitch(protocols.Interface):

    """What a thread yields control to

    Iterators running in a thread yield 'ITaskSwitch' objects to control the
    thread's flow and co-operation.

    In addition to PEAK-supplied classes like 'Readable', 'Writable', and
    'Sleep', generator-iterators are also adaptable to 'ITaskSwitch', thus
    allowing one to 'yield someGenerator(someArgs)' in a thread.  This allows
    the nested generator to run until it is completed or raises an error.
    """

    def shouldSuspend(thread):
        """Return true if 'thread' should be suspended

        Typically, this will be implemented as something like::

            def shouldSuspend(self, thread):
                self.addCallback(thread.enable)
                return True

        at least in cases where the scheduler is also an 'IEventSource'.

        This method is explicitly allowed to call the thread's 'schedule()'
        method, thus "interrupting" the currently running routine in that
        thread.  The 'ITaskSwitch' adapter for generators schedules the
        generator and returns 'False', indicating that the thread should
        continue execution immediately, within the supplied generator.
        """




class IEventSource(ITaskSwitch):

    """Thing you can receive notifications from, as well as task-switch on

    Note that every event source can control task switching, but not every
    task switcher is an event source.  Generators, for example, can control
    task flow, but do not really produce any "events".

    Event callbacks must *not* raise errors, as event sources are not required
    to ensure that all callbacks are executed when a callback raises an error.
    """

    def addCallback(func):
        """Call 'func' the next time this event occurs

        If this method is called from within a callback, 'func' must *not* be
        invoked until the *next* occurrence of the event.
        """

    def addSubscriber(func):
        """Return an 'ISubscription' for "Call 'func' each time event occurs"

        (In the absence of more meaningful semantics for repeated occurences,
        the 'ISubscription' may be implemented as an object that adds itself
        as a callback, then re-adds itself as a callback each time it's
        called.)
        """














class ISubscription(protocols.Interface):

    """Ongoing subscription to an 'IEventSource'"""

    def pause():
        """Stop receiving events until 'resume()' is called"""

    def resume():
        """Resume receiving events"""



class IValue(IEventSource):

    """A variable that triggers events when its value is changed or set"""

    def set(value):
        """Set the value to 'value', triggering an event"""

    def __call__():
        """Return the current value"""

    def asQueue():
        """Return an 'IQueue' that yields each new value set"""

    def when(condition=lambda v:v):
        """'IEventSource' that triggers when 'condition(value)' is true"""

    def equals(val):
        """'IEventSource' that triggers when value is set to 'val'"""


class IState(IValue):
    """An 'IValue' that only triggers events when its value is *changed*

    That is, when 'oldValue<>newValue'.  Note that this affects the
    behavior of dependent event sources such as supplied by the 'when()',
    'equals()', and 'asQueue()' methods.
    """


class IQueue(IEventSource):

    """An iterator that triggers events as values become available

    Note that queues do not "multicast".  If multiple callbacks are registered
    for the same queue, they will receive items in a "round robin" fashion.
    That is, each will receive some subset of the items put into the queue.
    Thus, a queue can be used either as a simple data source, or as a pool from
    which readers may obtain items (for e.g. task distribution).
    """

    def put(ob):
        """Put 'ob' on the end of the queue

        Note that this must be buffered, since a reader of the queue may
        not be able to read its contents immediately.  This method should
        raise 'AlreadyRead' if the queue has been closed."""

    def close():
        """Stop accepting values; raise 'StopIteration' after all consumed"""

    def next():
        """Return (and remove) the next item in the queue

        This method should raise 'StopIteration' if the queue is closed and
        any buffered items have been consumed, or 'AlreadyRead' if there are
        no items in the queue (meaning that somebody isn't yielding to the
        queue, or else is sharing it.)"""

    def push(ob):
        """Push 'ob' on the beginning of the queue

        This can be used by a reader to put back an item they don't want (yet).
        Note that if there are no other readers and the reader yields to the
        queue, the reader will read the pushed item on its next read attempt.
        """

    def __iter__():
        """Must return 'self' (i.e. queues are not reiterable!)"""


    readersWaiting = protocols.Attribute(
        """'IState' for whether callbacks registered > items buffered

        (This allows generator-like data sources to suspend until somebody
        wants the information they're putting in the queue.)
        """
    )


class IThread(protocols.Interface):

    """Simulate a thread using iterables that yield 'ITaskSwitch' objects

    Threads maintain a stack of "currently executing iterables".  The topmost
    iterable's 'next()' method is invoked repeatedly to obtain 'ITaskSwitch'
    instances that determine whether the thread will continue, invoke a nested
    iterable (by pushing it on the stack), or be suspended (by returning from
    the 'run()' method.  When an iterable is exhausted, it's popped from the
    stack, and the next-highest iterable is resumed.  This simple "virtual
    machine" allows linear Python code to co-operatively multitask on the
    basis of arbitrary events.
    """

    def step():
        """Run until thread is suspended by an 'ITaskSwitch' or finishes"""

    def enable():
        """Un-suspend the thread"""

    def call(iterator):
        """Put 'iterable' at the top of the stack for the next 'step()'"""

    isFinished = protocols.Attribute(
        """An 'IState' that's set to 'True' when the thread is completed"""
    )






class IClock(protocols.Interface):

    """A clock controls the running of an event-driven program"""

    now = protocols.Attribute("""'IValue' representing the current time""")

    def tick():
        """Update 'now', and invoke scheduled callbacks"""

    def run():
        """'tick()' until no events/foreground threads, or 'stop()' called"""

    def stop():
        """Exit 'run()' as soon as due or overdue callbacks are finished"""

    def crash():
        """Force immediate exit from 'run()', without triggering any events"""

    def schedule(callback, delay=0):
        """Call 'callback' after at least 'delay' seconds"""

    def spawn(iterator, background=True):
        """Return a new (possibly background) thread running 'iterator'"""

    def sleep(secs=0):
        """Get 'IEventSource' that fires 'secs' from now"""

    def until(time):
        """Get 'IEventSource' that fires when 'clock.now() >= time'"""

    def idleFor():
        """Return number of seconds until next scheduled callback"""

    starting = protocols.Attribute(
        """'IEventSource' that fires when 'run()' is first called"""
    )

    stopping = protocols.Attribute(
        """'IEventSource' that fires when 'run()' is about to exit"""
    )

class ISelector(protocols.Interface):

    """Like a reactor, but supplying 'IEventSources' instead of callbacks

    May be implemented using a callback on 'IClock.now' that calls a reactor's
    'iterate()' method with a delay of 'IClock.idleFor()' seconds.
    """

    def readable(stream):
        """Get 'IEventSource' that triggers each time 'stream' is readable"""

    def writable(stream):
        """Get 'IEventSource' that triggers each time 'stream' is writable"""

    def signal(signame):
        """Get 'IEventSource' that triggers whenever named signal occurs"""


























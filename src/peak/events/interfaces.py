from peak.api import *

__all__ = [
    'ITaskSwitch', 'IEventSource', 'ISubscription', 'IValue', 'IState',
    'IQueue', 'IProactor', 'IThread',
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
                self.addCallback(thread.run)
                return True

        at least in cases where the scheduler is also an 'IEventSource'.

        This method is explicitly allowed to call the thread's 'schedule()'
        method, thus "interrupting" the currently running routine in that
        thread.  The 'ITaskSwitch' adapter for generators schedules the
        generator, and returns 'False', indicating that the thread should
        continue execution immediately, within the supplied generator.
        """




class IEventSource(ITaskSwitch):

    """Thing you can receive notifications from, as well as task-switch on

    Note that every event source can control task switching, but not every
    task switcher is an event source.  Generators, for example, can control
    task flow, but do not really produce any "events".

    Event callbacks must *not* raise errors: event sources are not required
    to ensure that all callbacks are executed, if a callback raises an error.
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


class IState(IValue):
    """An 'IValue' that only triggers events when its value is *changed*

    (That is, when 'oldValue<>newValue'.)
    """






















class IQueue(IEventSource):

    """An iterator that triggers events when new values are available

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

    def __iter__():
        """Must return 'self' (i.e. queues are not reiterable!)"""

    readersWaiting = protocols.Attribute(
        """'IState' for whether callbacks registered > items buffered

        (This allows generator-like data sources to suspend until somebody
        wants the information they're putting in the queue.)
        """
    )


class IProactor(protocols.Interface):

    """Like a reactor, but supplying 'IEventSources' instead of callbacks"""

    def sleep(secs=0):
        """Get 'IEventSource' that delays 'secs' from each callback request"""

    def readable(stream):
        """Get 'IEventSource' that triggers each time 'stream' is readable"""

    def writable(stream):
        """Get 'IEventSource' that triggers each time 'stream' is writable"""


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

    def run(iterator=None):
        """Run until thread is finished (or suspended by an 'ITaskSwitch')"""

    def schedule(iterator):
        """Put 'iterable' at the top of the list for the next 'run()'"""

    isFinished = protocols.Attribute(
        """An 'IState' that's set to 'True' when the thread is completed"""
    )





from peak.api import *

__all__ = [
    'ITask', 'ITaskSwitch', 'IEventSource', 'IEventSink', 'IReadableSource',
    'IWritableSource', 'IConditional', 'ISemaphore', 'IThread',
    'IScheduledThread', 'IThreadState', 'IScheduler', 'ISignalSource',
    'ISelector', 'IEventLoop',
]


class ITask(protocols.Interface):

    """Iterator suitable for use with a thread, such as a generator-iterator"""

    def __iter__():
        """*Must* return the 'ITask'; i.e. iterator not iterable"""

    def next():
        """Return an 'ITaskSwitch', or value to be yielded to previous task"""






















class ITaskSwitch(protocols.Interface):

    """What a thread yields control to

    Iterators running in a thread yield 'ITaskSwitch' objects to control the
    thread's flow and co-operation.

    In addition to PEAK-supplied event sources like 'Value', 'Semaphore', and
    'Condition', generator-iterators and other 'ITask' objects are also
    adaptable to 'ITaskSwitch', thus allowing one to e.g.
    'yield someGenerator(someArgs)' in a thread.  This allows the nested
    generator to run next in the thread.
    """


    def nextAction(thread=None, state=None):
        """Return true if thread should continue

        If supplied, 'thread' and 'state' are an 'IThread' and 'IThreadState',
        respectively, and the task switch may perform any needed actions with
        them, such as arranging to call back 'thread.step()', or performing
        an action such as 'state.YIELD(value)' or 'state.CALL(task)'.
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
        """Call 'func(source,event)' the next time this event occurs

        If this method is called from within a callback, 'func' must *not* be
        invoked until the *next* occurrence of the event.

        Note also that callbacks will be called at most once for each time
        they are registered; adding a callback does not result in an ongoing
        "subscription" to the event source.
        """


class IEventSink(protocols.Interface):

    """Signature for callables passed to 'IEventSource.addCallback()'"""

    def __call__(source, event):
        """Accept 'event' from an 'IEventSource' ('source')

        This method should return 'True' if the callback wishes to "consume"
        the event (i.e. prevent other callbacks from receiving it).  However,
        the event source is free to ignore the callback's return value.  The
        "consume an event" convention is normally used only by "stream" event
        sources such as distributors and semaphores, and by event sources with
        ongoing listeners/handlers (as opposed to one-time callbacks).
        """



class IReadableSource(IEventSource):

    """An event source whose current value or state is readable"""

    def __call__():
        """Return the current value, condition, or event"""


class IWritableSource(IReadableSource):

    """An event source whose current value or state can be read or changed"""

    def set(value,force=False):
        """Set the current state to 'value', possibly triggering an event

        If the 'force' parameter is a true value, and the event source would
        not have fired an event due to a lack of change in value, the event
        source should fire the event anyway.  (The firing may be suppressed
        for other reasons, such as falsehood in the case of an 'IConditional'
        or 'ISemaphore'.)"""


class IConditional(IReadableSource):

    """An event source that fires when (or resumes while) its value is true

    Note that callbacks added to an 'IConditional' with a true value should be
    called immediately."""


class ISemaphore(IWritableSource,IConditional):

    """An event source that allows 'n' threads to proceed at once"""

    def put():
        """Increase the number of runnable threads by 1"""

    def take():
        """Decrease the number of runnable threads by 1"""


class IThread(protocols.Interface):

    """Simulate a thread using iterables that yield 'ITaskSwitch' objects

    Threads maintain a stack of "currently executing iterables".  The topmost
    iterable's 'next()' method is invoked repeatedly to obtain 'ITaskSwitch'
    instances that determine whether the thread will continue, invoke a nested
    iterable (by pushing it on the stack), or be suspended (by returning from
    the 'step()' method.  When an iterable is exhausted, it's popped from the
    stack, and the next-highest iterable is resumed.  This simple "virtual
    machine" allows linear Python code to co-operatively multitask on the
    basis of arbitrary events.

    Iterators used in threads must call 'events.resume()' immediately after
    each 'yield' statement (or at the beginning of their 'next()' method, if
    not a generator), in order to ensure that errors are handled properly.  If
    the event source or generator that was yielded sends a value or event
    back to the thread, that value will be returned by 'resume()'.

    Iterators may send values back to their calling iterators by yielding
    values that do not implement 'ITaskSwitch'.  Event sources may send values
    back to a thread by passing them as events to the thread's 'step()'
    callback method.
    """

    def step(source=None,event=NOT_GIVEN):
        """Run until thread is suspended by an 'ITaskSwitch' or finishes

        If the thread's current generator calls 'events.resume()', it will
        receive 'event' as the return value.
        """

    isFinished = protocols.Attribute(
        """'IConditional' that fires when the thread is completed"""
    )






class IScheduledThread(IThread):

    """A thread that relies on a scheduler for ongoing execution

    Scheduled threads do not run when their 'step()' methods are called, but
    instead simply put themselves on the scheduler's schedule for later
    execution.  This means that scheduled threads do not run during operations
    that cause callbacks, and so they cannot raise errors in apparently-unrelated
    code.  They also are less likely to cause unintended or unexpected
    side-effects due to their executing between 'yield' statements in other
    threads.  And finally, scheduled threads can reliably signal that they
    were aborted due to an uncaught exception, via their 'aborted' attribute.

    There are some drawbacks, however.  First, scheduled threads require a
    scheduler, and the scheduler must 'tick()' repeatedly as long as one wishes
    the threads to continue running.  Second, scheduled threads can take
    slightly longer to task switch than unscheduled ones, because multiple
    callbacks are required.

    Last, but far from least, when a scheduled thread is resumed, it cannot be
    guaranteed that another thread or callback has not already contravened
    whatever condition the thread was waiting for.  This is true even if only
    one thread is waiting for that condition, since non-thread callbacks or
    other code may be executed between the triggering of the event, and the
    time at which the thread's resumption is scheduled.
    """


    def step(source=None,event=NOT_GIVEN):
        """Schedule thread to resume during its scheduler's next 'tick()'"""


    aborted = protocols.Attribute(
        """'IConditional' that fires if the thread is aborted"""
    )






class IThreadState(protocols.Interface):

    """Control a thread's behavior

    This interface is made available only to 'ITaskSwitch' objects via their
    'nextAction()' method, so you don't need to know about this unless you're
    writing a new kind of event source or task switch.  Even then, 90% of the
    time the 'YIELD()' method is the only one you'll need.  The rest should be
    considered "internal" methods that can break things if you don't know
    precisely what you're doing and why.
    """

    def YIELD(value):
        """Supply 'value' to next 'resume()' call"""

    def CALL(iterator):
        """Cause thread to execute 'iterator' next"""

    def RETURN():
        """Silently abort the currently-running iterator"""

    def THROW():
        """Reraise 'sys.exc_info()' when current iterator resumes"""

    def CATCH():
        """Don't reraise 'sys.exc_info()' until next 'THROW()'"""


    lastEvent = protocols.Attribute(
        """Last value supplied to 'YIELD()', or 'NOT_GIVEN'"""
    )

    handlingError = protocols.Attribute(
        """True between 'THROW()' and 'CATCH()'"""
    )

    stack = protocols.Attribute(
        """List of running iterators"""
    )


class IScheduler(protocols.Interface):

    """Time-based conditions"""

    def spawn(iterator):
        """Return a new 'IScheduledThread' based on 'iterator'"""

    def now():
        """Return the current time"""

    def tick():
        """Invoke scheduled callbacks whose time has arrived"""

    def sleep(secs=0):
        """'IEventSource' that fires 'secs' after each callback/task switch

        The object returned is reusable: each time you yield it or add a
        callback to it, the thread or callback will be delayed 'secs' from
        the time that the task switch was requested or the callback added.
        Multiple threads and callbacks may wait on the same 'sleep()' object,
        although they will "wake" at different times according to when they
        went to "sleep"."""

    def until(time):
        """Get an 'IConditional' that fires when 'scheduler.now() >= time'"""

    def timeout(secs):
        """Get an 'IConditional' that will fire 'secs' seconds from now"""

    def time_available():
        """Return number of seconds until next scheduled callback"""










class ISignalSource(protocols.Interface):

    """Signal events"""

    def signals(*signames):
        """'IEventSource' that triggers whenever any of named signals occur

        Note: signal callbacks occur from within a signal handler, so it's
        usually best to yield to an 'IScheduler.sleep()' (or use a scheduled
        thread) in order to avoid doing anything that might interfere with
        running code.

        Also note that signal event sources are only active so long as a
        reference to them exists.  If all references go away, the signal
        handler is deactivated, and no callbacks will be sent, even if they
        were already registered.
        """

    def haveSignal(signame):
        """Return true if signal named 'signame' exists"""


class ISelector(ISignalSource):

    """Like a reactor, but supplying 'IEventSources' instead of callbacks

    May be implemented using a callback on 'IScheduler.now' that calls a
    reactor's 'iterate()' method with a delay of 'IScheduler.time_available()'
    seconds.  Note that all returned event sources are active only so long
    as a reference to them is kept.  If all references to an event source go
    away, its threads/callbacks will not be called."""

    def readable(stream):
        """'IConditional' that's true when 'stream' is readable"""

    def writable(stream):
        """'IConditional' that's true when 'stream' is writable"""

    def exceptional(stream):
        """'IConditional' that's true when 'stream' is in error/out-of-band"""








class IEventLoop(IScheduler, ISelector):

    def runUntil(eventSource,suppressErrors=False):
        """'tick()' repeatedly until 'eventSource' fires, returning event

        If 'suppressErrors' is true, this method will trap and log
        all errors without allowing them to reach the caller.  Note
        that event loop implementations based on Twisted *require*
        that 'suppressErrors' be used."""

































from peak.interface import Interface, Attribute
from peak.api import PropertyName
from peak.binding.interfaces import IBindingFactory, IComponent
import sys, os

CLUSTER = PropertyName('peak.running.cluster').of(None)

__all__ = [

    'CLUSTER',

    'ICmdLineAppFactory', 'ICmdLineApp',

    'IPeriodicTask', 'ITaskQueue', 'IMainLoop',

    'IAdaptiveTask', 'IAdaptiveTaskSPI',

    'IBasicReactor', 'ITwistedReactor',

]





















class ICmdLineAppFactory(IBindingFactory):

    """Class interface for creating ICmdLineApp components

    A command-line app object is created with keyword arguments for 'stdin',
    'stdout', 'stderr', 'environ', and 'argv'.  It is free to use default
    values for items not supplied, but it must *not* bypass or override any
    values which *are* supplied.  E.g. it should *never* write to 'sys.stdin'.
    The purpose of this encapsulation is to allow application objects to
    be composed by other application objects, and to also allow "server"
    invocations of applications, as is needed for protocols like FastCGI
    and ReadyExec."""

    def __call__(parentComponent=None, componentName=None,

        argv  = sys.argv,

        stdin = sys.stdin,
        stdout = sys.stdout,
        stderr = sys.stderr,

        environ = os.environ, **otherAttrs):

        """Create a new "command-line" application instance"""



class ICmdLineApp(IComponent):

    """Encapsulate a "commandline-style" app for reusability/composability"""

    def run():
        """Perform the functionality of the application; return exit code"""








class IPeriodicTask(Interface):

    """Thing that does work periodically"""

    def __call__():
        """Do whatever work is required; return truth if useful work done

        This method should update the task's 'pollInterval' if needed.  To
        request that the task should no longer be recurrently scheduled,
        raise 'exceptions.StopRunning'."""

    pollInterval = Attribute(
        """Number of seconds till next desired invocation"""
    )

    priority = Attribute("""Integer priority value; higher=more important""")

    def __cmp__(other):
        """Compare to another daemon on the basis of priority"""






















class ITaskQueue(Interface):

    """Schedule and run prioritized periodic tasks using the system reactor

    When more than one task is available for execution, the highest priority
    one is executed.  (Equal priority tasks are scheduled in round-robin
    fashion.)  A task is considered available for execution when it is first
    added, and when its 'pollInterval' elapses after its last execution.

    Whenever the queue is enabled (the default state), tasks are executed
    and scheduled.  When disabled, execution and scheduling stops until
    re-enabled.  Enabling and disabling do not affect the task schedule
    in any way, although while the queue is disabled, tasks may pile up
    in the "available" state.  (Note: a task queue is allowed to let the
    system reactor hold onto waiting tasks, so if the reactor's state is
    reset, queue contents may be lost whether the queue is enabled or not.)

    Unlike many scheduling-related components, you may have as many of
    these as you like, but each must have access to an 'IBasicReactor'
    utility and an 'IMainLoop' utility.

    Note, by the way, that this interface does not include a way to
    remove tasks from the queue.  A task may remove itself from the
    queue by raising 'StopRunning' when it is invoked."""


    def addTask(ptask):
        """Add 'IPeriodicTask' instance 'ptask' to the priority queue"""

    def enable():
        """Allow all added tasks to run (default state)"""

    def disable():
        """Stop executing tasks after the current task completes"""







class IMainLoop(Interface):

    """Run the reactor event loop, with activity monitoring and timeouts

    This is typically used to control the lifetime of an event-driven
    application.  The application invokes 'run()' with the desired parameters
    once the system reactor is ready to run.

    Reactor-driven components should invoke the 'activityOccurred()' method
    on this interface whenever I/O or useful processing occurs, in order to
    prevent inactivity timeouts."""


    def activityOccurred():
        """Call this periodically to prevent inactivity timeouts."""


    lastActivity = Attribute(
        """The 'time()' that 'activityOccurred()' was last called, or the
        start of the current 'run()', whichever is later.  If 'run()' is
        not currently executing, this is 'None'."""
    )


    def run(stopAfter=0, idleTimeout=0, runAtLeast=0):

        """Loop polling for IO, GUI, and scheduled events

        'stopAfter' -- No scheduled actions will be invoked after this
                       many seconds.  'run()' will exit soon afterward.
                       (Zero means "run until the reactor stops".)

        'idleTimeout' -- If 'activityOccurred()' is not called for this
                         many seconds, stop and return from 'run()'.
                         (Zero means, "don't check for inactivity".)

        'runAtLeast' -- run at least this many seconds before an 'idleTimeout'
                        is allowed to occur.  (Zero means, "idle timeouts
                        may occur any time after the run starts.")
        """

class IAdaptiveTask(IPeriodicTask):

    """Periodic task with tunable polling interval"""

    runEvery = Attribute(
       """Base value for 'pollInterval' when daemon has no work waiting"""
    )

    increaseIdleBy = Attribute(
        """Add this to 'pollInterval' each time there's no work"""
    )

    multiplyIdleBy = Attribute(
        """Multiply 'pollInterval' by this each time there's no work"""
    )

    maximumIdle = Attribute(
        """Never let 'pollInterval' get bigger than this"""
    )

    minimumIdle = Attribute(
        """'pollInterval' used when daemon has work to do"""
    )


















class IAdaptiveTaskSPI(Interface):

    """Things you implement when subclassing the AdaptiveTask abstract base"""

    def getWork():
        """Return a "job" (true value) for 'doWork()', or a false value"""

    def doWork(job):
        """Do work described by 'job'; return a true value if successful"""

    lock = Attribute(
        """An optional lock object to wrap calls to 'getWork()/doWork()'"""
    )

    def lockMe():
        """Override this for custom locking: return True if lock acquired"""

    def unlockMe():
        """Override this for custom locking: ensure lock released"""






















class IBasicReactor(Interface):

    """I/O Scheduler -- 'twisted.internet.reactor' or a substitute

    Twisted reactors actually do a lot more than this, but this is all
    we need for basic "running" operations that don't involve support
    for specialized protocols.  This is a simple enough set of operations
    that we should be able to provide an "unTwisted" implementation."""

    def run():
        """Loop polling for IO or GUI events and calling scheduled funcs"""

    def stop():
        """Cause 'run()' to exit at the earliest practical moment"""

    def callLater(delay, callable, *args, **kw):
        """Invoke 'callable' after 'delay' seconds with '*args, **kw'"""


    def addReader(reader):
        """Register 'reader' file descriptor to receive 'doRead()' calls

        'reader' must have a 'fileno()' method and a 'doRead()' method."""

    def addWriter(writer):
        """Register 'writer' file descriptor to receive 'doWrite()' calls

        'writer' must have a 'fileno()' method and a 'doWrite()' method."""

    def removeReader(reader):
        """Unregister 'reader'"""

    def removeWriter(writer):
        """Unregister 'writer'"""

    def iterate(delay=0):
        """Handle scheduled events, then do I/O for up to 'delay' seconds"""




class ITwistedReactor(IBasicReactor):

    """Ask for this if you really need Twisted

    For the "rest" of this interface's documentation, see
    'twisted.internet.interfaces' and look at the various 'IReactor*'
    interfaces.

    The purpose of this interface in PEAK is to let a component ask for
    a Twisted reactor if it really needs one.
    """
































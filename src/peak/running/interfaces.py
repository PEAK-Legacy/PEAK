from peak.interface import Interface, Attribute
from peak.api import PropertyName

CLUSTER = PropertyName('peak.running.cluster').of(None)

__all__ = [

    'CLUSTER',

    'IPeriodicTask', 'ITaskScheduler', 'IAdaptiveTask', 'IAdaptiveTaskSPI',

]


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








class ITaskScheduler(Interface):

    """Single-threaded task and I/O scheduler

        Only one instance is useful per thread.  This is our access point to
        Twisted or a replacement thereof, with some additions for better
        managing periodic tasks and "transient" servers such as an
        all-daemon worker process or a webserver-invoked FastCGI process."""

    def addPeriodic(ptask):
        """Add 'ptask' to the prioritized processing schedule"""

    def run():
        """Loop polling for IO or GUI events and calling scheduled funcs"""

    def stop():
        """Cause 'run()' to exit at the earliest practical moment"""

    def activityOccurred():
        """Automatically called when daemons perform useful
        activities, but may also be called by protocol handlers
        such as servers to flag activity."""

    lastActivity = Attribute(
        """The 'time()' that 'activityOccurred' was last called, or 'None'
        if not currently running."""
    )

    runningSince = Attribute(
        """The time that 'run()' was called, or 'None' if not running"""
    )

    stayAliveFor = Attribute(
        """'run()' will run at least this many seconds"""
    )

    shutDownAfter = Attribute(
        """No scheduled actions will be invoked after this many seconds;
        'run()' will exit soon afterward."""
    )

    shutDownIfIdleFor = Attribute(
        """If 'activityOccurred()' is not called for this many
        seconds, and the 'stayAliveFor' time has passed, shut down."""
    )

    def callLater(delay, callable, *args, **kw):
        """Invoke 'callable' after 'delay' seconds with '*args, **kw'"""


































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























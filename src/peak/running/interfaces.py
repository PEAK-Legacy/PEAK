from peak.interface import Interface, Attribute
from peak.api import PropertyName

CLUSTER = PropertyName('peak.running.cluster').of(None)

__all__ = [

    'CLUSTER',

    'IDaemon', 'IDaemonScheduler', 'IDaemonicApp', 'IEventLoop',
    'IBaseDaemon', 'IBaseDaemonSPI',
    
]




























class IDaemon(Interface):

    """Thing that does work periodically"""

    def __call__():
        """Do whatever work is required, and update pollInterval"""

    pollInterval = Attribute(
        """Number of seconds till next desired invocation"""
    )

    priority = Attribute("""Integer priority value""")

    def __cmp__(other):
        """Compare to another daemon on the basis of priority"""


class IDaemonScheduler(Interface):

    """Thing that schedules daemons; must have an IEventLoop available"""

    def addDaemon(daemon):
        """Add 'daemon' to the schedule and ensure processing is scheduled"""

    def run():
        """Run daemons indefinitely"""

    def stop():
        """Stop running daemons and return from 'run()'"""

    def activityOccurred():
        """Automatically called when daemons perform useful
        activities, but may also be called by protocol handlers
        such as servers to flag activity."""







class IDaemonicApp(IDaemonScheduler):

    """An application that just runs daemons/servers"""

    # XXX this should also subclass some kind of 'app' interface

    stayAliveFor = Attribute(
        """Daemons will run at least this many seconds"""
    )

    shutDownAfter = Attribute(
        """No daemons will be invoked after this many seconds; 
        the application will exit soon afterward."""
    )

    shutDownIfIdleFor = Attribute(
        """If 'activityOccurred()' is not called for this many 
        seconds, and the 'stayAliveFor' time has passed, shut down."""
    )
     

class IEventLoop(Interface):

    """Per-interpreter event loop manager; 'twisted.internet.reactor'
       implements this for us."""

    def callLater(delay, callable, *args, **kw):
        """Invoke 'callable' after 'delay' seconds with '*args, **kw'"""

    def run():
        """Loop polling for IO or GUI events and calling scheduled funcs"""

    def stop():
        """Cause 'run()' to exit at the earliest practical moment"""    







class IBaseDaemon(IDaemon):

    """Extra goodies to be supplied by BaseDaemon"""

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
    

















class IBaseDaemonSPI(Interface):

    """Things you implement when subclassing BaseDaemon"""

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


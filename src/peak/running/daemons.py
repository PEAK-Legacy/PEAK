from peak.api import *
from interfaces import *
from bisect import insort_left
from peak.naming.interfaces import IStreamFactory
from peak.storage.interfaces import IManagedConnection
from lockfiles import NullLockFile

__all__ = [
    'AdaptiveTask', 'TaskQueue',
]































class TaskQueue(binding.Component):

    protocols.advise(
        instancesProvide=[ITaskQueue]
    )

    reactor     = binding.Obtain(IBasicReactor)
    loop        = binding.Obtain(IMainLoop)
    ping        = binding.Obtain('loop/activityOccurred')

    activeTasks = binding.Make(list)
    _scheduled  = False
    _disabled   = False


    def addTask(self,ptask):
        insort_left(self.activeTasks, ptask)    # round-robin if same priority
        self._scheduleProcessing()


    def enable(self):
        self._disabled = False
        self._scheduleProcessing()


    def disable(self):
        self._disabled = True


    def _scheduleProcessing(self):

        if self._scheduled or self._disabled or not self.activeTasks:
            return

        self.reactor.callLater(0, self._processNextTask)
        self._scheduled = True





    def _processNextTask(self):

        # Processes the highest priority pending task

        del self._scheduled

        if self._disabled:
            return      # Don't run tasks when disabled


        didWork = cancelled = False

        try:

            task = self.activeTasks.pop()  # Highest priority task

            try:
                didWork = task()

            except exceptions.StopRunning:  # Don't reschedule the task
                cancelled = True

        finally:

            if didWork:
                self.ping()     # we did something; make note of it

            if not cancelled:
                self.reactor.callLater(task.pollInterval,self.addTask,task)

            self._scheduleProcessing()










class AdaptiveTask(binding.Component):

    """Periodic task that adapts its polling interval based on its workload"""

    protocols.advise(
        instancesProvide=[IAdaptiveTask]
    )

    pollInterval = binding.Obtain('minimumIdle')

    runEvery = binding.Require("Number of seconds between invocations")

    minimumIdle    = binding.Obtain('runEvery')
    increaseIdleBy = 0
    multiplyIdleBy = 1

    priority = 0

    # Maximum idle defaults to increasing three times

    maximumIdle = binding.Make(
        lambda s: s.runEvery * s.multiplyIdleBy**3 + s.increaseIdleBy*3
    )

    __ranLastTime = True


    def __cmp__(self, other):
        """Compare to another daemon on the basis of priority"""
        return cmp(self.priority, other.priority)


    __addToQueue = binding.Make(
        lambda self:
            self.lookupComponent(ITaskQueue).addTask(self), uponAssembly=True
    )





    def __call__(self):

        """Do a unit of work, return true if anything worthwhile was done"""

        didWork = False

        try:
            # Make sure we're locked while working

            if self.lockMe():
                try:
                    job = self.getWork()
                    if job:
                        didWork = self.doWork(job)
                finally:
                    self.unlockMe()

        finally:

            if didWork:
                # We did something, so use minimum interval
                self.pollInterval = self.minimumIdle

            elif self.__ranLastTime:
                # First time we failed, set to 'runEvery'
                self.pollInterval = self.runEvery

            else:
                # Adapt polling interval
                pi = self.pollInterval * self.multiplyIdleBy
                pi = min(pi + self.increaseIdleBy, self.maximumIdle)
                self.pollInterval = pi

            self.__ranLastTime = didWork

        return didWork





    def getWork(self):
        """Find something to do, and return it"""
        pass

    def doWork(self,job):
        """Do the job; throw errors if unsuccessful"""
        return job

    lockMe = binding.Obtain(
        'lock/attempt', doc=
        """Try to begin critical section for doing work, return true if successful"""
    )

    unlockMe = binding.Obtain(
        'lock/release', doc=
        """End critical section for doing work"""
    )

    _name = 'unnamed_task'    # Allow ZConfig to give us a '_name'

    logName = binding.Make(
        lambda self: "logger:daemons."+self._name
    )

    log = binding.Make(
        lambda self: self.lookupComponent(self.logName), adaptTo = logs.ILogger
    )

    lockName = None

    lock = binding.Make(
        lambda s:
            s.lockName and s.lookupComponent(s.lockName) or NullLockFile(),
        adaptTo = ILock
    )






from glob import glob
import os.path, time


class FileCleaner(AdaptiveTask):

    """Periodically remove stale files from a directory"""

    directory  = binding.Require("Directory name to search in")
    matchFiles = binding.Require("Python glob for files to check")

    olderThan  = binding.Require(
        "Age in seconds after which files are stale"
    )

    pattern   = binding.Make(
        lambda self: os.path.join(self.directory,self.matchFiles)
    )

    def getWork(self):
        t = time.time() - self.olderThan
        self.log.info(
            'Scanning for files matching %s older than %d minutes',
            self.pattern, self.olderThan/60
        )
        return [f for f in glob(self.pattern) if os.stat(f).st_mtime < t]

    def doWork(self, job):
        self.log.info('Deleting %d old files', len(job))
        for f in job:
            os.unlink(f)










class URLChecker(AdaptiveTask):
    """Check if specified resource is up and running; try to restart if not"""

    url = binding.Require("name (usually URL) of resource to check")
    restartURL = binding.Require("command to execute to restart")

    restarter = binding.Make(
        lambda self: self.lookupComponent(self.restartURL)
    )

    def getWork(self):
        self.log.info("%s: checking %s", self._name, self.url)
        try:
            rsrc = self.lookupComponent(self.url)
        except:
            self.log.exception("%s: Error looking up %s", self._name, self.url)
            return True

        try:
            err = adapt(rsrc, ICheckableResource).checkResource()

            if err:
                self.log.error("%s: %s", self._name, err)
                return True
        except:
            self.log.exception("%s: Error checking %s", self._name, rsrc)
            return True

    def doWork(self, job):
        self.log.warning('%s: not responding; restarting', self._name)
        ret = adapt(self.restarter, ICmdLineAppFactory)(self).run()
        # XXX logging of command output?
        if ret:
            self.log.warning("%s: restart returned %d", self._name, ret)

        if self.getWork():
            self.log.critical('%s: still not responding', self._name)
        else:
            self.log.log(logs.NOTICE, '%s: now responding', self._name)
        return True

class StreamFactoryAsCheckableResource(object):

    protocols.advise(
        instancesProvide = [ICheckableResource],
        asAdapterForProtocols = [IStreamFactory]
    )

    def __init__(self, ob, proto):
        self.sf = ob

    def checkResource(self):
        if not self.sf.exists():
            return "Check failed"



class ManagedConnectionAsCheckableResource(object):

    protocols.advise(
        instancesProvide = [ICheckableResource],
        asAdapterForProtocols = [IManagedConnection]
    )

    def __init__(self, ob, proto):
        self.mc = ob

    def checkResource(self):
        self.mc.connection # reference it to ensure it's opened
        # and just return None (success)













from peak.api import *
from interfaces import *
from bisect import insort_left
from peak.naming.interfaces import IStreamFactory
from peak.storage.interfaces import IManagedConnection

__all__ = [
    'AdaptiveTask', 'TaskQueue',
]
































class TaskQueue(binding.Component):

    protocols.advise(
        instancesProvide=[ITaskQueue]
    )

    reactor     = binding.bindTo(IBasicReactor)
    loop        = binding.bindTo(IMainLoop)
    ping        = binding.bindTo('loop/activityOccurred')

    activeTasks = binding.New(list)
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

    pollInterval = binding.bindTo('minimumIdle')

    runEvery = binding.requireBinding("Number of seconds between invocations")

    minimumIdle    = binding.bindTo('runEvery')
    increaseIdleBy = 0
    multiplyIdleBy = 1

    priority = 0

    # Maximum idle defaults to increasing three times

    maximumIdle = binding.Once(
        lambda s,d,a: s.runEvery * s.multiplyIdleBy**3 + s.increaseIdleBy*3
    )

    __ranLastTime = True


    def __cmp__(self, other):
        """Compare to another daemon on the basis of priority"""
        return cmp(self.priority, other.priority)


    __addToQueue = binding.whenAssembled(
        lambda self,d,a:
            self.lookupComponent(ITaskQueue).addTask(self),
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


    def lockMe(self):
        """Try to begin critical section for doing work, return true if successful"""

        lock = self.lock

        if lock:
            return lock.attempt()

        return True


    def unlockMe(self):
        """End critical section for doing work"""

        lock = self.lock
        if lock: lock.release()


    lock = None

    _name = 'unnamed_task'    # Allow ZConfig to give us a '_name'

    logName = binding.Once(
        lambda s,d,a: PropertyName("peak.logs.daemons."+s._name)
    )

    log = binding.Once(
        lambda s,d,a: s.lookupComponent(s.logName), adaptTo = ILogger
    )


from glob import glob
import os.path, time


class FileCleaner(AdaptiveTask):

    """Periodically remove stale files from a directory"""

    directory  = binding.requireBinding("Directory name to search in")
    matchFiles = binding.requireBinding("Python glob for files to check")

    olderThan  = binding.requireBinding(
        "Age in seconds after which files are stale"
    )

    pattern   = binding.Once(
        lambda s,d,a: os.path.join(s.directory,s.matchFiles)
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

    url = binding.requireBinding("name (usually URL) of resource to check")
    restartURL = binding.requireBinding("command to execute to restart")

    restarter = binding.Once(
        lambda s,d,a: s.lookupComponent(s.restartURL)
    )

    def getWork(self):
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













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












from glob import glob
import os, time


class FileCleaner(AdaptiveTask):

    """Periodically remove stale files from a directory"""
    
    pattern = binding.requireBinding("Python glob pattern for files to check")
    olderThan = binding.requireBinding("Age in seconds after which files are stale")
    log = binding.requireBinding("logger object")

    def getWork(self):
        t = time.time() - self.olderThan
        self.log.info(
            'Scanning for files matching %s older than %d minutes',
            d, self.older_than/60
        )
        return [f for f in glob(self.pattern) if os.stat(f).st_mtime < t]

    def doWork(self, job):
        self.log.info('Deleting %d old files', len(job))
        for f in job:
            os.unlink(f)

















import traceback


class URLChecker(AdaptiveTask):

    """Checks if a resource specified by a URL is up and running
    and tries to restart it if not"""
    
    url = binding.requireBinding("name (usually URL) for resource to check")    
    restarter = binding.requireBinding("command to execute to restart")

    def getWork(self):
        try:
            rsrc = self.lookupComponent(self.url)
        except:
            # XXX log error
            return True
            
        err = adapt(rsrc, ICheckableResource).checkResource()

        if err:
            # XXX log error
            return True
        
        return False
        

    def doWork(self, job):
        self.log.warning('Service %s not responding; restarting', self.name)
        ret = adapt(self.restarter, ICmdLineAppFactory)(self).run()
        # XXX logging of command output?
        if ret:
            self.log.warning("Service %s restart returned %d", self.name, ret)
        
        if self.getWork():
            self.log.critical('Service %s still not responding', self.name)
        else:
            self.log.notice('Service %s now responding', self.name)
        return True


class StreamFactoryAsCheckableResource(object):

    protocols.advise(
        instancesProvide = [ICheckableResource],
        asAdapterForProtocols = [IStreamFactory]
    )

    def __init__(self, ob, proto):
        self.sf = ob

    def checkResource(self):
        if self.sf.exists():
            return None

        return "Check failed"



class ManagedConnectionAsCheckableResource(object):

    protocols.advise(
        instancesProvide = [ICheckableResource],
        asAdapterForProtocols = [IManagedConnection]
    )

    def __init__(self, ob, proto):
        self.mc = ob

    def checkResource(self):
        try:
            self.mc.connection # reference it to ensure it's opened
            return None
        except:
            return ''.join(traceback.format_exception(*sys.exc_info()))

        return "Check failed"






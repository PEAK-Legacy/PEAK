from peak.api import *
from interfaces import IAdaptiveTask
from time import time

__all__ = [
    'AdaptiveTask'
]

class AdaptiveTask(binding.Component):

    """Periodic task that adapts its polling interval based on its workload"""

    __implements__ = IAdaptiveTask

    pollInterval = binding.bindTo('minimumIdle')

    runEvery = binding.requireBinding("Number of seconds between invocations")

    minimumIdle = binding.bindTo('runEvery')
    increaseIdleBy = 0
    multiplyIdleBy = 1

    # Maximum idle defaults to increasing three times
    maximumIdle = binding.Once(
        lambda s,d,a: s.runEvery * s.multiplyIdleBy**3 + s.increaseIdleBy*3
    )

    __ranLastTime = True













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
                pi = max(pi + self.increaseIdleBy, self.maximumIdle)
                self.pollInterval = pi

            self.__ranLastTime = didWork

        return didWork





    def getWork(self):
        """Find something to do, and return it"""
        pass


    def doWork(self,job):
        """Do the job; throw errors if unsuccessful"""
        LOG_DEBUG(`job`, self)
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












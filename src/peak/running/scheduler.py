"""System-wide task scheduler"""

from peak.api import *
from interfaces import *
from bisect import insort_left
from time import time



































class ReactorBasedScheduler(binding.Component):

    __implements__ = ISystemScheduler

    lastActivity = runningSince = None
    stayAliveFor = 0
    shutDownAfter = 0
    shutDownIfIdleFor = 0

    activeTasks = binding.New(list)

    stop = callLater = binding.delegateTo('reactor')

    reactor = binding.bindTo('import:twisted.internet.reactor')

    def addPeriodic(ptask):
        """Add 'ptask' to the prioritized processing schedule"""
        insort_left(self.activeTasks, ptask)    # round-robins if same priority
        self._scheduleProcessing()  # ensure that we'll be called

    def run():
        """Loop polling for IO or GUI events and calling scheduled funcs"""

        self.lastActivity = self.runningSince = time()

        try:
            if self.shutdownAfter:
                self.callLater(self.shutdownAfter, self.stop)

            if self.shutDownIfIdleFor:
                self.callLater(self.stayAliveFor, self._checkIdle)

            self.reactor.run()

        finally:
            del self.lastActivity, self.runningSince

    def activityOccurred():
        self.lastActivity = time()


    def _checkIdle(self):

        # Check whether we've been idle long enough to stop
        idle = time() - self.lastActivity
        
        if idle >= self.shutDownIfIdleFor:
            self.stop()

        else:
            # reschedule check for the earliest point at which
            # we could have been idle for the requisite amount of time
            self.callLater(self.shutDownIfIdleFor - idle, self._checkIdle)
            
            
    def _processNextTask(self):

        # Processes the highest priority pending task
        
        del self._scheduled

        try:
            task = self.activeTasks.pop()  # Highest priority task

            try:
                if task():
                    # It did something, make note of it
                    self.activityOccurred()
                    
            except exceptions.StopRunning:               
                pass    # Don't reschedule the task

            except:
                self.callLater(task.pollInterval, self.addPeriodic, task)
                raise

            else:
                self.callLater(task.pollInterval, self.addPeriodic, task)

        finally:
            self._scheduleProcessing()

    _scheduled = False

    def _scheduleProcessing(self):

        if self._scheduled or not self.activeTasks:
            return
            
        self._scheduled = self.callLater(0, self._processNextTask) or True














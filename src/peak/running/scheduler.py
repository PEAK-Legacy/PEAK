"""Periodic task scheduler"""

from peak.api import *
from interfaces import *
from bisect import insort_left
from time import time



































class ReactorBasedScheduler(binding.Component):

    __implements__ = ITaskScheduler

    lastActivity = runningSince = None
    stayAliveFor = 0
    shutDownAfter = 0
    shutDownIfIdleFor = 0

    activeTasks = binding.New(list)

    callLater = binding.delegateTo('reactor')

    reactor = binding.bindTo('import:twisted.internet.reactor')

    def addPeriodic(self,ptask):
        """Add 'ptask' to the prioritized processing schedule"""
        insort_left(self.activeTasks, ptask)    # round-robins if same priority
        self._scheduleProcessing()  # ensure that we'll be called

    def run(self):
        """Loop polling for IO or GUI events and calling scheduled funcs"""

        self.lastActivity = self.runningSince = time(); self._stopped = False
        self._scheduleProcessing()

        try:
            if self.shutDownAfter:
                self.callLater(self.shutDownAfter, self.stop)

            if self.shutDownIfIdleFor:
                self.callLater(self.stayAliveFor, self._checkIdle)

            self.reactor.run()

        finally:
            del self.lastActivity, self.runningSince

    def activityOccurred(self):
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

        didWork = cancelled = False

        try:

            task = self.activeTasks.pop()  # Highest priority task

            try:
                didWork = task()

            except exceptions.StopRunning:  # Don't reschedule the task               
                cancelled = True

        finally:
            if didWork:               
                self.activityOccurred() # did something; make note of it

            if not cancelled:
                self.callLater(task.pollInterval, self.addPeriodic, task)

            self._scheduleProcessing()

    _stopped = _scheduled = False

    def _scheduleProcessing(self):

        if self._scheduled or not self.activeTasks or self._stopped:
            return
            
        self._scheduled = self.callLater(0, self._processNextTask) or True


    def stop(self):
        self._stopped = True
        self.reactor.stop()

    











"""System-wide task scheduler"""

from peak.api import *
from interfaces import *
from bisect import insort
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
        self.callLater(0, self._processNextTask)

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

        if time() > self.lastActivity + self.shutDownIfIdleFor:
            self.stop()
        else:
            self.callLater(self.shutDownIfIdleFor, self._checkIdle)
            
            
    def _processNextTask(self):

        task = self.activeTasks.pop()  # Highest priority task

        try:
            if task():
                # It did something, make note of it
                self.activityOccurred()
                
        except exceptions.StopRunning:
            # Don't reschedule the task
            return
            
        self.callLater(task.pollInterval, self.addPeriodic, task)

















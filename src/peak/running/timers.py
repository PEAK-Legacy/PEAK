from peak.api import *

__all__ = [
    'ITimerService', 'ITimer', 'ITimeListener', 'TimerStateError'
]


class TimerStateError(Exception):
    """Timer operations invoked in improper sequence"""


class ITimerService(protocols.Interface):

    def getTimer(key):
        """Return timer named by PropertyName 'key'"""

    def addListener(key,listener,events=['stop']):
        """Add listener for 'key' (may be wildcard) on 'events' (empty=all)"""


class ITimer(protocols.Interface):

    def start(**info):
        """Start timing after setting info (like 'reset(); resume()')"""

    def resume(**info):
        """Resume timing (i.e. don't reset) after adding info"""

    def reset():
        """Reset the timer to zero and clear info"""

    def stop(**info):
        """Stop timing"""

    def addInfo(**info):
        """Update info"""

    def addListener(listener,events=['stop']):
        """Add an 'ITimeListener' for 'events' (empty=all) of this timer"""


class ITimeListener(protocols.Interface):

    def __call__(service,key,event,info,elapsed=None,processor=None):
        """'event' occurred for timer 'key' of 'service'

        'event' is the name of the corresponding 'ITimer' method that was
        called.  Only '"stop"' and '"resume"' events supply the 'elapsed'
        and 'processor' measurements, corresponding to elapsed and CPU
        timings, respectively.
        """































class Timer(binding.Component):

    protocols.advise(
        instancesProvide=[ITimer]
    )

    key = binding.Require("PropertyName key of this timer")
    info = binding.Make(dict)
    listeners = binding.Make(dict)

    elapsed = binding.Obtain(
        PropertyName('peak.running.timers.elapsed'), uponAssembly=True
    )

    cpu     = binding.Obtain(
        PropertyName('peak.running.timers.cpu'), uponAssembly=True
    )

    lastCPU = lastElapsed = None
    accumCPU = accumElapsed = 0
    isRunning = False
    eventNames = 'start','resume','addInfo','reset','stop'

    def addListener(self, listener, events=['stop']):
        for event in events or self.eventNames:
            if event not in self.eventNames:
                raise exceptions.InvalidName("No such ITimer event: %r" % event)
            self.listeners.setdefault(event,[]).append(listener)

    def addInfo(self,**info):
        if self.isRunning:
            self.info.update(info); self._notify('addInfo')
        else:
            raise TimerStateError("addInfo() while not running", self)

    def reset(self):
        if self.isRunning:
            raise TimerStateError("reset() while running", self)
        map(self._delBinding,['info','lastCPU','lastElapsed','accumCPU','accumElapsed'])
        if self.listeners: self._notify('reset')

    def start(self,**info):
        if self.isRunning:
            raise TimerStateError("start() while already running", self)
        self.isRunning = True
        self.info = info
        if self.listeners:
            self._notify('start')
            self.accumCPU = self.accumElapsed = 0   #self.reset()
            self.lastCPU = self.cpu()
            self.lastElapsed = self.elapsed()

    def stop(self,**info):
        if self.isRunning:
            self.isRunning = False
            if self.listeners:
                self.accumCPU += self.cpu()-self.lastCPU
                self.accumElapsed += self.elapsed()-self.lastElapsed
                self.info.update(info)
                self._notify('stop',self.accumElapsed,self.accumCPU)
        else:
            raise TimerStateError("stop() while not running", self)

    def resume(self,**info):
        if self.isRunning:
            raise TimerStateError("resume() while already running", self)
        self.isRunning = True
        if self.listeners:
            self.info.update(info)
            self._notify('resume',self.accumElapsed,self.accumCPU)
            self.lastCPU = self.cpu()
            self.lastElapsed = self.elapsed()

    def _notify(self,event,elapsed=None,cpu=None):
        args = (
            self.getParentComponent(), self.key, event, self.info.copy(),
            elapsed, cpu
        )
        for listener in self.listeners.get(event,()):
            listener(*args)


class TimerService(binding.Component):

    protocols.advise(
        instancesProvide=[ITimerService]
    )

    timers = binding.Make('weakref.WeakValueDictionary')

    timerClass = binding.Obtain( config.FactoryFor(ITimer) )

    def getTimer(self,key):

        key = PropertyName(key)

        if not key.isPlain():
            raise exceptions.InvalidName(
                "%r is not a plain property name" % key
            )

        try:
            return self.timers[key]
        except KeyError:
            timer = self.timerClass(self, key=key)
            self.timers[key] = timer
            return timer

















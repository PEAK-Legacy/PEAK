from peak.api import *
from interfaces import *
from peak.util.EigenData import AlreadyRead
from weakref import ref

__all__ = [
    'Subscription', 'EventSource', 'OneShot', 'Queue', 'Value', 'State',
]

































class Subscription(object):

    """Simple subscription to an event source"""

    __slots__ = 'active','subscribed','source','callback'

    protocols.advise(
        instancesProvide=[ISubscription]
    )

    def __init__(self,source,callback):
        self.source = source
        self.callback = callback
        source.addCallback(self)
        self.active = self.subscribed = True

    def __call__(self):
        self.subscribed = False
        if self.active:
            self.callback()
            self.source.addCallback(self)
            self.subscribed = True

    def pause(self):
        self.active = False

    def resume(self):
        self.active = True
        if not self.subscribed:
            self.source.addCallback(self)
            self.subscribed = True










class EventSource(object):

    __slots__ = '_callbacks'

    protocols.advise(
        instancesProvide=[IEventSource]
    )

    def __init__(self):
        self._callbacks = []

    def shouldSuspend(self, thread):
        self.addCallback(thread.run)
        return True

    def addCallback(self,func):
        self._callbacks.append(func)

    def addSubscriber(self,func):
        return Subscription(self,func)

    def fire(self,count=None):
        """Fire the event (not usually invoked directly in subclasses)

        If the optional 'count' is supplied, it requests that no more than
        'count' directly registered callbacks be invoked."""

        callbacks,self._callbacks = self.callbacks, []
        if count is not None and count<len(callbacks):
            self._callbacks[0:0] = callbacks[count:]
            callbacks = callbacks[:count]
        try:
            while callbacks:
                callbacks.pop(0)()
        except:
            # Restore unexecuted callbacks (not counting the one that failed)
            self._callbacks[0:0] = callbacks

            # ...and let the caller figure out what the heck to do about it!
            raise

class OneShot(EventSource):

    """Event that can be fired only once"""

    __slots__ = '_fired'

    def __init__(self):
        self._fired = False
        super(OneShot,self).__init__()


    def fire(self):
        if self._fired:
            raise AlreadyRead("OneShot can be fired only once")
        self._fired = True
        super(OneShot,self).fire()


    def addCallback(self,func):
        if not self._fired:
            super(OneShot,self).addCallback(func)




















class Queue(EventSource):

    __slots__ = 'buffer', 'closed', 'readersWaiting', '_triggering'

    protocols.advise(
        instancesProvide=[IValue]
    )

    def __init__(self):
        self.buffer = []
        self.closed = False
        self.readersWaiting = State(False)
        super(Queue,self).__init__()

    def put(self,ob):
        if self.closed:
            raise AlreadyRead
        else:
            self.buffer.append(ob)
            self.fire()

    def push(self,ob):
        if self.closed:
            raise AlreadyRead
        else:
            self.buffer.insert(0,ob)
            self.fire()

    def next(self):
        if self.buffer:
            item = self.buffer.pop(0)
            if self._callbacks and not self.buffer:
                self.readersWaiting.set(True)
            return item
        elif self.closed:
            raise StopIteration
        else:
            # Buffer underflow!
            raise AlreadyRead


    def close(self):
        self.closed = True

    def __iter__(self):
        return self


    def shouldSuspend(self,thread):
        if self.buffer:
            return False    # don't suspend if data is available
        else:
            self.addCallback(thread.enable)
            return True


    def addCallback(self,func):
        if self.buffer:
            func()  # data's available, so go ahead
        else:
            super(Queue,self).addCallback(func)
            self.readersWaiting.set(True)


    def fire(self, count=1):
        super(Queue,self).fire(count)
        self.readersWaiting.set(len(self._callbacks)>len(self.buffer))















class Value(EventSource):

    __slots__ = 'value'

    protocols.advise(
        instancesProvide=[IValue]
    )

    def __init__(self,value=NOT_GIVEN):
        self.value = value
        super(Value,self).__init__()

    def set(self,value):
        self.value = value
        self.fire()

    def __call__(self):
        return self.value

    def asQueue(self):

        queue = Queue()

        def put():
            queue.put(self.value)   # XXX weakref + handle closed queue!

        self.addSubscriber(put)
        return queue


    def when(condition=lambda v:v):
        """'IEventSource' that triggers when 'condition(value)' is true"""
        raise NotImplementedError   # XXX return Condition(condition,self)

    def equals(val):
        """'IEventSource' that triggers when value is set to 'val'"""
        raise NotImplementedError   # XXX return Condition(lambda v: v==val,self)




class State(Value):

    __slots__ = ()

    protocols.advise( instancesProvide=[IState] )

    def set(self,value):
        if value<>self.value:
            super(State,self).set(value)

































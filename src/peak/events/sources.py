from peak.api import *
from interfaces import *
from peak.util.EigenData import AlreadyRead

__all__ = [
    'Subscription', 'AbstractEventSource', 'Value', 'State', 'Queue',
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


class AbstractEventSource(object):

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

    def _trigger(self):
        callbacks,self._callbacks = self.callbacks, []
        try:
            while callbacks:
                callbacks.pop(0)()
        except:
            # Restore unexecuted callbacks (not counting the one that failed)
            self._callbacks[0:0] = callbacks

            # ...and let the caller figure out what the heck to do about it!
            raise









class Queue(AbstractEventSource):

    __slots__ = 'buffer', 'closed', 'readersWaiting'

    protocols.advise(
        instancesProvide=[IValue]
    )

    def __init__(self):
        self.buffer = []
        self.closed = False
        self.readersWaiting = State(False)
        super(Queue,self).__init__(self)


    def put(self,ob):
        if self.closed:
            raise AlreadyRead

        self.buffer.append(ob)
        if self._callbacks:
            self._callbacks.pop(0)()    # invoke only one callback per value
        else:
            # We now have more data than readers
            self.readersWaiting.set(False)


    def close(self):
        self.closed = True

    def __iter__(self):
        return self

    def addCallback(self,func):
        super(Queue,self).addCallback(func)
        if len(self._callbacks)>len(self.buffer):
            self.readersWaiting.set(True)




    def next(self):
        if self.buffer:
            item = self.buffer.pop(0)
            if len(self._callbacks)>len(self.buffer):
                self.readersWaiting.set(True)
            return item

        if self.closed:
            raise StopIteration
        else:
            # Buffer underflow!
            raise AlreadyRead





























class Value(AbstractEventSource):

    __slots__ = 'value'

    protocols.advise(
        instancesProvide=[IValue]
    )

    def __init__(self,value=NOT_GIVEN):
        self.value = value
        super(Value,self).__init__(self)

    def set(self,value):
        self.value = value
        self._trigger()

    def __call__(self):
        return self.value

    def asQueue(self):

        queue = Queue()

        def put():
            queue.put(self.value)

        self.addSubscriber(put)
        return queue


class State(Value):

    __slots__ = ()

    protocols.advise( instancesProvide=[IState] )

    def set(self,value):
        if value<>self.value:
            super(State,self).set(value)



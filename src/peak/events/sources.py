from peak.core import protocols, adapt, NOT_GIVEN
from interfaces import *
from peak.util.EigenData import AlreadyRead
from weakref import ref

__all__ = [
    'AnyOf', 'Distributor', 'Value', 'Condition', 'Semaphore',
]

































class AnyOf(object):

    """Union of multiple event sources

    Example usage::

        timedOut = scheduler.timeout(30)
        untilSomethingHappens = events.AnyOf(stream.dataRcvd, timedOut)

        while not timedOut():
            yield untilSomethingHappens; src,evt = events.resume()
            if src is stream.dataRcvd:
                data = event
                print data

    'AnyOf' fires callbacks whenever any of its actual event sources fire (and
    allows threads to continue if any of its actual event sources allow it).
    The 'event' it supplies to its user is actually a '(source,event)' tuple
    as shown above, so you can distinguish which of the actual event sources
    fired, as well as receive the event from it.

    Note that callbacks registered with an 'AnyOf' instance will fire at most
    once, even if more than one of the original event sources fires.  Thus,
    you should not assume in a callback or thread that the event you received
    is the only one that has occurred.  This is especially true in scheduled
    threads, where many things may happen between the triggering of an event
    and the resumption of a thread that was waiting for the event.
    """

    __slots__ = '_sources'

    protocols.advise(
        instancesProvide=[IEventSource]
    )







    def __new__(klass, *sources):
        if len(sources)==1:
            return adapt(sources[0],IEventSource)
        elif sources:
            self =object.__new__(klass)
            self._sources = adapt(sources, protocols.sequenceOf(IEventSource))
            return self

        raise ValueError, "AnyOf must be called with one or more IEventSources"


    def nextAction(self, thread=None, state=None):
        """See 'events.ITaskSwitch.nextAction()'"""

        for source in self._sources:
            action = source.nextAction()

            if action:
                flag = source.nextAction(thread,state)

                if state is not None:
                    state.YIELD( (source,state.lastEvent) )
                return flag

        if thread is not None:
            self.addCallback(thread.step)


    def addCallback(self,func):
        """See 'events.IEventSource.addCallback()'"""

        unfired = [True]
        def onceOnly(source,event):
            if unfired:
                unfired.pop()
                return func(self, (source,event))

        for source in self._sources:
            source.addCallback(onceOnly)


class Distributor(object):

    """Sends each event to one callback

    This is perhaps the simplest possible 'IEventSource'.  When its 'send()'
    method is called, the supplied event is passed to any registered
    callbacks.  As soon as a callback "accepts" the event (by returning a true
    value), distribution of the event stops.

    Yielding to an 'events.Distributor' in a thread always suspends the thread
    until the next 'send()' call on the distributor.

    You may subclass this class to create other kinds of event sources: change
    the 'singleFire' class attribute to 'False' in your subclass if you would
    like for events to be broadcast to all callbacks, whether they accept or
    reject the event.
    """

    __slots__ = '_callbacks'

    singleFire = True

    protocols.advise(
        instancesProvide=[IEventSource]
    )

    def __init__(self):
        self._callbacks = []


    def nextAction(self, thread=None, state=None):
        """See 'events.ITaskSwitch.nextAction()'"""
        if thread is not None:
            self.addCallback(thread.step)


    def addCallback(self,func):
        """See 'events.IEventSource.addCallback()'"""
        self._callbacks.append(func)


    def send(self,event):
        """Send 'event' to one or more callbacks, as needed

        Note that this method is *not* part of 'IEventSource', and is therefore
        not part of the API of 'Distributor' subclasses, unless they explicitly
        state otherwise.
        """

        callbacks, self._callbacks = self._callbacks, []
        count = len(callbacks)

        try:
            if self.singleFire:
                while count:
                    if callbacks.pop(0)(self,event):
                        return
                    count -= 1
            else:
                while count:
                    callbacks.pop(0)(self,event)
                    count -= 1

        finally:
            self._callbacks[0:0] = callbacks      # put back unfired callbacks

















class Value(Distributor):

    """Broadcast changes in a variable to all observers

    'events.Value()' instances implement a near-trivial version of the
    'Observer' pattern: callbacks can be informed that a change has been
    made to the 'Value'.  Example::

        aValue = events.Value(42)
        assert aValue()==42
        aValue.set(78)  # fires any registered callbacks
        aValue.set(78)  # doesn't fire, value hasn't changed
        aValue.set(78,force=True)   # force firing even though value's the same

    Events are broadcast to all callbacks, whether they "accept" or "reject"
    the event, and threads yielding to a 'Value' are suspended until the next
    event is broadcast.  The current value of the 'Value' is supplied to
    callbacks and threads via the 'event' parameter, and the 'Value' itself
    is supplied as the 'source'.  (See 'events.IEventSink'.)
    """

    __slots__ = 'value'

    protocols.advise(
        instancesProvide=[IWritableSource]
    )

    defaultValue = NOT_GIVEN
    singleFire   = False

    def __init__(self,value=NOT_GIVEN):
        if value is NOT_GIVEN:
            value = self.defaultValue
        self.value = value
        super(Value,self).__init__()






    def set(self,value,force=False):
        """See 'events.IWritableSource.set()'"""
        if force or value<>self.value:
            self.value = value
            self.send(value)


    def __call__(self):
        """See 'events.IReadableSource.__call__()'"""
        return self.value































class Condition(Value):

    """Send callbacks/allow threads to proceed when condition is true

    A 'Condition' is very similar to a 'Value', except in its yielding and
    callback behavior.  Yielding to a 'Condition' in a thread will suspend the
    thread *only* if the current value of the 'Condition' is false.  If the
    'Condition' has a true value, the thread is allowed to proceed, and
    'events.resume()' will return the value of the 'Condition'.  If the
    'Condition' has a false value, the thread will be suspended until
    the value is changed to a true one.

    The behavior for callbacks is similar: when a callback is added with
    'addCallback()', it will be fired immediately if the 'Condition' is true
    at the time the callback is added.  Otherwise, the callback will be fired
    once the 'Condition' becomes true.
    """

    __slots__ = ()

    protocols.advise( instancesProvide=[ICondition] )

    defaultValue = False

    def nextAction(self, thread=None, state=None):
        """See 'events.ITaskSwitch.nextAction()'"""

        if self.value:
            if state is not None:
                state.YIELD(self.value)
            return True

        if thread is not None:
            self.addCallback(thread.step)







    def set(self,value,force=False):
        """See 'events.IWritableSource.set()'"""

        old = self.value
        self.value = value
        if force or (value and not old):
            self.send(value)


    def addCallback(self, func):
        """See 'events.IEventSource.addCallback()'"""

        if self.value:
            func(self,self.value)
        else:
            super(Condition,self).addCallback(func)

























class Semaphore(Condition):

    """Allow up to 'n' threads to proceed simultaneously

    A 'Semaphore' is like a 'Condition', except that it does not broadcast
    its events.  Each event is supplied to callbacks only until one "accepts"
    the event (by returning a true value).

    'Semaphore' instances also have 'put()' and 'take()' methods that
    respectively increase or decrease their value by 1.

    Note that 'Semaphore' does not automatically decrease its count due to
    a callback or thread resumption.  You must explicitly 'take()' the
    semaphore in your thread or callback to reduce its count.
    """

    __slots__ = ()

    protocols.advise( instancesProvide=[ISemaphore] )

    singleFire   = True
    defaultValue = 0

    def put(self):
        """See 'events.ICondition.put()'"""
        self.set(self.value+1)

    def take(self):
        """See 'events.ICondition.take()'"""
        self.set(self.value-1)












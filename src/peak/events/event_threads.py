from peak.api import *
from interfaces import *
from types import GeneratorType
from sys import exc_info
import traceback
from sources import State

__all__ = ['resume', 'Thread']


no_exc = None, None, None

def resume():
    if exc_info()<>no_exc:
        try:
            t,v,tb = sys.exc_info()
            raise t,v,tb
        finally:
            t=v=tb=None


class GeneratorAsTaskSwitch(protocols.Adapter):

    protocols.advise(
        instancesProvide=[ITaskSwitch],
        asAdapterForTypes=[GeneratorType]
    )

    def shouldSuspend(self,thread):
        thread.schedule(self.subject)
        return False










class Thread(object):

    protocols.advise(
        instancesProvide=[IThread]
    )

    def __init__(self):
        self.stack = []
        self.schedule = self.stack.append
        self.isFinished = State(False)


    def run(self, iterator=None):
        stack = self.stack
        if iterator is not None:
            stack.append(iterator)

        while stack:
            try:
                switch = stack[-1].next()
            except StopIteration:
                stack.pop() # No switch, so topmost iterator is finished
                continue    # resume the next iterator down, or finish
            except:
                # Remove the current iterator, since it can't be resumed
                stack.pop()

                if stack:
                    continue    # delegate the error to the next iterator
                else:
                    # nobody to delegate to, pass the buck to our caller  :(
                    raise   # XXX doesn't set isFinished

            try:
                if adapt(switch,ITaskSwitch).shouldSuspend(self):
                    return
            except:
                continue    # push the error back into the current iterator

        self.isFinished.set(True)


"""DEPRECATED: Push/pop signal managers with SIGWHATEVER() methods"""

__all__ = ['pushSignals', 'popSignals']

def pushSignals(manager):

    """Add signal manager 'manager' to top of signal handling stack

    When a signal occurs, the signal stack is searched for a signal manager
    that has a method named for the signal, e.g. a 'SIGTERM' method if the
    signal is 'SIGTERM'.  The first method found is called.  If no signal
    manager defines such a method, the platform-default handling is used.
    To remove a signal manager from the stack, use 'popSignals()'.

    Note that the actual implementation is such that the "search" for valid
    signal-handling methods is done when 'pushSignals()' is called, not when
    the signal occurs."""

    save = {}
    signalStack.append(save)

    try:
        for name,number in signals.items():
            if hasattr(manager,name):
                save[number] = signal(number,getattr(manager,name))
    except:
        popSignals()    # undo settings made as of when the error occurred
        raise


def popSignals():

    """Remove/return topmost signal manager, or 'None' if the stack is empty"""

    if signalStack:
        manager = signalStack.pop()
        for number,handler in manager.items():
            signal(number,handler)
        return manager


try:
    import signal

except ImportError:
    signal = lambda *args: None
    signals = {}

else:
    signals = dict(
        [(name,number)
            for (name,number) in signal.__dict__.items()
                if name.startswith('SIG') and not name.startswith('SIG_')
        ]
    )
    signal = signal.signal

signalStack = []

























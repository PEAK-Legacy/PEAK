"""Threading-related utilities

    This module provides a degree of platform independence for thread support.
    At the moment, it only really provides conditional 'allocate_lock()' and
    'get_ident()' functions, but other API's may be added in the future.

    By default, this module will use thread support if it is available.  You
    can override this, however, by using the 'disableThreading()',
    'allowThreading()', or 'requireThreading()' API function, preferably at the
    start of your program before any other modules have a chance to use any
    of this module's APIs.
"""

__all__ = [
    'allocate_lock', 'get_ident', 'DummyLock'
    'allowThreading', 'disableThreading', 'requireThreading',
]

try:
    import thread
except ImportError:
    HAVE_THREADS = False
else:
    HAVE_THREADS = True


# default is to 'allowThreading'

USE_THREADS = HAVE_THREADS


if HAVE_THREADS:
    from thread import get_ident
else:
    def get_ident(): return 1






def allowThreading():

    """Enable the use of real thread locks, if possible"""

    global USE_THREADS
    USE_THREADS = HAVE_THREADS


def disableThreading():

    """Don't use threads, even if we have them.

    Note that this must be called *before* any locks have been allocated, as it
    only affects subsequent allocations."""
    
    global USE_THREADS
    USE_THREADS = False


def requireThreading():

    """Raise RuntimeError if threads aren't available; otherwise enable them"""

    if not HAVE_THREADS:
        raise RuntimeError, "Threads required but not available"

    self.allowThreading()













    
class DummyLock(object):

    """Dummy lock type used when threads are inactive or unavailable"""

    __slots__ = ['_lockCount']   

    def __init__(self):
        self._lockCount = 0
        

    def acquire(self, *waitflag):

        lc = self._lockCount = self._lockCount + 1

        if lc==1:
            if waitflag:
                # an argument was supplied, return success
                return 1
            else:
                # no argument, just return None
                return None
                
        else:
            self._lockCount -= 1
            
            if waitflag and not waitflag[0]:
                # no-wait; unlock/return failure
                return 0

            raise RunTimeError(
                "Attempt to double-lock a lock in a single-threaded program"
            )

            
    def release(self):
        self._lockCount -= 1

    def locked(self):
        return self._lockCount and True or False


def allocate_lock():

    """Returns either a real or dummy thread lock, depending on availability"""

    if USE_THREADS:
        return thread.allocate_lock()

    else:
        return DummyLock()





    

"""
Lockfiles

These are used for synchronization between processes, unlike
thread.LockType locks.  The common use is non-blocking lock attempts. 
For convenience and in order to reduce confusion with the (somewhat odd)
thread lock interface, these locks have a different interface.

    attempt()   try to obtain the lock, return boolean success
    obtain()    wait to obtain the lock, returns None
    release()   release an obtained lock, returns None
    locked()    returns True if any thread IN THIS PROCESS
                has obtained the lock, else False
"""

__all__ = ['LockFile', 'SHLockFile', 'FLockFile']

import os, errno, string, time
from peak.util.threads import allocate_lock






















class LockFileBase:

    """Common base for lockfiles"""
    
    def __init__(self, fn):
        self.fn = os.path.abspath(fn)
        self._lock = allocate_lock()
        self._locked = False

    def attempt(self):
        if self._lock.acquire(False):
            r = 0
            try:
                r = self.do_acquire(0)
            finally:
                if not r and self._lock.locked():
                    self._lock.release()
            return r
        else:
            return False
    
    def obtain(self):
        self._lock.acquire()
        r = 0
        try:
            r = self.do_acquire(1)
        finally:
            if not r and self._lock.locked():
                self._lock.release()
        if not r:
            raise RuntimeError, "lock obtain shouldn't fail!"
    
    def release(self):
        self.do_release()
        self._locked = False
        self._lock.release()

    def locked(self):
        return self._locked


### Posix-y lockfiles ###

try:
    import posix; from posix import O_EXCL, O_CREAT, O_RDWR
except:
    posix=None

try:
    import fcntl
except:
    fcntl = None
        

def pid_exists(pid):
    """Is there a process with PID pid?"""
    if pid < False:
        return False
    
    exist = False
    try:
        os.kill(pid, 0)
        exist = 1
    except OSError, x:
        if x.errno != errno.ESRCH:
            raise
   
    return exist














def check_lock(fn):
    """Check the validity of an existing lock file

    Reads the PID out of the lock and check if that process exists"""

    try:
        f = open(fn, 'r')
        pid = int(string.strip(f.read()))
        f.close()
        return pid_exists(pid)
    except:
        raise
        return 1 # be conservative


def make_tempfile(fn, pid):
    tfn = os.path.join(os.path.dirname(fn), 'shlock%d' % pid)

    errcount = 1000
    while 1:
        try: 
            fd = posix.open(tfn, O_EXCL | O_CREAT | O_RDWR, 0600)
            posix.write(fd, '%d\n' % pid)
            posix.close(fd)

            return tfn
        except OSError, x:
            if (errcount > 0) and (x.errno == errno.EEXIST):
                os.unlink(tfn)
                errcount = errcount - 1
            else:
                raise









class SHLockFile(LockFileBase):
    """
    HoneyDanBer/NNTP/shlock(1)-style locking

    Two bigs wins to this algorithm:

      o Locks do not survive crashes of either the system or the
        application by any appreciable period of time.

      o No clean up to do if the system or application crashes.
   
    Loses:

      o In the off chance that another process comes along with
        the same pid, we can get a false positive for lock validity. 

      o Not compatible with NFS or any shared filesystem
        (due to disjoint PID spaces)

      o Waiting for lock must be implemented by polling
    """

    def do_acquire(self, waitflag):
        if waitflag:
            sleep = 1
            locked = self.do_acquire(False)

            while not locked:
                time.sleep(sleep)
                sleep = min(sleep + 1, 15)
                locked = self.do_acquire(False)

            self._locked = locked
            return locked
        else:
            tfn = make_tempfile(self.fn, os.getpid())

            while 1:
                try:
                    os.link(tfn, self.fn)
                    os.unlink(tfn)
                    self._locked = 1
                    return 1
                except OSError, x:
                    if x.errno == errno.EEXIST:
                        if check_lock(self.fn):
                            os.unlink(tfn)
                            self._locked = False
                            return False
                        else:
                            # nuke invalid lock file, and try to lock again
                            os.unlink(self.fn)
                    else:
                        os.unlink(tfn)
                        raise
            

    def do_release(self):
        os.unlink(self.fn)























class FLockFile(LockFileBase):
    """
    flock(3)-based locks.

    Wins:

      o Locks do not survive crashes of either the system or the
        application.

      o Waiting for a lock is handled by the kernel and doesn't require
        polling

      o Potentially compatible with NFS or other shared filesystem
        _if_ you trust their lockd (or equivalent) implemenation.
        Note that this is a *big* if!

      o No false positives on stale locks

    Loses:

      o Leaves lockfiles around, since unlink would cause a race.
    """
    
    def do_acquire(self, waitflag=False):
        locked = False

        if waitflag:
            blockflag = 0
        else:
            blockflag = fcntl.LOCK_NB

        self.fd = posix.open(self.fn, O_CREAT | O_RDWR, 0600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX|blockflag)
            # locked it
            try:
                posix.ftruncate(self.fd, 0)
                posix.write(self.fd, `os.getpid()` + '\n')
                locked = True
            except:
                self.release()
                raise
        except IOError, x:
            if x.errno == errno.EWOULDBLOCK:
                # failed to lock
                posix.close(self.fd)
                del self.fd
            else:
                raise
 
        self._locked = locked
         
        return locked

    def do_release(self):
        posix.ftruncate(self.fd, 0)
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        posix.close(self.fd)
        del self.fd



# Default is shlock(1)-style if available
if posix:
    LockFile = SHLockFile
else:
    LockFile = FLockFile

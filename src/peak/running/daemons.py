from peak.binding.components import AutoCreated

from time import time, sleep
import sys

try:
    from signal import signal, getsignal, SIGTERM, SIGINT
    
except ImportError:
    # If we can't do signal stuff, fake it
    def signal(a,b): pass
    def getsignal(a): pass
    SIGTERM = SIGINT = None


__all__ = ['AbstractDaemon']

























class AbstractDaemon(AutoCreated):

    POLL_PERIOD = 0        # Minimum delay between an unsuccessful poll and the next one
    _nextpoll   = 0        # When's it okay to poll again?

    def __call__(self):

        """Do a unit of work, return true if anything worthwhile was done"""

        try:
            # Ensure we don't poll too often

            if self.POLL_PERIOD:
                if time()<self._nextpoll: return
                self._nextpoll = time()+self.POLL_PERIOD

            # Make sure we're locked while actually working

            if self.lockMe():
                try:
                    job = self.getWork()
                    if job: 
                        result = self.doWork(job)
                        if result:
                            if self.POLL_PERIOD: 
                                # Okay to try again if we did something
                                del self._nextpoll 
                            return result
                finally:
                    self.unlockMe()

        except (KeyboardInterrupt, SystemExit): raise
        #except MoveAlong,msg:      
        #   if msg: apply(self.log,msg)

        # Log errors if any
        #except:
        #    self.log.ALERT(sys.exc_info())



    HARD_LIFETIME  = 30 * 60    # Exit if this much time passes
    SOFT_LIFETIME  = 15 * 60    # How long till we exit when idle - 15 minutes default

    MIN_IDLE    = 10    # Sleep at least this long when idling
    MAX_IDLE    = 60    # Sleep at most this long when idling
    INC_IDLE    = 10    # Increase sleep time this much after each idle sleep

    def run(self):

        now=time()
        hard_death = now + self.HARD_LIFETIME
        soft_death = min(hard_death, now + self.SOFT_LIFETIME)

        idle = self.MIN_IDLE


        # XXX self.log.NOTICE("Beginning run")

        oldsigterm = signal(SIGTERM, getsignal(SIGINT))

        try:
            while 1:
    
                while self() and time()<hard_death:
                    idle = self.MIN_IDLE

                if time()+idle > soft_death: break

                # XXX self.log.DEBUG('Sleeping for %d seconds' % idle)
                
                sleep(idle)
                idle = min(idle + self.INC_IDLE, self.MAX_IDLE)

            # XXX self.log.NOTICE("Finished run")

        finally:
            signal(SIGTERM,oldsigterm)




    def getWork(self):
        """Find something to do, and return it"""
        pass


    def doWork(self,job):
        """Do the job; throw errors if unsuccessful"""
        # XXX self.log.DEBUG(`job`)
        return job


    def lockMe(self): 
        """Try to begin critical section for doing work, return true if successful"""

        lock = self.lock

        if lock:
            return self.lock.attempt()

        return True


    def unlockMe(self): 
        """End critical section for doing work"""

        lock = self.lock
        if lock: lock.release()


    lock = None











class MultiDaemon(AbstractDaemon):

    """Daemon that makes other daemons do the actual work"""

    start = 0
    prioritized = False     # True = reset to top of list when finding work

    def getWork(self):

        daemons = self.getDaemons()

        if not daemons:
            return
        
        if self.prioritized:
            start = now = 0
        else:
            start = now = self.start % len(daemons)

        job=None

        while not job:
            # XXX self.log.DEBUG('Checking %d of %d daemons' % (now + 1, len(daemons)))

            daemon = daemons[now]
            job = daemon()
            now = (now +1) % len(daemons)

            if now==start:
                # we're back to beginning, so nobody had anything to do
                break

        self.start = now
        return job


    def doWork(self, job):
        return job



    daemons = ()

    seed = None

    def getDaemons(self):
    
        if self.seed:

            spawn = self.seed()

            if spawn:
                self.daemons = spawn

        return self.daemons




"""Pre-forking process supervisor for FastCGI and other server-like apps"""

from peak.api import *
from interfaces import *
from peak.running.commands import EventDriven, Bootstrap
from peak.running.process import signals, signal_names
from shlex import shlex
from cStringIO import StringIO

def tokenize(s):
    return list(iter(shlex(StringIO(s)).get_token,''))

def unquote(s):
    if s.startswith('"') or s.startswith("'"):
        s = s[1:-1]
    return s

























class ProcessSupervisor(EventDriven):

    log           = binding.Obtain('logging.logger:supervisor')

    pidFile       = binding.Require("Filename where process ID is kept")
    minChildren   = 1
    maxChildren   = 4
    startInterval = 15  # seconds between forks
    importModules = ()  # Placeholder for ZConfig pre-import hook; see schema

    cmdText = ""        # String form of subprocess command line

    cmdLine = binding.Make(
        lambda self: [
            unquote(x) for x in tokenize(self.cmdText)
        ]+self.argv[1:]
    )

    template = binding.Make(
        lambda self: self.getSubcommand(
            Bootstrap,
            argv = ['supervise'] + self.cmdLine,
            parentComponent = config.makeRoot(),
        ),
        adaptTo=running.IProcessTemplate,
        offerAs=[running.IProcessTemplate],
        suggestParent=False
    )

    startLockURL = binding.Make(
        lambda self: "flockfile:%s.start" % self.pidFile
    )

    pidLockURL = binding.Make(
        lambda self: "flockfile:%s.lock" % self.pidFile
    )





    startLock = binding.Make(
        lambda self: self.lookupComponent(self.startLockURL),
        adaptTo = running.ILock
    )

    pidLock = binding.Make(
        lambda self: self.lookupComponent(self.pidLockURL),
        adaptTo = running.ILock
    )

    lastStart = None    # last time a fork occurred
    nextStart = None    # next scheduled fork

    processes = binding.Make(dict)
    plugins   = binding.Make(list)

    reactor = binding.Make(
        # Can't use Make(IBasicReactor), because 'getReactor()' is a singleton
        'peak.running.scheduler:UntwistedReactor',
        offerAs=[running.IBasicReactor]
    )

    mainLoop = binding.Make(running.IMainLoop, offerAs=[running.IMainLoop])

    taskQueue = binding.Make(running.ITaskQueue, offerAs=[running.ITaskQueue])

    _no_twisted = binding.Require(
        "ProcessSupervisor subcomponents may not depend on Twisted",
        offerAs = [running.ITwistedReactor]
    )

    import os

    from time import time

    def setup(self):
        self.log.debug("Beginning setup")
        template = adapt(self.template, ISupervisorPluginProvider, None)
        if template is not None:
            self.plugins.extend(template.getSupervisorPlugins(self))

    def _run(self):

        if not self.startLock.attempt():
            self.log.warning("Another process is in startup; exiting")
            return 1        # exit with errorlevel 1

        try:
            self.setup()
            self.killPredecessor()
            self.writePidFile()
        finally:
            self.startLock.release()

        self.startIfTooFew()

        retcode = super(ProcessSupervisor,self)._run()

        if adapt(retcode,running.IExecutable,None) is not None:
            # child process, drop out to the trampoline
            return retcode

        self.killProcesses()
        self.removePidFile()

        return retcode


    def requestStart(self):
        if self.nextStart is None:
            if self.lastStart is None:
                self.nextStart = self.time()
            else:
                self.nextStart = max(
                    self.lastStart + self.startInterval, self.time()
                )
            delay = self.nextStart-self.time()
            self.log.debug("Scheduling child start in %.1d seconds",delay)
            self.mainLoop.activityOccurred()
            self.reactor.callLater(delay, self._doStart)


    def _doStart(self):

        if len(self.processes)>=self.maxChildren:
            return

        proxy, stub = self.template.spawn(self)

        if proxy is None:
            del self.processes  # we're the child, so give up custody
            self.mainLoop.childForked(stub)
            return

        self.mainLoop.activityOccurred()
        self.log.debug("Spawned new child process (%d)", proxy.pid)
        proxy.addListener(self._childChange)
        self.processes[proxy.pid] = proxy

        for plugin in self.plugins:
            plugin.processStarted(proxy)

        self.lastStart = self.time()
        self.nextStart = None

        # We might not be up to our minimum yet
        self.startIfTooFew()


    def killProcesses(self):
        self.log.debug("Killing child processes")
        for pid,proxy in self.processes.items():
            proxy.sendSignal('SIGTERM')


    def startIfTooFew(self):
        if len(self.processes)<self.minChildren:
            self.requestStart()





    def _childChange(self,proxy):

        self.mainLoop.activityOccurred()

        if proxy.isFinished:

            if proxy.exitedBecause:
                self.log.warning(
                    "Child process %d exited due to signal %d (%s)",
                    proxy.pid, proxy.exitedBecause,
                    signal_names.setdefault(proxy.exitedBecause,('?',))[0]
                )
            elif proxy.exitStatus:
                self.log.warning(
                    "Child process %d exited with errorlevel %d",
                    proxy.pid, proxy.exitStatus
                )
            else:
                self.log.debug("Child process %d has finished", proxy.pid)

            del self.processes[proxy.pid]

            self.startIfTooFew()

        elif proxy.stoppedBecause:
            self.log.error("Child process %d stopped due to signal %d (%s)",
                proxy.pid, proxy.stoppedBecause,
                signal_names.getdefault(proxy.stoppedBecause,('?',))[0]
            )

        elif proxy.isStopped:
            self.log.error("Child process %d has stopped", proxy.pid)









    def writePidFile(self):
        self.pidLock.obtain()
        try:
            pf = open(self.pidFile,'w')
            pf.write('%d\n' % self.os.getpid())
            pf.close()
        finally:
            self.pidLock.release()


    def readPidFile(self, func):
        self.pidLock.obtain()
        try:
            if self.os.path.exists(self.pidFile):
                pf = open(self.pidFile,'r')
                func(int(pf.readline().strip()))
                pf.close()
        finally:
            self.pidLock.release()


    def removePidFile(self):

        def removeIfMe(pid):
            if pid==self.os.getpid():
                self.log.debug("Unlinking %s", self.pidFile)
                self.os.unlink(self.pidFile)

        self.readPidFile(removeIfMe)

    def killPredecessor(self):

        def doKill(pid):
            try:
                self.log.debug("Killing predecessor (process #%d)", pid)
                self.os.kill(pid,signals['SIGTERM'])
            except:
                pass # XXX

        self.readPidFile(doKill)


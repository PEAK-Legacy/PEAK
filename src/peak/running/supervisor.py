"""Pre-forking process supervisor for FastCGI and other server-like apps"""

from peak.api import *
from interfaces import *
from peak.net.interfaces import IListeningSocket
from commands import EventDriven, Bootstrap, AbstractInterpreter
from process import signals, signal_names, ChildProcess, AbstractProcessTemplate
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
        adaptTo=IProcessTemplate,
        offerAs=[IProcessTemplate],
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
        adaptTo = ILock
    )

    pidLock = binding.Make(
        lambda self: self.lookupComponent(self.pidLockURL),
        adaptTo = ILock
    )

    lastStart = None    # last time a fork occurred
    nextStart = None    # next scheduled fork

    processes = binding.Make(dict)
    plugins   = binding.Make(list)

    reactor = binding.Make(
        'peak.running.scheduler:UntwistedReactor', offerAs=[IBasicReactor]
    )
    mainLoop = binding.Make(
        'peak.running.scheduler.MainLoop', offerAs=[IMainLoop]
    )
    taskQueue = binding.Make(
        'peak.running.daemons.TaskQueue', offerAs=[ITaskQueue]
    )

    _no_twisted = binding.Require(
        "ProcessSupervisor subcomponents may not depend on Twisted",
        offerAs = [ITwistedReactor]
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

        self.requestStart()

        retcode = super(ProcessSupervisor,self)._run()

        if adapt(retcode,IExecutable,None) is not None:
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
            self.reactor.callLater(delay, self._doStart)


    def _doStart(self):

        if len(self.processes)>=self.maxChildren:
            return

        proxy, stub = self.template.spawn(self)

        if proxy is None:
            self.mainLoop.childForked(stub)
            return

        self.log.debug("Spawned new child process (%d)", proxy.pid)
        proxy.addListener(self._childChange)
        self.processes[proxy.pid] = proxy

        for plugin in self.plugins:
            plugin.processStarted(proxy)

        self.lastStart = self.time()
        self.nextStart = None

        if len(self.processes)<self.minChildren:
            self.requestStart()


    def killProcesses(self):
        self.log.debug("Killing child processes")
        for pid,proxy in self.processes.items():
            proxy.sendSignal('SIGTERM')












    def _childChange(self,proxy):

        if proxy.isFinished:

            if proxy.exitedBecause:
                self.log.warning(
                    "Child process %d exited due to signal %d (%s)",
                    proxy.pid, proxy.exitedBecause,
                    signal_names.getdefault(proxy.exitedBecause,('?',))[0]
                )
            elif proxy.exitStatus:
                self.log.warning(
                    "Child process %d exited with errorlevel %d",
                    proxy.pid, proxy.exitStatus
                )
            else:
                self.log.debug("Child process %d has finished", proxy.pid)

            del self.processes[proxy.pid]

            if len(self.processes)<self.minChildren:
                self.requestStart()

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

class BusyProxy(ChildProcess):

    """Proxy for process that communicates its "busy" status"""
    log        = binding.Obtain('logging.logger:supervisor.busy-monitor')
    reactor    = binding.Obtain(IBasicReactor)
    busyStream = binding.Require("readable pipe from child")
    fileno     = binding.Obtain('busyStream/fileno')
    isBusy     = False

    def doRead(self):
        if self.isFinished:
            return

        try:
            # We need this try block because the pipe could close at any time
            byte = self.busyStream.read(1)
        except ValueError:
            # already closed
            return

        if byte=='+':
            self.log.debug("Child process %d is now busy", self.pid)
            self.isBusy = True
            self._notify()
        elif byte=='-':
            self.log.debug("Child process %d is now free", self.pid)
            self.isBusy = False
            self._notify()

    def _setStatus(self,status):
        super(BusyProxy,self)._setStatus(status)
        if self.isFinished:
            self.reactor.removeReader(self)
            self.busyStream.close()

    __onStart = binding.Make(
        lambda self: self.reactor.addReader(self),
        uponAssembly = True
    )


class BusyStarter(binding.Component):

    """Start processes for incoming connections if all children are busy"""

    children = binding.Make(dict)
    template = binding.Obtain(IProcessTemplate, suggestParent=False)
    stream   = binding.Obtain('./template/stdin')
    fileno   = binding.Obtain('./stream/fileno')
    reactor  = binding.Obtain(IBasicReactor)

    supervisor = binding.Obtain('..')

    def processStarted(self, proxy):
        proxy.addListener(self.statusChanged)
        self.children[proxy.pid] = proxy.isBusy
        self._delBinding('allBusy')

    def statusChanged(self, proxy):
        if not proxy.isRunning:
            if proxy.pid in self.children:
                del self.children[proxy.pid]
        else:
            self.children[proxy.pid] = proxy.isBusy

        self._delBinding('allBusy')

    allBusy = binding.Make(
        # not one is available
        lambda self: False not in self.children.values()
    )

    def doRead(self):
        if self.allBusy:
            self.supervisor.requestStart()

    __onStart = binding.Make(
        lambda self: self.reactor.addReader(self),
        uponAssembly = True
    )


class FCGITemplateCommand(AbstractInterpreter):

    """Command to process a socket URL + a FastCGI command to run on it"""

    def interpret(self, filename):

        stdin = self.lookupComponent(filename, adaptTo=IListeningSocket)
        parent = self.getCommandParent()

        return FastCGITemplate(
            stdin=stdin,
            command = self.getSubcommand(
                Bootstrap,
                parentComponent=parent,
                componentName  =self.commandName,
                stdin = stdin
            )
        )























class FastCGITemplate(AbstractProcessTemplate):

    """Process template for FastCGI subprocess w/busy monitoring"""

    protocols.advise(
        instancesProvide=[IRerunnableCGI, ISupervisorPluginProvider]
    )

    proxyClass = BusyProxy
    readPipes  = ('busyStream',)

    socketURL = binding.Require("URL of TCP or Unix socket to listen on")

    command   = binding.Require(
        "IRerunnableCGI command to run in subprocess", adaptTo=IRerunnableCGI,
        uponAssembly=True   # force creation to occur in parent process
    )

    stdin = binding.Make(
        lambda self: self.lookupComponent(self.socketURL),
        adaptTo = IListeningSocket
    )

    def runCGI(self, *args):
        self.busyStream.write('+')      # start being busy  (XXX trap errors)
        try:
            self.command.runCGI(*args)
        finally:
            self.busyStream.write('-')  # finish being busy  (XXX trap errors)

    def _redirect(self):
        self.os.dup2(self.stdin.fileno(),0) # XXX what does this do if 0,0?

    def _makeStub(self):
        from peak.running.commands import CGICommand
        return CGICommand(self, cgiCommand=self, stdin=self.stdin)

    def getSupervisorPlugins(self, supervisor):
        return [BusyStarter(supervisor, template=self, stream=self.stdin)]



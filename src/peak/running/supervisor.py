"""Pre-forking process supervisor for FastCGI and other server-like apps"""

from peak.api import *
from interfaces import *
from peak.net.interfaces import IListeningSocket
from commands import EventDriven, Bootstrap, AbstractInterpreter
from process import signals, ChildProcess, AbstractProcessTemplate
from shlex import shlex
from cStringIO import StringIO
































class ProcessSupervisor(EventDriven):

    # log         = logger (to where?)

    pidFile       = binding.Require("Filename where process ID is kept")
    minChildren   = 1
    maxChildren   = 4
    startInterval = 15  # seconds between forks
    importModules = ()  # Placeholder for ZConfig pre-import hook; see schema

    cmdText = binding.Require("String form of subprocess command line")

    cmdLine = binding.Make(
        lambda self: list(
            iter(shlex(StringIO(self.cmdLine)).get_token,'')
        )+self.argv[1:]
    )

    template = binding.Make(
        lambda self: self.getSubcommand(
            Bootstrap,
            argv = self.cmdLine,
            parentComponent = config.makeRoot(),
            componentName = self.commandName
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
        template = adapt(self.template, ISupervisorPluginProvider, None)
        if template is not None:
            self.plugins.extend(template.getSupervisorPlugins(self))



    def _run(self):

        if not self.startLock.attempt():
            # self.log.warn("Another process is starting")
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

            self.reactor.callLater(self.nextStart-self.time(), self._doStart)


    def _doStart(self):

        if len(self.processes)>=self.maxChildren:
            return

        self.lastStart = self.time()
        self.nextStart = None

        proxy, stub = self.template.spawn(self)
        if proxy is None:
            self.mainLoop.childForked(stub)
            return

        # XXX log started
        proxy.addListener(self._childChange)
        self.processes[proxy.pid] = proxy

        for plugin in self.plugins:
            plugin.processStarted(proxy)

        if len(self.processes)<self.minChildren:
            self.requestStart()


    def _childChange(self,proxy):
        if proxy.isFinished:
            # XXX log exited
            del self.processes[proxy.pid]


    def killProcesses(self):
        for pid,proxy in self.processes.items():
            proxy.sendSignal('SIGTERM')








    def writePidFile(self):
        self.pidLock.obtain()
        try:
            pf = open(self.pidFile,'w')
            pf.write('%d\n', self.os.getpid())
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
                self.os.unlink(self.pidFile)

        self.readPidFile(removeIfMe)


    def killPredecessor(self):

        def doKill(pid):
            try:
                self.os.kill(pid,signals['SIGTERM'])
            except:
                pass # XXX

        self.readPidFile(doKill)


class BusyProxy(ChildProcess):

    """Proxy for process that communicates its "busy" status"""

    reactor    = binding.Obtain(IBasicReactor)
    busyStream = binding.Require("readable pipe from child")
    fileno     = binding.Obtain('busyStream/fileno')
    isBusy     = False


    def doRead(self):
        byte = self.busyStream.read()[-1]
        if byte=='+':
            self.isBusy = True
            self._notify()
        elif byte=='-':
            self.isBusy = False
            self._notify()
        else:
            return


    def _setStatus(status):
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
            if proxy.pid in self.allChildren:
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
        self.busyStream.write('+')      # start being busy
        try:
            self.command.runCGI(*args)
        finally:
            self.busyStream.write('-')  # finish being busy

    def _redirect(self):
        self.os.dup2(self.stdin.fileno(),0)

    def makeStub(self):
        from peak.running.commands import CGICommand
        return CGICommand(self, cgiCommand=self, stdin=self.stdin)

    def getSupervisorPlugins(self, supervisor):
        return [BusyStarter(supervisor, template=self, stream=self.stdin)]



"""
Namespace Interactor
"""

from peak.api import *
from commands import *
from interfaces import *


class NamingInteractor(binding.Component):

    """A shell-like interactor for namespaces"""

    shell = binding.bindTo('..')
    width = binding.bindTo('shell/width')

    def interact(self, object, shell):
        self.run = 1
   
        while self.run:
            try:
                cl = raw_input('n2> ')
            except:
                print >>shell.stdout
                return

            cl = cl.strip()
            if not cl or cl[0] == '#':
                continue

            cmdinfo = parseCmd(cl, shell)
            cmd = cmdinfo['argv'][0]

            cmdobj = getattr(self, 'cmd_' + cmd, None)
            if cmdobj is None:
                print >>cmdinfo['stderr'], "n2: %s: command not found. Try 'help'." % cmd
            else:
                cmdobj.run(
                    cmdinfo['stdin'], cmdinfo['stdout'], cmdinfo['stderr'],
                    cmdinfo['environ'], cmdinfo['argv']
                )

            # let files get closed, etc
            del cmdinfo


    def stop(self):
        self.run = 0

    
    def command_names(self):
        return [k[4:] for k in dir(self) if k.startswith('cmd_')]


    def command(self, cmdname):
        return getattr(self, 'cmd_' + cmdname, None)


    class cmd_cd(ShellCommand):
        """cd [name] -- change directory

        with name, change current context to one named
        without name, change current context back to startup context"""

        args = ('', 0, 1)
   
        def cmd(self, cmd, args, stderr, **kw):
            shell = self.shell
            last = shell.get_pwd()
   
            if not args:
                c = shell.get_home()
            else:
                c = shell.get_pwd()
                try:
                    c = c[args[0]]
                except exceptions.NameNotFound:
                    print >>stderr, '%s: %s: not found' % (cmd, args[0])
                    return

            ob = adapt(c, naming.IBasicContext, None)
            if ob is None:
                print >>stderr, '(not a context... using alternate handler)\n'
   
                shell.do_cd(c)
                shell.handle(c)
                shell.do_cd(last)
            else:
                shell.do_cd(ob)
   
    cmd_cd = binding.New(cmd_cd)


    class cmd_ls(ShellCommand):
        """ls [-1|-l] [-s] [-R] [-r] [name] -- list namespace contents
   
-1\tsingle column format
-l\tlong format (show object repr)
-R\trecursive listing
-r\treverse order
-s\tdon't sort list
name\tlist object named, else current context"""

        args = ('1lRrs', 0, 1)
   
        def cmd(self, cmd, opts, args, stdout, stderr, ctx=None, **kw):
            shell = self.shell

            if ctx is None:
                ctx = shell.get_pwd()

            if args:
                try:
                    ctx = ctx[args[0]]
                except exceptions.NameNotFound:
                    print >>stderr, '%s: %s not found' % (cmd, args[0])
                    return

            ctx = adapt(ctx, naming.IReadContext, None)
            if ctx is None:
                if args:
                    print >>stdout, `ctx`
                else:
                    print >>stderr, \
                        "naming.IReadContext interface not supported by object"
                return

            if '-l' in opts:
                l = [(str(k), `v`) for k, v in ctx.items()]
                if '-s' not in opts: l.sort()
                if '-r' in opts: l.reverse()
                kl = max([len(x[0]) for x in l])
                vl = max([len(x[1]) for x in l])
                if kl+vl >= self.width:
                    if kl < 40:
                        vl = self.width - kl - 2
                    elif vl < 40:
                        kl = self.width - vl - 2
                    else:
                        kl = 30; vl = self.width - kl - 2

                for k, v in l:
                    print >>stdout, k.ljust(kl)[:kl] + ' ' + v.ljust(vl)[:vl]

            elif '-1' in opts:
                l = [str(x) for x in ctx.keys()]
                if '-s' not in opts: l.sort()
                if '-r' in opts: l.reverse()
                print >>stdout, '\n'.join(l)
            else:
                l = [str(x) for x in ctx.keys()]
                shell.printColumns(stdout, l, '-s' not in opts, '-r' in opts)

            if '-R' in opts:
                for k, v in ctx.items():
                    v = adapt(v, naming.IReadContext, None)
                    if v is not None:
                        print >>stdout, '\n%s:\n' % str(k)

                        self.cmd(cmd, opts, [], stdout, stderr, ctx)
                                   
   
    class cmd_l(cmd_ls):
        """l [-s] [-R] [-r] [name] -- shorthand for ls -l. 'help ls' for more."""

        args = ('Rrs', 0, 1)
   
        def cmd(self, cmd, opts, args, stdout, stderr, **kw):
            opts['-l'] = None
            cmd_ls(self, cmd, opts, args, stdout, stderr, **kw)


    cmd_dir = binding.New(cmd_ls)
    cmd_ls = binding.New(cmd_ls)
    cmd_l = binding.New(cmd_l)


    class cmd_pwd(ShellCommand):
        """pwd -- display current context"""

        def cmd(self, **kw):
            print `self.shell.get_pwd()`

    cmd_pwd = binding.New(cmd_pwd)


    class cmd_python(ShellCommand):
        """python -- enter python interactor"""

        def cmd(self, **kw):
            self.shell.interact()

    cmd_py = binding.New(cmd_python)
    cmd_python = binding.New(cmd_python)


    class cmd_help(ShellCommand):
        """help [cmd] -- help on commands"""
  
        args = ('', 0, 1)
  
        def cmd(self, stdout, stderr, args, **kw):
            if args:
                c = self.interactor.command(args[0])
                if c is None:
                    print >>stderr, 'help: no such command: ' + args[0]
                else:
                    print c.__doc__
            else:
                print >>stdout, 'Available commands:\n'
                self.shell.printColumns(
                    stdout, self.interactor.command_names(), sort=1)


    cmd_help = binding.New(cmd_help)


    class cmd_rm(ShellCommand):
        """rm name -- unbind name from context"""
  
        args = ('', 1, 1)

        def cmd(self, cmd, stderr, args, **kw): 
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return
            
            try:
                del c[args[0]]
            except exceptions.NameNotFound:
                print >>stderr, '%s: %s: not found' % (cmd, args[0])
        
    cmd_rm = binding.New(cmd_rm)

   
    class cmd_mv(ShellCommand):
        """mv oldname newname -- rename oldname to newname"""
    
        args = ('', 2, 2)
    
        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            c.rename(args[0], args[1])        
        
    cmd_mv = binding.New(cmd_mv)


    class cmd_quit(ShellCommand):
        """quit -- leave n2 naming shell"""
    
        def cmd(self, **kw):
            self.interactor.stop()
                
    cmd_quit = binding.New(cmd_quit)


    class cmd_ll(ShellCommand):
        """ll name -- lookupLink name"""
    
        args = ('', 1, 1)
    
        def cmd(self, stdout, args, **kw):
            c = self.shell.get_pwd()
            r = c.lookupLink(args[0])
            print `r`

    cmd_ll = binding.New(cmd_ll)


    class cmd_commit(ShellCommand):
        """commit -- commit current transaction and begin a new one"""
        
        def cmd(self, **kw):
            storage.commit(self.shell)
            storage.begin(self.shell)

    cmd_commit = binding.New(cmd_commit)
    

    class cmd_abort(ShellCommand):
        """abort -- roll back current transaction and begin a new one"""
        
        def cmd(self, **kw):
            storage.abort(self.shell)
            storage.begin(self.shell)

    cmd_abort = binding.New(cmd_abort)
    

    class cmd_mksub(ShellCommand):
        """mksub name -- create a subcontext"""
        
        args = ('', 1, 1)
        
        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            c.mksub(args[0])

    cmd_md = binding.New(cmd_mksub)        
    cmd_mkdir = binding.New(cmd_mksub)        
    cmd_mksub = binding.New(cmd_mksub)        


    class cmd_rmsub(ShellCommand):
        """rmsub name -- remove a subcontext"""
        
        args = ('', 1, 1)
        
        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            c.rmsub(args[0])

    cmd_rd = binding.New(cmd_rmsub)        
    cmd_rmdir = binding.New(cmd_rmsub)        
    cmd_rmsub = binding.New(cmd_rmsub)        


protocols.declareAdapter(
    lambda ns, proto: NamingInteractor(),
    provides = [IN2Interactor],
    forProtocols = [naming.IBasicContext]
)

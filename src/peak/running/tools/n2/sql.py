"""
SQL Interactor
"""

from peak.api import *
from commands import *
from interfaces import *

from tempfile import mktemp
import sys, os, time


def bufname(s):
    """comvert buffer name to canonical form
    ignoring leading ! on user-defined buffers"""
    
    if s in ('!.', '!!'):
        return s
    elif s.startswith('!'):
        return s[1:]
    
    return s
            


class SQLInteractor(binding.Component):
    
    editor = binding.bindToProperty('__main__.EDITOR', default='vi')

    shell = binding.bindTo('..')
    con = binding.requireBinding('The SQL connection')

    state = ''
    pushbuf = binding.New(list)
    bufs = binding.New(dict)
    buf = ''
    line = 1
    semi = -1
    


    def prompt(self):
        return '%s%d> ' % (self.state, self.line)



    def interact(self, object, shell):
        binding.suggestParentComponent(shell, None, object)

        self.con.connection # ensure it's opened immediately

        self.quit = False
        
        while not self.quit:
            try:
                l = self.readline(self.prompt()) + '\n'
            except EOFError:
                print >>shell.stdout
                return
                                
            sl = l.strip()
            if ';' in sl:
                sl = sl.split(';', 1)[0].strip()
                
            if sl:
                cmd = sl.split(None, 1)[0].lower()

                if self.handleCommand(cmd, l) is not NOT_FOUND:
                    continue

            self.line += 1
            
            self.updateState(l)
            semi = self.semi
            
            if semi >= 0:
                b = self.getBuf()
                b, cmd = b[:semi] + '\n', b[semi+1:]
                self.setBuf(b)
                
                self.handleCommand('go', 'go ' + cmd)



    def getBuf(self, name='!.'):
        name = bufname(name)

        return self.bufs.get(name, '')



    def setBuf(self, val, name='!.', append=False):
        name = bufname(name)

        if append:
            self.bufs[name] = self.bufs.get(name, '') + val
        else:
            self.bufs[name] = val


    
    def resetBuf(self):
        self.state = ''; self.line = 1; self.semi = - 1
        self.setBuf('')

    
        
    def command(self, cmd):
        return getattr(self, 'cmd_' + cmd.replace('-', '_'), None)
        
       
        
    def handleCommand(self, cmd, l):
        shell = self.shell

        r = NOT_FOUND
        
        cmd = cmd.lower()
        if cmd[0] == '\\' or cmd in (
            'go','commit','abort','rollback','help'
        ):
            if cmd[0] == '\\':
                cmd = cmd[1:]
                
            cmdobj = self.command(cmd)
            if cmdobj is None:
                print >>shell.stderr, "command '%s' not found. Try 'help'." % cmd

                return
            else:
                cmdinfo = parseCmd(l, shell)

                r = cmdobj.run(
                    cmdinfo['stdin'], cmdinfo['stdout'], cmdinfo['stderr'],
                    cmdinfo['environ'], cmdinfo['argv']
                )

                # let files get closed, etc
                del cmdinfo

            if r is True:
                self.redraw(self.shell.stdout)

        return r
        


    def toStr(self, v, w=None):
        if v is None:
            return "NULL"
        elif w is None:
            return str(v)
        elif type(v) in (int, long):
            return "%*d" % (w, v)
        elif type(v) is float:
            return "%*g" % (w, v)
        else:
            return str(v).ljust(w)[:w]


            
    def showResults(self, c, shower, opts, stdout):
        shower = self.showers.get(shower, 'showHoriz')
        shower = getattr(self, shower)
        nr = shower(c, opts, stdout)
        if not opts.has_key('-f'):
            print >>stdout, "(%d rows)" % nr
        while c.nextset():
            print >>stdout
            nr = shower(r, opts, stdout)
            if not opts.has_key('-f'):
                print >>stdout, "(%d rows)" % nr



    showers = {
        'horiz' : 'showHoriz',
        'vert' : 'showVert',
        'plain' : 'showPlain',
        'python' : 'showPython',
    }

                                
                               
    def showHoriz(self, c, opts, stdout):
        out = stdout.write
        t, d, l = [], [], []
        first = 1
        nr = 0
        for r in c._cursor.description:
            w = r[2]
            if w <= 0: w = 20 # XXX
            
            t.append(self.toStr(r[0], w)); d.append('-' * w); l.append(w)

        if '-h' not in opts:
            out(' '.join(t)); out('\n')
            out(' '.join(d)); out('\n')
            
        for r in c:
            nr += 1
            i = 0
            o = []
            for v in r:
                o.append(self.toStr(v, l[i]))
                i += 1

            out(' '.join(o))
            out('\n')
        
        return nr



    def showVert(self, c, opts, stdout):
        h = [x[0] for x in c._cursor.description]
        w = max([len(x) for x in h])
        nr = 0
        
        for r in c:
            i = 0
            nr += 1
            for v in r:
                print >>stdout, "%s %s" % (h[i].rjust(w), self.toStr(v))
                i += 1
            print >>stdout
            
        return nr


            
    def showPlain(self, c, opts, stdout):
        d = opts.get('-d', '|')
        nr = 0
        
        if not '-h' in opts:
            print >>stdout, d.join([x[0] for x in c._cursor.description])
        for r in c:
            nr += 1
            print >>stdout, d.join([self.toStr(v) for v in r])

        return nr
            


    def showPython(self, c, opts, stdout):
        nr = 0
        
        if not '-h' in opts:
            print >>stdout, c._cursor.description
        for r in c:
            nr += 1
            print >>stdout, r

        return nr


            
    def command_names(self):
        l = [k for k in dir(self) if k.startswith('cmd_')]
        l2 = [k[4:].replace('_','-') for k in l
            if getattr(getattr(self, k), 'noBackslash', False)]
        l = ['\\'+k[4:].replace('_','-') for k in l]
        l.sort(); l2.sort()

        return l2 + l



    class cmd_go(ShellCommand):
        """go [-d delim] [-m style] [-h] [-f] -- submit current input
-d delim\tuse specified delimiter
-m style\tuse specified format (one of: horiz, vert, plain, python)
-h\t\tsuppress header
-f\t\tsuppress footer"""

        noBackslash = True
        
        args = ('d:m:hf', 0, 0)
        
        def cmd(self, cmd, opts, stdout, stderr, **kw):
            i = self.interactor.getBuf()
            if i.strip():
                if self.interactor.state:
                    print >>stderr, "Please finish comment or quotes first."
                    return
            else:
                i = self.interactor.getBuf('!!')
                if not i.strip():
                    self.interactor.resetBuf()
                    return

            try:
                con = self.interactor.con
                con.joinTxn()
                c = con(i)
            except:
                # currently the error is logged
                # sys.excepthook(*sys.exc_info()) # XXX
                self.interactor.resetBuf()
                return

            shower = opts.get('-m', 'horiz')
            self.interactor.showResults(c, shower, opts, stdout)

            self.interactor.setBuf(i, name='!!')

            self.interactor.resetBuf()

    cmd_go = binding.New(cmd_go)



    class cmd_abort(ShellCommand):
        """abort -- abort current transaction
rollback -- abort current transaction"""

        noBackslash = True

        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            storage.abortTransaction(self)
            storage.beginTransaction(self)
            
            self.interactor.resetBuf()

    cmd_rollback = binding.New(cmd_abort)
    cmd_abort = binding.New(cmd_abort)


   
    class cmd_commit(ShellCommand):
        """commit -- commit current transaction"""

        noBackslash = True

        args = ('', 0, 0)
        
        def cmd(self, cmd, stderr, **kw):
            if self.interactor.getBuf().strip():
                print >>stderr, "Use GO or semicolon to finish outstanding input first"
            else:
                storage.commitTransaction(self)
                storage.beginTransaction(self)
            
                self.interactor.resetBuf()

    cmd_commit = binding.New(cmd_commit)


   
    class cmd_reset(ShellCommand):
        """\\reset -- empty input buffer"""
            
        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            self.interactor.resetBuf()

    cmd_reset = binding.New(cmd_reset)



    class cmd_exit(ShellCommand):
        """\\exit -- exit SQL interactor
\\quit -- exit SQL interactor"""
            
        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            self.interactor.quit = True

    cmd_quit = binding.New(cmd_exit)
    cmd_exit = binding.New(cmd_exit)



    class cmd_python(ShellCommand):
        """\\python -- enter python interactor"""
            
        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            self.shell.interact()

    cmd_python = binding.New(cmd_python)



    class cmd_buf_copy(ShellCommand):
        """\\buf-copy dest [src] -- copy buffer src to dest

default for src is '!.', the current input buffer"""
            
        args = ('', 1, 2)
        
        def cmd(self, cmd, args, stdout, **kw):
            src = '!.'
            if len(args) == 2:
                src = args[1]
                
            self.interactor.setBuf(self.interactor.getBuf(src), name=args[0])
            
            if args[0] == '!.':
                return True

    cmd_buf_copy = binding.New(cmd_buf_copy)



    class cmd_buf_get(ShellCommand):
        """\\buf-get src -- like \buf-append !. src"""
            
        args = ('', 1, 1)
        
        def cmd(self, cmd, args, stdout, **kw):
            self.interactor.setBuf(self.interactor.getBuf(args[0]), append=True)

            return True

    cmd_buf_get = binding.New(cmd_buf_get)



    class cmd_buf_append(ShellCommand):
        """\\buf-append dest [src] -- append buffer src to dest

default for src is '!.', the current input buffer"""
            
        args = ('', 1, 2)
        
        def cmd(self, cmd, args, stdout, **kw):
            src = '!.'
            if len(args) == 2:
                src = args[1]
                
            self.interactor.setBuf(self.interactor.getBuf(src), name=args[0],
                append=True)
            
            if args[0] == '!.':
                return True

    cmd_buf_append = binding.New(cmd_buf_append)



    class cmd_buf_save(ShellCommand):
        """\\buf-save [-a] filename [src] -- save buffer src in a file

-a\tappend to file instead of overwriting"""
            
        args = ('a', 1, 2)
        
        def cmd(self, cmd, opts, args, stderr, **kw):
            mode = 'w'
            if opts.has_key('-a'):
                mode = 'a'
                
            src = '!.'
            if len(args) == 2:
                src = args[1]

            try:
                f = open(args[0], mode)
                f.write(self.interactor.getBuf(src))
                f.close()
            except:
                sys.excepthook(*sys.exc_info()) # XXX

    cmd_buf_save = binding.New(cmd_buf_save)



    class cmd_buf_load(ShellCommand):
        """\\buf-load [-a] filename [dest] -- load buffer dest from file

-a\tappend to buffer instead of overwriting"""
            
        args = ('a', 1, 2)
        
        def cmd(self, cmd, opts, args, stderr, **kw):
            try:
                dest = '!.'
                if len(args) == 2:
                    dest = args[1]

                f = open(args[0], 'r')
                l = f.read()
                self.interactor.setBuf(l, append=opts.has_key('-a'), name=dest)

                f.close()
                
                l = self.interactor.getBuf(dest)
                if l and not l.endswith('\n'):
                    self.interactor.setBuf('\n', append=True, name=dest)

            except:
                sys.excepthook(*sys.exc_info()) # XXX

            if dest == '!.':                
                return True
            
    cmd_buf_load = binding.New(cmd_buf_load)



    class cmd_buf_show(ShellCommand):
        """\\buf-show -- show buffer list
\\buf-show [buf] -- show named buffer"""
            
        args = ('', 0, 1)
        
        def cmd(self, cmd, args, stdout, **kw):
            if len(args) == 1:
                stdout.write(self.interactor.getBuf(args[0]))
            else:
                l = self.interactor.bufs.keys()
                l.sort()
                stdout.write('\n'.join(l))
                stdout.write('\n')

            stdout.flush()

    cmd_buf_show = binding.New(cmd_buf_show)



    class cmd_buf_edit(ShellCommand):
        """\\buf-edit -- use external editor on current input buffer"""
            
        args = ('r:w:', 0, 0)
        
        def cmd(self, cmd, opts, stderr, **kw):
            t = mktemp()
            f = open(t, 'w')
            f.write(self.interactor.getBuf(opts.get('-r', '!.')))
            f.close()
            r = os.system('%s "%s"' % (self.interactor.editor, t))
            if r:
                print >>stderr, '[edit file unchanged]'
            else:
                f = open(t, 'r')
                l = f.read()
                f.close()
                wr = opts.get('-w', '!.')
                self.interactor.setBuf(l, name=wr)
                if l and not l.endswith('\n'):
                    self.interactor.setBuf('\n', append=True, name=wr)

            os.unlink(t)
                
            return True

    cmd_buf_edit = binding.New(cmd_buf_edit)



    class cmd_source(ShellCommand):
        """\\source [-r] filename -- interpret input from file

-r\treset input buffer before sourcing file"""
            
        args = ('r', 1, 1)
        
        def cmd(self, cmd, opts, args, stderr, **kw):
            try:
                f = open(args[0], 'r')
                l = f.read()
                if l[-1] == '\n':
                    l = l[:-1]
                l = l.split('\n')
                l.reverse()
                self.interactor.pushbuf = l + self.interactor.pushbuf
                f.close()
                
                return opts.has_key('-r')
            except:
                sys.excepthook(*sys.exc_info()) # XXX

    cmd_source = binding.New(cmd_source)



    class cmd_help(ShellCommand):
        """\\help [cmd] -- help on commands"""

        noBackslash = True

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
                    stdout, self.interactor.command_names(), sort=False)

    cmd_help = binding.New(cmd_help)



    class cmd_reconnect(ShellCommand):
        """\\reconnect -- abort current transaction and reconnect to database"""

        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            self.interactor.con.closeASAP()
            storage.abortTransaction(self)
            self.interactor.con.connection
            storage.beginTransaction(self)
            
            self.interactor.resetBuf()

    cmd_reconnect = binding.New(cmd_reconnect)



    class cmd_redraw(ShellCommand):
        """\\redraw -- redraw current input buffer"""

        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            return True
            
    cmd_redraw = binding.New(cmd_redraw)



    class cmd_echo(ShellCommand):
        """\\echo secs -- echo for 'secs' seconds"""

        args = ('-n', 0, sys.maxint)
        
        def cmd(self, cmd, opts, args, stdout, **kw):
            stdout.write(' '.join(args))
            if not opts.has_key('-n'):
                stdout.write('\n')
            stdout.flush()

    cmd_echo = binding.New(cmd_echo)



    class cmd_sleep(ShellCommand):
        """\\sleep secs -- sleep for 'secs' seconds"""

        args = ('', 1, 1)
        
        def cmd(self, cmd, args, stderr, **kw):
            try:
                s = float(args[0])
            except:
                print >>stderr, "%s: invalid number '%s'" % (cmd, args[0])
                return
                
            time.sleep(s)

    cmd_sleep = binding.New(cmd_sleep)



    def redraw(self, stdout):
        b = self.getBuf()
        self.resetBuf()
        out = self.shell.stdout

        if b.endswith('\n'):
            b = b[:-1]

        b = b.split('\n')

        for l in b:
            l += '\n'
            stdout.write(self.prompt())
            stdout.write(l)
            
            self.line += 1
            
            self.updateState(l)

         
       
    def updateState(self, s):
        state = self.state

        i = 0
        for c in s:
            if not state:
                if c in '\'"/':
                    state = c
                elif c == ';' and self.semi < 0:
                    self.semi = len(self.getBuf()) + i
            elif state == '/':
                if c == '*':
                    state = 'C'
                elif c == ';' and self.semi < 0:
                    self.semi = len(self.getBuf()) + i
                else:
                    state = ''
            elif state == 'C':
                if c == '*':
                    state = c
            elif state == '*':
                if c == '/':
                    state = ''
                else:
                    state = 'C'
            elif state in ("'", '"'):
                if c == state:
                    state = 'D' + c
            elif state[0] == 'D':
                if c == state[1]:
                    state = state[1]
                elif c == '/':
                    state = c
                elif c == ';' and self.semi < 0:
                    self.semi = len(self.getBuf()) + i
                else:
                    state = ''
            i += 1

        self.state = state
        self.setBuf(s, append=True)

    
    def readline(self, prompt):
        if self.pushbuf:
            l = self.pushbuf.pop()
            self.shell.stdout.write(prompt + l + '\n')
            return l
        else:
            return raw_input(prompt)


protocols.declareAdapter(
    lambda con, proto: SQLInteractor(con=con),
    provides = [IN2Interactor],
    forProtocols = [storage.ISQLConnection]
)


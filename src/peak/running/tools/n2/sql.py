"""
SQL Interactor
"""

from peak.api import *
from commands import *
from interfaces import *

from tempfile import mktemp
import sys, os

class SQLInteractor(binding.Component):
    
    editor = binding.bindToProperty('__main__.EDITOR', default='vi')

    shell = binding.bindTo('..')
    con = binding.requireBinding('The SQL connection')

    state = ''
    pushbuf = binding.New(list)
    buf = ''
    line = 0
    semi = -1
    
    def interact(self, object, shell):
        binding.suggestParentComponent(shell, None, object)

        self.quit = False
        
        while not self.quit:
            self.line += 1
            
            try:
                l = self.readline('%s%d> ' % (self.state, self.line)) + '\n'
            except EOFError:
                print >>shell.stdout
                return
                                
            sl = l.strip()
            if ';' in sl:
                sl = sl.split(';', 1)[0].strip()
                
            if sl:
                cmd = sl.split(None, 1)[0].lower()

                if self.handleCommand(cmd, l) is not None:
                    continue

            self.updateState(l)
            semi = self.semi
            
            if semi >= 0:
                self.buf, cmd = self.buf[:semi] + '\n', self.buf[semi+1:]
                
                self.handleCommand('go', 'go ' + cmd)



    def resetBuf(self):
        self.state = self.buf = ''; self.line = 0; self.semi = - 1

    
        
    def command(self, cmd):
        return getattr(self, 'cmd_' + cmd.replace('-', '_'), None)
        
       
        
    def handleCommand(self, cmd, l):
        shell = self.shell

        r = None
        
        cmd = cmd.lower()
        if cmd[0] == '\\' or cmd in (
            'go','commit','abort','rollback','reset','quit','help'
        ):
            if cmd[0] == '\\':
                cmd = cmd[1:]
                
            cmdobj = self.command(cmd)
            if cmdobj is None:
                print >>shell.stderr, "command '%s' not found. Try 'help'." % cmd

                return False
            else:
                cmdinfo = parseCmd(l, shell)

                r = cmdobj.run(
                    cmdinfo['stdin'], cmdinfo['stdout'], cmdinfo['stderr'],
                    cmdinfo['environ'], cmdinfo['argv']
                )

                # let files get closed, etc
                del cmdinfo

            if r:
                self.resetBuf()
            elif r is not None:
                self.line = self.buf.count('\n')

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
        shower(c, opts, stdout)
        while c.nextset():
            print >>stdout
            show(r, opts, stdout)



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
        for r in c._cursor.description:
            w = r[2]
            if w <= 0: w = 20 # XXX
            
            t.append(self.toStr(r[0], w)); d.append('-' * w); l.append(w)

        if '-h' not in opts:
            out(' '.join(t)); out('\n')
            out(' '.join(d)); out('\n')
            
        for r in c:
            i = 0
            o = []
            for v in r:
                o.append(self.toStr(v, l[i]))
                i += 1

            out(' '.join(o))
            out('\n')



    def showVert(self, c, opts, stdout):
        h = [x[0] for x in c._cursor.description]
        w = max([len(x) for x in h])
        
        for r in c:
            i = 0
            for v in r:
                print >>stdout, "%s %s" % (h[i].rjust(w), self.toStr(v))
                i += 1
            print >>stdout


            
    def showPlain(self, c, opts, stdout):
        d = opts.get('-d', '|')
        
        if not '-h' in opts:
            print >>stdout, d.join([x[0] for x in c._cursor.description])
        for r in c:
            print >>stdout, d.join([self.toStr(v) for v in r])
            


    def showPython(self, c, opts, stdout):
        if not '-h' in opts:
            print >>stdout, c._cursor.description
        for r in c:
            print >>stdout, r


            
    def command_names(self):
        return [k[4:].replace('_','-')
            for k in dir(self) if k.startswith('cmd_')]



    class cmd_go(ShellCommand):
        """go [-d delim] [-f format] [-h] -- submit current input
-d delim\tuse specified delimiter
-f format\tuse specified format (one of: horiz, vert, plain, python)
-h\t\tsuppress header"""

        args = ('d:f:h', 0, 0)
        
        def cmd(self, cmd, opts, stdout, **kw):
            i = self.interactor.buf
            if not i.strip():
                return True

            try:
                c = self.interactor.con(i)
            except:
                sys.excepthook(*sys.exc_info()) # XXX
                return True

            shower = opts.get('-f', 'horiz')
            self.interactor.showResults(c, shower, opts, stdout)

            return True

    cmd_go = binding.New(cmd_go)



    class cmd_abort(ShellCommand):
        """abort -- abort current transaction
rollback -- abort current transaction"""

        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            storage.abortTransaction(self)
            storage.beginTransaction(self)
            
            return True

    cmd_rollback = binding.New(cmd_abort)
    cmd_abort = binding.New(cmd_abort)


   
    class cmd_commit(ShellCommand):
        """commit -- commit current transaction"""

        args = ('', 0, 0)
        
        def cmd(self, cmd, stderr, **kw):
            if self.interactor.buf.strip():
                print >>stderr, "Use GO or semicolon to finish outstanding input first"

                return False
            else:
                storage.commitTransaction(self)
                storage.beginTransaction(self)
            
                return True

    cmd_commit = binding.New(cmd_commit)


   
    class cmd_reset(ShellCommand):
        """reset -- empty input buffer"""
            
        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            return True

    cmd_reset = binding.New(cmd_reset)



    class cmd_quit(ShellCommand):
        """quit -- quit SQL interactor"""
            
        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            self.interactor.quit = True
            return True

    cmd_quit = binding.New(cmd_quit)



    class cmd_python(ShellCommand):
        """python -- enter python interactor"""
            
        args = ('', 0, 0)
        
        def cmd(self, cmd, **kw):
            self.shell.interact()
            return False

    cmd_python = binding.New(cmd_python)



    class cmd_buf_show(ShellCommand):
        """buf-show -- show current input buffer"""
            
        args = ('', 0, 0)
        
        def cmd(self, cmd, stdout, **kw):
            stdout.write(self.interactor.buf)
            stdout.flush()
            
            return False

    cmd_buf_show = binding.New(cmd_buf_show)



    class cmd_buf_edit(ShellCommand):
        """buf-edit -- use external editor on current input buffer"""
            
        args = ('', 0, 0)
        
        def cmd(self, cmd, stderr, **kw):
            t = mktemp()
            f = open(t, 'w')
            f.write(self.interactor.buf)
            f.close()
            r = os.system('%s "%s"' % (self.interactor.editor, t))
            if r:
                print >>stderr, '[edit file unchanged]'
            else:
                f = open(t, 'r')
                l = f.read()
                f.close()
                self.interactor.buf = l
                if self.interactor.buf and self.interactor.buf[-1] != '\n':
                    self.interactor.buf += '\n'

            os.unlink(t)
                
            return False

    cmd_buf_edit = binding.New(cmd_buf_edit)



    class cmd_buf_save(ShellCommand):
        """buf-save [-a] filename -- save input buffer in a file

-a\tappend to file instead of overwriting"""
            
        args = ('a', 1, 1)
        
        def cmd(self, cmd, opts, args, stderr, **kw):
            mode = 'w'
            if opts.has_key('-a'):
                mode = 'a'

            try:
                f = open(args[0], mode)
                f.write(self.interactor.buf)
                f.close()
            except:
                sys.excepthook(*sys.exc_info()) # XXX
                
            return False
            

    cmd_buf_save = binding.New(cmd_buf_save)



    class cmd_buf_load(ShellCommand):
        """buf-load [-a] filename -- load input buffer from file

-a\tappend to buffer instead of overwriting"""
            
        args = ('a', 1, 1)
        
        def cmd(self, cmd, opts, args, stderr, **kw):
            try:
                f = open(args[0], 'r')
                l = f.read()
                if opts.has_key('-a'):
                    self.interactor.buf += l
                else:
                    self.interactor.buf = l

                f.close()
                
                if self.interactor.buf and self.interactor.buf[-1] != '\n':
                    self.interactor.buf += '\n'

            except:
                sys.excepthook(*sys.exc_info()) # XXX
                
            return False
            

    cmd_buf_load = binding.New(cmd_buf_load)



    class cmd_source(ShellCommand):
        """source [-r] filename -- interpret input from file

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
                
            return False
            

    cmd_source = binding.New(cmd_source)



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
                print >>stdout, 'Available commands:\t(note, many require "\\" prefix)\n'
                self.shell.printColumns(
                    stdout, self.interactor.command_names(), sort=1)

            return False

    cmd_help = binding.New(cmd_help)



    def updateState(self, s):
        state = self.state

        i = 0
        for c in s:
            if not state:
                if c in '\'"/':
                    state = c
                elif c == ';' and self.semi < 0:
                    self.semi = len(self.buf) + i
            elif state == '/':
                if c == '*':
                    state = 'C'
                elif c == ';' and self.semi < 0:
                    self.semi = len(self.buf) + i
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
                    self.semi = len(self.buf) + i
                else:
                    state = ''
            i += 1

        self.state = state
        self.buf += s

    
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
            

"""Readline configuration stack, with fallback if no readline module"""

import os

__all__ = ['pushRLHistory', 'popRLHistory', 'addRLHistoryLine']

try:
    import readline
    def_delims = readline.get_completer_delims()
    try:
        import rlcompleter
        readline.parse_and_bind("tab: complete")
        pycomplete = rlcompleter.Completer().complete
    except:
        pycomplete = None
except:
    readline = None



histstack = []
curhist = curcompl = curdelims = None
curlines = -1


def pushRLHistory(fn, completer=None, delims=None, environ=None, lines=-1):
    """Set up readline with given parameters, saving old state.
    This function is safe to call if readline is absent; it will
    silently do nothing.
    
    fn is a filename, relative to the home directory, for the history file.

    completer is a completion callable (see readline module documentation),
    or as a convenience, True may be passed for an interactive Python
    completer.
    
    delimns is a string containing characters that delimit completion words.
    passing None will use teh default set.
    
    environ is the environment in which to look up variables such as the
    home directory. 
    
    lines is the number of lines of history to keep, or -1 for unlimited.
    """
    
    global curhist, curcompl, curdelims, curlines, histstack
    
    if readline:
        if environ is None:
            environ = os.environ
            
        if curhist:
            readline.write_history_file(curhist)
            histstack.append((curhist, curcompl, curdelims, curlines))
        homedir = environ.get('HOME', os.getcwd())
        curhist = os.path.join(homedir, fn)
        try:
            readline.read_history_file(curhist)
        except:
            pass

        if completer is True:
            completer = pycomplete
        if delims is None:
            delims = def_delims

        curcompl = completer
        curdelims = delims
        curlines = lines
            
        readline.set_completer(completer)
        readline.set_completer_delims(curdelims)
        readline.set_history_length(curlines)


def popRLHistory():
    global curhist, curcompl, curdelims, curlines, histstack

    if readline:
        readline.write_history_file(curhist)
        if histstack:
            curhist, curcompl, curdelims, curlines = histstack.pop()
            try:
                readline.read_history_file(curhist)
            except:
                pass
            readline.set_completer(curcompl)
            readline.set_completer_delims(curdelims)
            readline.set_history_length(curlines)
        


def addRLHistoryLine(l):
    if readline is not None:
        readline.add_history(l)

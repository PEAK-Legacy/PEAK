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


def pushRLHistory(fn, completer, delims, environ):
    global curhist, curcompl, curdelims, histstack
    
    if readline:
        if curhist:
            readline.write_history_file(curhist)
            histstack.append((curhist, curcompl, curdelims))
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
            
        readline.set_completer(completer)
        readline.set_completer_delims(curdelims)


def popRLHistory():
    global curhist, curcompl, curdelims, histstack

    if readline:
        readline.write_history_file(curhist)
        if histstack:
            curhist, curcompl, curdelims = histstack.pop()
            try:
                readline.read_history_file(curhist)
            except:
                pass
            readline.set_completer(curcompl)
            readline.set_completer_delims(curdelims)
        


def addRLHistoryLine(l):
    if readline is not None:
        readline.add_history(l)

"""Miscellaneous utilities that I don't know where else to put..."""

def upToDate(source,dest):

    """Is file 'dest' up to date relative to file 'source'?"""
    
    from os import path, stat
    from stat import ST_MTIME
    
    return  source and dest and \
            path.exists(dest) and path.exists(source) and \
            stat(source)[ST_MTIME]<=stat(dest)[ST_MTIME] 


def getCallerInfo(stacklevel=2):

    """Return caller module and line number"""
    
    import sys
    
    try:
        caller = sys._getframe(stacklevel)
        
    except ValueError:  # sys couldn't tell us, crap out
        return sys.__name__, 1
        
    except AttributeError: # 1.5.2, get it the sneaky way

        caller = sys.exc_info()[2].tb_frame
        
        for f in range(stacklevel):
            if caller.f_back is not None: caller = caller.f_back
                    
    return caller.f_globals['__name__'], caller.f_lineno







def InterfaceChecker(anInterface):

    def checkInterface(object, check = anInterface.isImplementedBy, hasattr=hasattr):
        if hasattr(object,'__implements__') or \
           hasattr(object,'__class_implements__'):
            return check(object)
            
    return checkInterface

"""
# experimental...

from Interface.Standard import Class as IPythonClass
from Interface.iclass import _typeImplements
from ClassTypes import isClass

def cachedInterfaceChecker(anInterface):

    def checkInterface(object, check = anInterface.isImplementedBy, cache={}):

        t=type(object)
        if isClass(t):
            if hasattr(object, '__class_implements__'):
                implements=object.__class_implements__
            else:
                implements=IPythonClass
                
        elif hasattr(object, '__implements__'):
            implements=object.__implements__
        else:
            implements =_typeImplements.get(t, None)
            if implements is None: return 0
    
        if cache.has_key(implements):
            return cache[implements]
            
        c = cache[implements] = check(object)
        return c

    return checkInterface
"""

from array import array
import new
from types import CodeType, StringType
from dis import HAVE_ARGUMENT, EXTENDED_ARG, opname

__all__ = ['Code', 'Function', 'opcode', 'codeIter', 'FunctionBinder', 'bind_func']

opcode = {}

for code in range(256):
    name=opname[code]
    if name.startswith('<'): continue
    opcode[name]=code

LOAD_NAME = opcode['LOAD_NAME']
LOAD_GLOBAL = opcode['LOAD_GLOBAL']
LOAD_CONST = opcode['LOAD_CONST']
SET_LINENO = opcode['SET_LINENO']


try:
    x = object
    del x

except:
    # XXX 2.1 backport
    from ExtensionClass import Base as object
    from ComputedAttribute import ComputedAttribute as property
    StopIteration = 'StopIteration'
    def iter(x): return x.__iter__()











class Code(object):

    def __init__(self, code=None):
        if code is None:
            self.init_code_defaults()
        elif isinstance(code,CodeType) or isinstance(code,Code):
            self.init_code(code)
        else:
            self.init_code_tuple(code)
            
    def init_code_defaults(self):
        self.init_code_tuple((
            0, 0,(),(),(),'<edited code>','no name',0,'','',(),(),
        ))

    def init_code(self,code):
        self.init_code_tuple((            
            code.co_argcount,
            code.co_nlocals,
            code.co_stacksize,
            code.co_flags,
            code.co_code,
            code.co_consts,
            code.co_names,
            code.co_varnames,
            code.co_filename,
            code.co_name,
            code.co_firstlineno,
            code.co_lnotab,
            code.co_freevars,
            code.co_cellvars,
        ))
        
    def __iter__(self):
        return codeIter(self)

    def code(self):
        return new.code(*self.code_as_tuple())



    def init_code_tuple(self,tup):
        ( self.co_argcount, self.co_nlocals, self.co_stacksize, self.co_flags,
          co_code, co_consts, co_names, co_varnames, self.co_filename,
          self.co_name, self.co_firstlineno, self.co_lnotab, self.co_freevars,
          self.co_cellvars
        ) = tup
        self.co_consts = list(co_consts)
        self.co_names = list(co_names)
        self.co_varnames = list(co_varnames)
        self.co_code = array('B',co_code)


    def code_as_tuple(self):
        return (
            self.co_argcount,
            len(self.co_varnames),
            self.co_stacksize,
            self.co_flags,
            self.co_code.tostring(),
            tuple(self.co_consts),
            tuple(self.co_names),
            tuple(self.co_varnames),
            self.co_filename,
            self.co_name,
            self.co_firstlineno,
            self.co_lnotab,
            self.co_freevars,
            self.co_cellvars
        )


    def iterFromEnd(self):
        return codeIter(self,len(self.co_code))

    def name_index(self,name):
        if name not in self.co_names:
            self.co_names.append(name)
        return self.co_names.index(name)



    def const_index(self,const):
        if const not in self.co_consts:
            self.co_consts.append(const)
        return self.co_consts.index(const)

    def local_index(self,name):
        if name not in self.co_varnames:
            self.co_varnames.append(name)
        return self.co_varnames.index(name)

    def free_index(self,name):
        if name not in self.co_freevars:
            self.co_freevars.append(name)
        return self.co_freevars.index(name)

    def cell_index(self,name):
        if name not in self.co_cellvars:
            self.co_cellvars.append(name)
        return self.co_cellvars.index(name)


    def findOp(self,op):
        return codeIter(self,0,[op])

    def findOps(self,oplist):
        return codeIter(self,0,oplist)


    def namesUsed(self):
        used = {}
        names = self.co_names
        cursor = self.findOp(LOAD_NAME)

        for op in cursor:
            used[names[cursor.arg]]=1

        return used.keys()




    def renumberLines(self, toLine):

        self.co_firstlineno = toLine

        cursor = self.findOp(SET_LINENO)
        cursor.next()
        offset = (toLine - cursor.arg)
        cursor.go(0)

        for op in cursor:
            cursor.write(SET_LINENO, cursor.arg + offset)






























class Function(Code):
    
    def __init__(self, func=None):
        if func is None:
            self.init_func_defaults()
        else:
            self.init_func(func)

    def init_func_defaults(self):
        self.func_globals={}
        self.func_name='unnamed function'
        self.func_dict=None
        self.func_doc=None
        self.func_closure=None
        self.func_defaults = ()
        self.init_code_defaults()
        
    def init_func(self, func):
        self.func_globals   = func.func_globals
        self.func_name      = func.func_name
        self.func_dict      = func.func_dict
        self.func_doc       = func.func_doc
        self.func_closure   = func.func_closure
        self.func_defaults  = func.func_defaults
        self.init_code(func.func_code)    

    def func(self):
        c = self.code()
        f = new.function(c, self.func_globals, self.func_name, self.func_defaults or ())
        f.func_dict = self.func_dict
        f.func_doc  = self.func_doc
        #f.func_closure = self.func_closure
        return f








allOps = [1]*256

class codeIter(object):
    
    op = None

    def __init__(self, codeObject, startAt=0, findOps=None):
        self.code = codeObject
        self.codeArray = codeObject.co_code
        self.end = startAt
        self.setMask(findOps)

    def setMask(self,opList):
        if opList:
            opmap = self.findOps = [0]*256
            for f in opList:
                if isinstance(f,StringType): f = opcode[f]
                opmap[f]=1
        else:
            self.findOps = allOps
            
    def arg(self):
        s, e = self.start, self.end
        l = e-s
        if l>=3:
            ca = self.codeArray
            arg = ca[s+1] | ca[s+2]<<8
            if l==6:
                arg <<= 16
                arg += (ca[s+4] | ca[s+5]<<8)
            return arg

    arg = property(arg)
    
    def __iter__(self):
        return self

    def __getitem__(self,x):    # XXX 2.1 backport
        try: return self.next()
        except StopIteration: raise IndexError, x

    def go(self,offset):
        self.end = offset
        return self.next()

    def next(self):
        ca = self.codeArray
        findOps = self.findOps
        end = self.end
        l = len(ca)

        while end < l:
            
            start = end
            op = ca[start]
            
            if op>=HAVE_ARGUMENT:
                if op==EXTENDED_ARG:
                    op = ca[start+3]
                    end = start+6
                else:
                    end = start+3
            else:
                end = start+1

            if findOps[op]:
                self.start = start
                self.end = end
                self.op = op
                return op

        self.op = None
        self.start = start
        self.end = end
        raise StopIteration







    def write(self, op, arg=None, sameSize=1):

        if isinstance(op,StringType): op = opcode[op]
    
        ca=self.codeArray
        start = self.start
        if arg is not None:
            bytes = [op, arg & 0xFF, (arg & 0xFF00)>>8]
            bl=3
            if (arg & 0xFFFF0000) not in (0xFFFF0000, 0):
                bl=6
                bytes[0:0] = [
                    EXTENDED_ARG, (arg & 0xFF0000)>>16, (arg & 0xFF000000)>>24
                ]

            if start==len(ca):
                ca.extend(array('B',bytes))
                self.end=len(ca)
                return
            
            elif sameSize and (self.end-start)<>bl:
                raise ValueError

            ca[start:start+bl] = array('B',bytes)
            self.end = start+bl
            
        else:
            if start==len(ca):
                ca.append(op)
                self.end += 1

            elif sameSize and self.end-self.start<>1:
                raise ValueError

            ca[self.start]=op






class FunctionBinder(object):

    def __init__(self, func):

        if type(func) is not Function:  # XXX 2.1 backport hack (isinstance)
            func = Function(func)
            
        self.func = func
        cursor = func.findOp(LOAD_GLOBAL)
        bindables = self.bindables = {}
        sd = bindables.setdefault
        names = func.co_names
        
        for op in cursor:
            sd(names[cursor.arg], []).append(cursor.start)
                
    def _rebind(self, kw):
        get = self.bindables.get
        func = self.func
        cursor = iter(func)
        
        for k,v in kw.items():
            fixups = get(k)
            if fixups:
                ci = func.const_index(v)
                for f in fixups:
                    cursor.go(f)
                    cursor.write(LOAD_CONST,ci)

    def boundCode(self, **kw):
        self._rebind(kw)
        return self.func.code()
    
    def boundFunc(self, **kw):
        self._rebind(kw)
        return self.func.func()





def bind_func(func, **kw):
    b=FunctionBinder(func)
    func.func_code = b.boundCode(**kw)
    return func


def copy_func(func):
    return Function(func).func()



# And now, as a demo... self-modifying code!

bid = getattr(__builtins__,'__dict__',__builtins__)

for f in (
        codeIter.next, codeIter.write,
        FunctionBinder.__init__, FunctionBinder._rebind,
    ):
    bind_func(f.im_func, **globals())
    bind_func(f.im_func, **bid)




















def visit(code, visitFunc=lambda code,path,newconsts: code, path=()):

    consts = list(code.co_consts)

    for i in range(len(consts)):

        co = consts[i]

        if type(co) is CodeType:
            consts[i]=visit(co,visitFunc,path+(co.co_name,))

    return visitFunc(code, path, tuple(consts))


def show(code, path, newconsts):
    print path
    return code



if __name__ == '__main__':
    
    foo = "foo"

    def bar():
        print foo

    baz = bind_func(copy_func(bar), foo="Hello, World!")
   
    bar(); baz()
    
    foo = "it worked!"
    
    bar(); baz()



"""Module Inheritance and Module Advice

    The APIs defined here let you create modules which derive from other
    modules, by defining a module-level '__bases__' attribute which lists
    the modules you wish to inherit from.  For example::

        from TW.API import *

        import BaseModule1, BaseModule2

        __bases__ = BaseModule1, BaseModule2

       
        class MyClass:
            ...

        setupModule()

    The 'setupModule()' call will convert the calling module, 'BaseModule1',
    and 'BaseModule2' into specially altered bytecode objects and execute
    them (in "method-resolution order") rewriting the calling module's
    dictionary in the process.  The result is rather like normal class
    inheritance, except that classes (even nested classes) are merged by name,
    and metaclass constraints are inherited.  So an inheriting module need
    not list all the classes from its base module in order to change them
    by altering a base class in that module.

    Note: All the modules listed in '__bases__' must call 'setupModule()', even
    if they do not define a '__bases__' or desire module inheritance
    themselves.  This is because TransWarp cannot otherwise get access to
    their bytecode in a way that is compatible with the many "import hook"
    systems that exist for Python.  (E.g. running bytecode from zip files or
    frozen into an executable, etc.)

    Function Rebinding

        All functions inherited via "module inheritance" using 'setupModule()'
        (including those which are instance or class methods) have their
        globals rebound to point to the inheriting module.  This means that if
        a function or method references a global in the base module you're
        inheriting from, you can override that global in the inheriting module,
        without having to recode the function that referenced it.  (This is
        especially useful for 'super()' calls, which usually use global
        references to class names!)

        In addition to rebinding general globals, functions which reference
        the global name '__proceed__' are also specially rebound so that
        '__proceed__' is the previous definition of that function, if any, in
        the inheritance list.  (It is 'None' if there is no previous
        definition.)  This allows you to do the rough equivalent of a 'super()'
        call (or AspectJ "around advice") without having to explicitly import
        the old version of a function.  Note that '__proceed__' is always
        either a function or 'None', so you must include 'self' as a parameter
        when calling it from a method definition.

    Inheritance of Metaclass Constraints

        Python 2.2 enforces metaclass constraints for "new-style" classes.
        That is, it requires that a new class' metaclass be "compatible" with
        the metaclass of each of the base classes of the class, where
        "compatible" means "is the same as, or is a subclass of".

        Python, however, does not automatically generate such a metaclass for
        you.  You must ordinarily supply that metaclass yourself, either as
        an explicit '__metaclass__' definition, or by having one of the base
        classes supply a suitable metaclass.  This is fine for simple programs,
        where metaclasses are infrequently mixed, but more problematic for
        complex frameworks like TransWarp, where a variety of metaclasses are
        mixed and matched to supply various properties.

        So, using 'setupModule()' gives you an additional bonus: TransWarp
        will automatically generate the necessary metaclasses for you, so long
        as you use TransWarp's alternate API for specifying metaclasses.
        Please see the documentation of the 'makeClass' function in the
        'TW.Utils.Meta' module for more information about how this works.

        Please note that metaclasses are not combined *across* modules, unless
        they are specified with same-named 'class' statements in both modules.
        (In which case, they are combined because they are following the normal
        class combination rules of module inheritance, not because of anything
        to do with metaclasses.)

    Special Considerations for Mutables and Dynamic Initialization

        Both inheritance and advice are implemented by running hacked,
        module-level code under a "simulator" that intercepts the setting of
        variables.  This works great for static definitions like 'class'
        and 'def' statements, constant assignments, 'import', etc.  It also
        works reasonably well for many other kinds of static initialization
        of immutable objects
        
        Mutable values, however, may require special considerations.  For
        example, if a module sets up some kind of registry as a module-level
        variable, and an inheriting module overrides the definition, things
        can get tricky.  If the base module writes values into that registry as
        part of module initialization, those values will also be written into
        the registry defined by the derived module.

        Another possible issue is if the base module performs other externally
        visible, non-idempotent operations, such as registering classes or
        functions in another module's registry, printing things to the console,
        etc.  The simple workaround for all these considerations, however, is
        to move your dynamic initialization code to a module-level '__init__'
        function.

    Module-level '__init__()' Functions

        The last thing 'setupModule()' does before returning, is to check for a
        module-level '__init__()' function, and call it with no arguments, if
        it exists.  This allows you to do any dynamic initialization operations
        (such as modifying or resetting global mutables) *after* inheritance
        has taken effect.  As with any other function defined in the module,
        '__proceed__' refers to the previous (i.e. preceding base module)
        definition of the function or 'None'.  This lets you can chain to your
        predecessors' initialization code, if needed/desired.

        Note, by the way, that if you have an 'if __name__=="__main__"' block
        in your module, it would probably be best if you move it inside the
        '__init__()' function, as this ensures that it will not be run
        repeatedly if you do not wish it to be.  It will also allow other
        modules to inherit that code and wrap around it, if they so desire.
        

    To-do Items

        * The 'adviseModule()' API is as-yet untested, and 'setupModule()' is
          only lightly tested so far.  We need lots of test cases to make sure
          this thing is working right, because a *lot* of things are going to
          depend on it in future.

        * The simulator should issue warnings for a variety of questionable
          situations, such as...

          - Code matching the following pattern, which doesn't do what it looks
            like it does, and should probably be considered a "serious order
            disagreement"::

            BaseModule:

                class Foo: ...
                    
                class Bar: ...

            DerivedModule:

                class Bar: ...

                class Foo(Bar): ...

          - Module level 'del' of globals, mixing of 'def', 'class' and
            assignments to the same logical object...
                    
        * This docstring is woefully inadequate to describe all the interesting
          subtleties of module inheritance; a tutorial is really needed.  But
          there *does* need to be a reference-style explanation as well, that
          describes the precise semantics of interpretation for assignments,
          'def', and 'class', in modules running under simulator control.

        * Add 'LegacyModule("name")' and 'loadLegacyModule("name")' APIs to
          allow inheriting from and/or giving advice to modules which do not
          call 'setupModule()'.
"""


import sys
from types import ModuleType
__proceed__ = None
__all__ = ['adviseModule', 'setupModule', '__proceed__']

adviceMap = {}



































def getCodeListForModule(module, code=None):

    if hasattr(module,'__codeList__'):
        return module.__codeList__

    assert code is not None, ("Can't get codelist for %s" % module)

    name = module.__name__
    code = prepForSimulation(code)
    codeList = module.__codeList__ = adviceMap.get(name,[])+[code]

    bases = getattr(module,'__bases__',())
    if isinstance(bases,ModuleType):
        bases = bases,

    for baseModule in bases:
        if type(baseModule) is not ModuleType:
            raise TypeError (
                "%s is not a module in %s __bases__" % (baseModule,name)
            )
        for c in getCodeListForModule(baseModule):
            if c in codeList:
                codeList.remove(c)
            codeList.append(c)

    return codeList















def setupModule():

    """setupModule() - Build module, w/advice and inheritance

        'setupModule()' should be called only at the very end of a module's
        code.  This is because any code which follows 'setupModule()' will be
        executed twice.  (Actually, the code before 'setupModule()' gets
        executed twice, also, but the module dictionary is reset in between,
        so its execution is cleaner.)
    """

    frame = sys._getframe(1)
    dict = frame.f_globals

    if dict.has_key('__TW_Simulator__'):
        return

    code = frame.f_code
    name = dict['__name__']
    module = sys.modules[name]

    codelist = getCodeListForModule(module, code)
    
    saved = {}
    for name in '__file__', '__path__', '__name__', '__codeList__':
        try:
            saved[name] = dict[name]
        except KeyError:
            pass

    dict.clear(); dict.update(saved)    
    sim = Simulator(dict)   # Must happen after!

    # XXX Should we *not* do this if len(codelist)==1???
    map(sim.execute, codelist); sim.finish()
    
    if dict.has_key('__init__'):
        dict['__init__']()



def adviseModule(moduleName):

    frame = sys._getframe(1)
    dict = frame.f_globals

    if dict.has_key('__TW_Simulator__'):
        return

    if dict.has_key('__bases__'):
        raise SpecificationError(
            "Advice modules cannot use '__bases__'"
        )

    if sys.modules.has_key(moduleName):
        raise SpecificationError(
            "%s is already imported and cannot be advised" % moduleName
        )

    code = frame.f_code
    name = dict['__name__']
    module = sys.modules[name]

    codelist = getCodeListForModule(module, code)
    adviceMap.setdefault(moduleName, [])[0:0] = codelist

















from TW.Utils.Code import *

from TW.Utils.Code import BUILD_CLASS, STORE_NAME, MAKE_CLOSURE, \
    MAKE_FUNCTION, LOAD_CONST, STORE_GLOBAL, CALL_FUNCTION, IMPORT_STAR, \
    IMPORT_NAME, JUMP_ABSOLUTE, POP_TOP, ROT_FOUR, LOAD_ATTR, LOAD_GLOBAL, \
    LOAD_CONST, ROT_TWO, LOAD_LOCALS

from TW.Utils.Meta import makeClass
from sys import _getframe
































class Simulator:

    def __init__(self, dict):

        self.defined   = {}
        self.locked    = {}
        self.funcs     = {}
        self.lastFunc  = {}
        self.classes   = {}
        self.classPath = {}
        self.dict      = dict


    def execute(self, code):
        
        d = self.dict
        
        try:
            d['__TW_Simulator__'] = self
            exec code in d

        finally:
            del d['__TW_Simulator__']
            self.locked.update(self.defined)
            self.defined.clear()
            self.classPath.clear()

    def finish(self):
        for k,v in self.lastFunc.items():
            bind_func(v,__proceed__=None)
    

    def ASSIGN_VAR(self, value, qname):
        locked = self.locked
        if locked.has_key(qname):
            return locked[qname]
        self.defined[qname] = value
        return value



    def DEFINE_FUNCTION(self, value, qname):

        lastFunc, locked, funcs = self.lastFunc, self.locked, self.funcs

        if lastFunc.has_key(qname):
            bind_func(lastFunc[qname],__proceed__=value); del lastFunc[qname]
            
        if '__proceed__' in value.func_code.co_names:
            lastFunc[qname] = value

        if locked.has_key(qname):
            return locked[qname]

        if funcs.has_key(qname):
            return funcs[qname]

        funcs[qname] = value
        return value


    def IMPORT_STAR(self, module, locals, prefix):
        locked = self.locked
        have = locked.has_key
        defined = self.defined
        
        all = getattr(module,'__all__',None)
        
        if all is None:
            for k,v in module.__dict__.items():
                if not k.startswith('_'):
                    qname = prefix+k
                    if not have(qname):
                        locals[k] = defined[qname] = v
        else:
            for k in all:
                qname = prefix+k
                if not have(qname):
                    locals[k] = defined[qname] = getattr(module,k)



    def DEFINE_CLASS(self, name, bases, dict, qname):

        classes = self.classes
        get = self.classPath.get
        basePaths = tuple([get(id(base)) for base in bases])
        
        if classes.has_key(qname):
            
            oldClass, oldBases, oldPaths, oldDict = classes[qname]
            addBases = []; addBase = addBases.append
            addPaths = []; addPath = addPaths.append
            
            for b,p in zip(oldBases, oldPaths):
                if p is None or p not in basePaths:
                    addBase(classes.get(p,(b,))[0])
                    addPath(p)
            
            bases = tuple(addBases) + bases
            basePaths = tuple(addPaths) + basePaths

            have = dict.has_key
            for k,v in oldDict.items():
                if not have(k): dict[k]=v

        newClass = makeClass(name,bases,dict)
        classes[qname] = newClass, bases, basePaths, dict.copy()

        try:
            newClass.__module__ = self.dict['__name__']
        except:
            pass

        self.classPath[id(newClass)] = qname

        locked = self.locked
        if locked.has_key(qname):
            return locked[qname]

        return newClass
        

def prepForSimulation(code, path='', depth=0):

    code = Code(code)

    idx = code.index()
    opcode, operand, lineOf = idx.opcode, idx.operand, idx.byteLine
    offset = idx.offset

    name_index = code.name_index
    const_index = code.const_index

    Simulator = name_index('__TW_Simulator__')
    DefFunc   = name_index('DEFINE_FUNCTION')
    DefClass  = name_index('DEFINE_CLASS')
    Assign    = name_index('ASSIGN_VAR')
    ImpStar   = name_index('IMPORT_STAR')

    names   = code.co_names
    consts  = code.co_consts
    co_code = code.co_code
    
    emit = code.append
    patcher = code.iterFromEnd(); patch = patcher.write; go = patcher.go

    spc = '    ' * depth
















    ### Fix up IMPORT_STAR operations

    for i in idx.opcodeLocations[IMPORT_STAR]:

        backpatch = offset[i]
        line = lineOf[backpatch]
        
        assert opcode[i-1]== IMPORT_NAME, (
            "Unrecognized 'import *' at line %(line)d" % locals()
        )

        patchTarget = len(co_code)
        go(offset[i-1])
        patch(JUMP_ABSOLUTE, patchTarget, 0)
        
        # rewrite the IMPORT_NAME
        emit(IMPORT_NAME, operand[i-1])

        # Call __TW_Simulator__.IMPORT_STAR(module, locals, prefix)
        emit(LOAD_GLOBAL, Simulator)
        emit(LOAD_ATTR, ImpStar)
        emit(ROT_TWO)
        emit(LOAD_LOCALS)
        emit(LOAD_CONST, const_index(path))
        emit(CALL_FUNCTION, 3)
        emit(JUMP_ABSOLUTE, backpatch)

        # Replace IMPORT_STAR w/remove of the return val from IMPORT_STAR()
        co_code[offset[i]] = POP_TOP

        #print "%(line)04d import * (into %(path)s)" % locals()










    ### Fix up all other operation types

    for i in idx.opcodeLocations[STORE_NAME]+idx.opcodeLocations[STORE_GLOBAL]:

        op     = opcode[i]
        arg    = operand[i]
        prevOp = opcode[i-1]
        qname = name = names[arg]

        backpatch = offset[i]
        patchTarget = len(co_code)

        line = lineOf[backpatch]

        if path and opcode[i]==STORE_NAME:
            qname = path+name

        namArg = const_index(qname)
        
        # common prefix - get the simulator object
        emit(LOAD_GLOBAL, Simulator)




















        ### Handle class operations
        
        if prevOp == BUILD_CLASS:

            bind = "class"
            
            assert opcode[i-2]==CALL_FUNCTION and \
               opcode[i-3] in (MAKE_CLOSURE, MAKE_FUNCTION) and \
               opcode[i-4]==LOAD_CONST, (
                    "Unrecognized class %(qname)s at line %(line)d" % locals()
            )
            const = operand[i-4]
            suite = consts[const]
            consts[const] = prepForSimulation(suite, qname+'.', depth+1)

            backpatch -= 1  # back up to the BUILD_CLASS instruction...
            nextI = offset[i+1]
            
            # and fill up the space to the next instruction with POP_TOP, so
            # that if you disassemble the code it looks reasonable...
            
            for j in range(backpatch,nextI):
                co_code[j] = POP_TOP
                
            # get the DEFINE_CLAS method
            emit(LOAD_ATTR, DefClass)
            
            # Move it before the (name,bases,dict) args
            emit(ROT_FOUR)

            # Get the absolute name, and call method w/4 args
            emit(LOAD_CONST, namArg)
            emit(CALL_FUNCTION, 4)








        ### Non-class definition

        else:
            if prevOp in (MAKE_FUNCTION, MAKE_CLOSURE):
                bind = "def"
                # get the DEFINE_FUNCTION method
                emit(LOAD_ATTR, DefFunc)
            else:
                bind = "assign"
                # get the ASSIGN_VAR method
                emit(LOAD_ATTR, Assign)
            
            # Move it before the value, get the absolute name, and call method
            emit(ROT_TWO)
            emit(LOAD_CONST, namArg)
            emit(CALL_FUNCTION, 2)
            


        # Common patch epilog
        
        go(backpatch)
        patch(JUMP_ABSOLUTE, patchTarget, 0)
        
        emit(op, arg)
        emit(JUMP_ABSOLUTE, offset[i+1])
        
        #print "%(line)04d %(spc)s%(bind)s %(qname)s" % locals()

    code.co_stacksize += 5  # add a little margin for error
    return code.code()


bind_func(prepForSimulation, **globals())
bind_func(prepForSimulation, **getattr(__builtins__,'__dict__',__builtins__))






if __name__=='__main__':
    from glob import glob
    for file in glob('ick.py'):
        print
        print "File: %s" % file,
        source = open(file,'r').read().rstrip()+'\n'
        try:
            code = compile(source,file,'exec')
        except SyntaxError:
            print "Syntax Error!"
        else:
            print
        code = prepForSimulation(code)
    print

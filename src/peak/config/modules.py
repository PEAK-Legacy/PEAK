"""Module Inheritance and Patching

    The APIs defined here let you create modules which derive from other
    modules, by defining a module-level '__bases__' attribute which lists
    the modules you wish to inherit from.  For example::

        from peak.api import *

        import BaseModule1, BaseModule2

        __bases__ = BaseModule1, BaseModule2

       
        class MyClass:
            ...

        binding.setupModule()

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
    themselves.  This is because PEAK cannot otherwise get access to
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


    Pickling Instances of Nested Classes and the '__name__' Attribute

        One more bonus of using 'setupModule()' is that instances of nested
        classes defined in modules using 'setupModule()' will be pickleable.
        Ordinarily, nested class instances aren't pickleable because Python
        doesn't know how to find them, using only 'someClass.__name__' and
        'someClass.__module__'.

        PEAK overcomes this problem by renaming nested classes so that
        they are defined with their full dotted name (e.g. 'Foo.Bar' for
        class 'Bar' nested in class 'Foo'), and saving a reference to the class
        under its dotted name in the module dictionary.  This means that
        'someClass.__name__' may not be what you'd normally expect, and that
        doing 'del someClass' may not delete all references to a class.  But
        pickling and unpickling should work normally.

        Note that some PEAK classes and metaclasses provide a "short
        form" of the class name for use when appropriate.  For example,
        Feature classes have an 'attrName' class attribute.  In a pinch, you
        can also use '__name__.split(".")[-1]' to get the undotted form of
        a class' name.

    Special Considerations for Mutables and Dynamic Initialization

        Both inheritance and patching are implemented by running hacked,
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

        * This docstring is woefully inadequate to describe all the interesting
          subtleties of module inheritance; a tutorial is really needed.  But
          there *does* need to be a reference-style explanation as well, that
          describes the precise semantics of interpretation for assignments,
          'def', and 'class', in modules running under simulator control.

        * Add 'LegacyModule("name")' and 'loadLegacyModule("name")' APIs to
          allow inheriting from and/or patching modules which do not
          call 'setupModule()'.
"""














import sys
from types import ModuleType


# Make the default value of '__proceed__' a built-in, so that code written for
# an inheriting module won't fail with a NameError if there's no base module
# definition of a function

import __builtin__; __builtin__.__proceed__ = None


__all__ = [
    'patchModule', 'setupModule', 'setupObject', 'ModuleInheritanceWarning'
]

patchMap = {}


def setupObject(obj, **attrs):

    """Set attributes without overwriting values defined in a derived module"""

    for k,v in attrs.items():
        if not hasattr(obj,k):
            setattr(obj,k,v)
















def getCodeListForModule(module, code=None):

    if hasattr(module,'__codeList__'):
        return module.__codeList__

    assert code is not None, ("Can't get codelist for %s" % module)

    name = module.__name__
    code = prepForSimulation(code)
    codeList = module.__codeList__ = patchMap.get(name,[])+[code]

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

    """setupModule() - Build module, w/patches and inheritance

        'setupModule()' should be called only at the very end of a module's
        code.  This is because any code which follows 'setupModule()' will be
        executed twice.  (Actually, the code before 'setupModule()' gets
        executed twice, also, but the module dictionary is reset in between,
        so its execution is cleaner.)
    """

    frame = sys._getframe(1)
    dict = frame.f_globals

    if dict.has_key('__PEAK_Simulator__'):
        return

    code = frame.f_code
    name = dict['__name__']
    module = sys.modules[name]

    codelist = getCodeListForModule(module, code)
    
    if len(codelist)>1:
        saved = {}
        for name in '__file__', '__path__', '__name__', '__codeList__':
            try:
                saved[name] = dict[name]
            except KeyError:
                pass

        dict.clear(); dict.update(saved)    
        sim = Simulator(dict)   # Must happen after!

        map(sim.execute, codelist); sim.finish()
    
    if dict.has_key('__init__'):
        dict['__init__']()



def patchModule(moduleName):

    """"Patch" a module - like a runtime (aka "monkey") patch, only better

        Usage::
            from peak.api import *

            ...

            patchModule('moduleToPatch')

    'patchModule()' works much like 'setupModule()'.  The main difference
    is that it applies the current module as a patch to the supplied module
    name.  The module to be patched must not have been imported yet, and it
    must call 'setupModule()'.  The result will be as though the patched
    module had been replaced with a derived module, using the standard module
    inheritance rules to derive the new module.

    Note that more than one patching module may patch a single target module,
    in which case the order of importing is significant.  Patch modules
    imported later take precedence over those imported earlier.  (The target
    module must always be imported last.)

    Patch modules may patch other patch modules, but there is little point
    to doing this, since both patch modules will still have to be explicitly
    imported before their mutual target for the patches to take effect.
    """    

    frame = sys._getframe(1)
    dict = frame.f_globals

    if dict.has_key('__PEAK_Simulator__'):
        return

    if dict.has_key('__bases__'):
        raise SpecificationError(
            "Patch modules cannot use '__bases__'"
        )



    if sys.modules.has_key(moduleName):
        raise SpecificationError(
            "%s is already imported and cannot be patched" % moduleName
        )

    code = frame.f_code
    name = dict['__name__']
    module = sys.modules[name]

    codelist = getCodeListForModule(module, code)
    patchMap.setdefault(moduleName, [])[0:0] = codelist



from peak.util.Code import *

from peak.util.Code import BUILD_CLASS, STORE_NAME, MAKE_CLOSURE, \
    MAKE_FUNCTION, LOAD_CONST, STORE_GLOBAL, CALL_FUNCTION, IMPORT_STAR, \
    IMPORT_NAME, JUMP_ABSOLUTE, POP_TOP, ROT_FOUR, LOAD_ATTR, LOAD_GLOBAL, \
    LOAD_CONST, ROT_TWO, LOAD_LOCALS, STORE_SLICE, DELETE_SLICE, STORE_ATTR, \
    STORE_SUBSCR, DELETE_SUBSCR, DELETE_ATTR, DELETE_NAME, DELETE_GLOBAL

from peak.util.Meta import makeClass
from sys import _getframe
from warnings import warn, warn_explicit

class ModuleInheritanceWarning(UserWarning):
    pass

mutableOps = (
    STORE_SLICE,  STORE_SLICE+1,  STORE_SLICE+2,  STORE_SLICE+3,
    DELETE_SLICE, DELETE_SLICE+1, DELETE_SLICE+2, DELETE_SLICE+3,
    STORE_ATTR,   DELETE_ATTR,    STORE_SUBSCR,   DELETE_SUBSCR,
)







class Simulator:

    def __init__(self, dict):

        self.defined   = {}
        self.locked    = {}
        self.funcs     = {}
        self.lastFunc  = {}
        self.classes   = {}
        self.classPath = {}
        self.setKind   = {}
        self.dict      = dict

    def execute(self, code):
        
        d = self.dict
        
        try:
            d['__PEAK_Simulator__'] = self
            exec code in d

        finally:
            del d['__PEAK_Simulator__']
            self.locked.update(self.defined)
            self.defined.clear()
            self.setKind.clear()
            self.classPath.clear()

    def finish(self):
        for k,v in self.lastFunc.items():
            bind_func(v,__proceed__=None)










    def ASSIGN_VAR(self, value, qname):

        locked = self.locked

        if locked.has_key(qname):

            if self.setKind.get(qname)==STORE_NAME:
                warn(
                    "Redefinition of variable locked by derived module",
                    ModuleInheritanceWarning, 2
                )

            return locked[qname]

        self.defined[qname] = value
        self.setKind[qname] = STORE_NAME
        return value
























    def DEFINE_FUNCTION(self, value, qname):

        if self.setKind.get(qname,IMPORT_STAR) != IMPORT_STAR:
            warn(
                ("Redefinition of %s" % qname),
                ModuleInheritanceWarning, 2
            )

        self.setKind[qname] = MAKE_FUNCTION

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
        setKind = self.setKind
        checkKind = setKind.get

        def warnIfOverwrite(qname):
            if checkKind(qname,IMPORT_STAR) != IMPORT_STAR:
                warn(
                    ("%s may be overwritten by 'import *'" % qname),
                    ModuleInheritanceWarning, 3
                )
            setKind[qname]=IMPORT_STAR

        all = getattr(module,'__all__',None)
        
        if all is None:

            for k,v in module.__dict__.items():
                if not k.startswith('_'):
                    qname = prefix+k
                    if not have(qname):
                        warnIfOverwrite(qname)
                        locals[k] = defined[qname] = v

        else:
            for k in all:
                qname = prefix+k
                warnIfOverwrite(qname)
                if not have(qname):
                    warnIfOverwrite(qname)
                    locals[k] = defined[qname] = getattr(module,k)







    def DEFINE_CLASS(self, name, bases, cdict, qname):

        if self.setKind.get(qname,IMPORT_STAR) != IMPORT_STAR:
            warn(
                ("Redefinition of %s" % qname),
                ModuleInheritanceWarning, 2
            )

        self.setKind[qname] = BUILD_CLASS

        classes = self.classes
        get = self.classPath.get
        oldDPaths = []
        basePaths = tuple([get(id(base)) for base in bases])
        dictPaths = [(k,get(id(v))) for (k,v) in cdict.items() if get(id(v))]

        if classes.has_key(qname):
            
            oldClass, oldBases, oldPaths, oldItems, oldDPaths = classes[qname]
            addBases = []; addBase = addBases.append
            addPaths = []; addPath = addPaths.append
            
            for b,p in zip(oldBases, oldPaths):
                if p is None or p not in basePaths:
                    addBase(classes.get(p,(b,))[0])
                    addPath(p)
            
            bases = tuple(addBases) + bases
            basePaths = tuple(addPaths) + basePaths

            have = cdict.has_key
            for k,v in oldItems:
                if not have(k): cdict[k]=v

            for k,v in oldDPaths:
                cdict[k] = classes[v][0]

        cdict['__name__'] = qname
        newClass = makeClass(qname,bases,cdict)


        classes[qname] = newClass, bases, basePaths, cdict.items(), \
            dict(dictPaths+oldDPaths).items()

        # Make sure that module and name are correct for pickling

        newClass.__module__ = self.dict['__name__']
        self.classPath[id(newClass)] = qname

        locked = self.locked
        if locked.has_key(qname):
            return locked[qname]

        # Save the class where pickle can find it
        self.dict[qname] = newClass

        return newClass
        
























def prepForSimulation(code, path='', depth=0):

    code = Code(code)
    idx = code.index()
    opcode, operand, lineOf = idx.opcode, idx.operand, idx.byteLine
    offset = idx.offset
    name_index = code.name_index
    const_index = code.const_index

    Simulator = name_index('__PEAK_Simulator__')
    DefFunc   = name_index('DEFINE_FUNCTION')
    DefClass  = name_index('DEFINE_CLASS')
    Assign    = name_index('ASSIGN_VAR')
    ImpStar   = name_index('IMPORT_STAR')

    names   = code.co_names
    consts  = code.co_consts
    co_code = code.co_code
    
    emit = code.append
    patcher = iter(code); patch = patcher.write; go = patcher.go
    spc = '    ' * depth

    for op in mutableOps:
        for i in idx.opcodeLocations[op]:
            warn_explicit(
                "Modification to mutable during initialization",
                ModuleInheritanceWarning,
                code.co_filename,
                lineOf[offset[i]],
            )

    for op in (DELETE_NAME, DELETE_GLOBAL):
        for i in idx.opcodeLocations[op]:
            warn_explicit(
                "Deletion of global during initialization",
                ModuleInheritanceWarning,
                code.co_filename,
                lineOf[offset[i]],
            )

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

        # Call __PEAK_Simulator__.IMPORT_STAR(module, locals, prefix)
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

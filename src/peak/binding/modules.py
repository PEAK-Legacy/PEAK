"""Module Inheritance and Module Advice

    The APIs defined here let you create modules which "subclass" other
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
    and metaclass constraints are inherited.  So a "subclassing module" need
    not list all the classes from its "base module" in order to change them
    by altering a base class in that module.

    Function Rebinding

        One extra advantage of using 'setupModule()' is that all functions
        (including those which are methods) have their globals rebound to point
        to the destination module.  This means that if a function or method
        references a global in the module you're inheriting from, you can
        override that global in the "subclass module", without having to recode
        the function that referenced it.

        In addition to rebinding general globals, functions which reference
        the global name '__proceed__' are also specially rebound so that
        '__proceed__' is the previous definition of the function, if any, in
        the inheritance list.  (It is 'None' if there is no previous
        definition.)  This allows you to do the rough equivalent of a "super"
        call (or AspectJ "around advice") without having to explicitly import
        the old version of a function.  Note that '__proceed__' is always
        either a function or 'None', so you must include 'self' as a parameter
        when calling it from a method.


    Special Considerations for Mutables and Dynamic Initialization

        Both inheritance and advice are implemented by running hacked,
        module-level code under a "simulator" that intercepts the setting of
        variables.  This works great for static definitions like 'class'
        and 'def' statements, constant assignments, 'import', etc.  It also
        works reasonably well for many other kinds of static initialization
        of immutable objects
        
        Mutable values, however, may require special considerations.  For
        example, if a module sets up some kind of registry as a module-level
        variable, and an inheriting module doesn't want to share that registry,
        things can get tricky.  If the "superclass module" writes values into
        that registry as part of module initialization, those values will also
        be written into the registry defined by the "subclass module".

        The simple workaround for these considerations, however, is to move
        your dynamic initialization code to a module-level '__init__' function.


    Module-level '__init__()' Functions

        The last thing 'setupModule()' does before returning is check for a
        module-level '__init__()' function, and calls it with no arguments, if
        it exists.  This allows you to do any dynamic initialization operations
        (such as modifying or resetting global mutables) *after* inheritance
        has taken effect.  As with any other function defined in the module,
        '__proceed__' refers to the previous (i.e. "superclass module")
        definition of the function or 'None'.  This lets you can chain to your
        predecessors' initialization code, if needed/desired.

        Note, by the way, that if you have an 'if __name__=="__main__"' block
        in your module, it should move inside the '__init__()' function for
        best results.
        
    Where to Find More Information on...

        Inheritance of Metaclass Constraints -- the Python 2.2 metaclass
            tutorial explains the concept of metaclass constraints, and notes
            that Python 2.2 checks that metaclasses conform, but does not
            automatically generate a metaclass if none is present.  TransWarp,
            however, *does* do this when you use 'setupModule()'.  See
            'TW.Utils.Meta' for the implementation, and the book "Putting
            Metaclasses To Work" for the theory.

        How Module Inheritance Works -- See 'TW.Utils.Simulator' for all the
            low-down dirty details of how the bytecode is hacked and how the
            "simulator" actually implements the various namespace alterations.


    To-do Items

        * The 'adviseModule()' API is as-yet untested, and 'setupModule()' is
          only lightly tested so far.  We need lots of test cases to make sure
          this thing is working right, because a *lot* of things are going to
          depend on it in future.

        * This docstring is woefully inadequate to describe all the interesting
          subtleties of module inheritance; a tutorial is really needed.  But
          there *does* need to be a reference-style explanation as well.

        * Add 'LegacyModule("name")' and 'loadLegacyModule("name")' APIs to
          allow inheriting from and/or giving advice to modules which do not
          call 'setupModule()'.
"""


from TW.Utils.Simulator import Simulator, prepForSimulation
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
    
    for baseModule in getattr(module,'__bases__',()):
        if type(baseModule) is not ModuleType:
            raise TypeError (
                "%s is not a module in %s __bases__" % (m,name)
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


















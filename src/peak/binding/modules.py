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
    and 'BaseModule2' into TransWarp component specifications, add them
    together (in reverse order), and then build the resulting recipe, rewriting
    the calling module's dictionary.  The result is rather like normal class
    inheritance, except that classes (even nested classes) are merged by name
    following TransWarp's normal build rules.  So a "subclassing module" need
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

        Another important thing to note is that function rebinding is only
        applied to *functions*.  This means that if you are using 'property'
        (in 2.2) or 'ComputedAttribute' (from 'ExtensionClass'), you must
        define the 'ComputedAttribute' or 'property' using 'Eval()' in order
        to ensure that it is created from the rebound function.  Examples::

            # 2.2 non-shadowing property example
            
            class aClass(object):

                def _get_x(self):
                    return __proceed__(self) * 10

                def _set_x(self, x):
                    __proceed__(self, x/10)

                x = Eval("property(_get_x,_set_x)", globals())


            # ComputedAttribute shadowing example

            class Class2(ExtensionClass.Base):

                def x(self):
                    return self.foo + 50

                x += Eval("ComputedAttribute(__previous__)", globals())


            # 2.2 get-property shadowing example

            class Class3(object):

                def x(self):
                    return self.foo + 50

                x += Eval("property(__previous__)", globals())


            # 2.2 staticmethod shadowing example

            class Class4(object):

                def aMethod(foo, bar, baz):
                    return foo+bar*baz

                aMethod += Eval("staticmethod(__previous__)", globals())


        In the second and following examples, we add the 'Eval()' to the
        function, and use '__previous__' to access it.  This is because we
        want the function to be overwritten by the attribute descriptor in the
        output class.  Note that you can still use this technique with a
        property that has more than just a getter method; you would then
        use something like 'Eval("property(__previous__,setter)",globals())'
        instead.

    To-do Items

        * The 'adviseModule()' API is as-yet untested, and setupModule() is
          only lightly tested so far.

        * Function rebinding perhaps belongs in the core API, since the
          '__proceed__' rebinding would allow functions to be "around advice"
          by default.  But since this is very new code, and since it would
          also impose an extra 'isinstance()' check on *every* build target,
          perhaps it's best to wait awhile.  Of course, right now you could
          force function rebinding against a particular target by importing
          'TW.API.Modules.DefaultFunctionInterpreter' and adding it to the
          crosscut of the function(s) you desired rebound.

        * The 'x += Eval("whatever(__previous__)")' syntax sucks.  When we
          go to full 2.2 support, there should be some sugar for this, e.g.
          'x += MakeProperty' or 'x += MakeStatic'.  Or maybe the whole thing
          will be moot due to metaclasses.  We'll have to see how it goes.
"""

from TW.API import *
from TW.Utils.ClassTypes import isClass

import sys
from types import ModuleType, FunctionType

__all__ = ['adviseModule', 'setupModule']

adviceMap = {}

emptyRecipe = Recipe()


def getSpecForModule(module):

    if hasattr(module,'__specification__'):
        return module.__specification__

    # build an empty template, using module dict, w/no name
    # __globals__ = module dict

    md = module.__dict__
    name = module.__name__

    d = md.copy()
    d['__globals__'] = md       # XXX still needs function-rebuild support
    
    return Template('', (), d)













def setupModule(dict=None):

    """setupModule(globals()) - Build module, w/advice and inheritance

        The 'setupModule()' call is usually made towards the end of a module's
        code, after all the necessary classes and functions are defined, but
        before any 'if __name__=="__main__"' standalone code.  About the only
        time one should have definitions after 'setupModule()' is when a module
        wants to be "abstract", but provide a default implementation if no
        advice generates an actual implementation.  In these cases, the module
        will call 'setupModule()' first, then check to see if the desired
        globals are present.  If not, it can then implement default ones, and
        run 'setupModule()' again.
    """

    if dict is None:
        from TW.Utils.Misc import getCallerInfo
        name,line_no = getCallerInfo()
        module = sys.modules[name]
        dict = module.__dict__

    else:
        name = dict['__name__']
        module = sys.modules[name]

    bases = []
    inputBases = dict.get('__bases__', ())
    if isinstance(inputBases,ModuleType):
        inputBases = (inputBases,)

    for m in (module,) + tuple(inputBases):
        if not isinstance(m,ModuleType):
            raise TypeError, ("%s is not a module in %s __bases__" % (m,name))
        bases.append(getSpecForModule(m))
        bases.append(adviceForModule(m.__name__))

    bases.reverse()
    spec = Recipe(ModuleDictInterpreter, *tuple(bases))
    dict.clear(); dict.update(spec(FunctionRebindingBuildTarget, globals=dict))
    dict['__specification__'] = spec    # save module spec

def adviseModule(moduleName, withDict=None):

    if withDict is None:
        from TW.Utils.Misc import getCallerInfo
        name,line_no = getCallerInfo()
        module = sys.modules[name]
        withDict = module.__dict__

    else:
        name = withDict['__name__']
        module = sys.modules[name]

    if withDict.has_key('__bases__'):
        raise SpecificationError(
            "Advice modules cannot use '__bases__'"
        )

    if sys.modules.has_key(moduleName):
        raise SpecificationError(
            "%s is already imported and cannot be advised" % moduleName
        )

    a = adviceForModule(moduleName)
    adviceMap[moduleName] = adviceForModule(moduleName) + \
                            getSpecForModule(module) + \
                            adviceForModule(name)


def adviceForModule(moduleName):
    return adviceMap.get(moduleName,emptyRecipe)











from Targets import BuildTarget

class FunctionRebindingBuildTarget(BuildTarget):

    def DEFAULT(self, spec, peerContext):

        if self.defaultInterpreter:

            if isClass(spec):
                self.interpreter = DefaultComponentInterpreter

            elif isinstance(spec,FunctionType):
                self.interpreter = DefaultFunctionInterpreter

            else:
                self.interpreter = DefaultInterpreter

        self.specs.append((spec,peerContext))























from Interpreters import *
from TW.Utils.Code import Function, FunctionBinder

class FunctionInterpreter(AbstractInterpreter):

    """Rebinds function globals and '__proceed__' to call next function"""

    def __call__(self, buildTarget, specList):

        if not specList:
            return UNDEFINED

        spec, pC = specList[-1]

        f_globals = spec.func_globals
        code = spec.func_code

        if pC.get(id(f_globals),'')=='__globals__':
            spec = Function(spec)
            spec.func_globals = buildTarget.getEnvironment('globals',f_globals)
            code = spec

        if '__proceed__' in code.co_names:

            if len(specList)>1:
                prevFunc = self(buildTarget, specList[:-1])
            else:
                prevFunc = None  # so function can detect end-of-chain

            spec = FunctionBinder(spec).boundFunc(__proceed__ = prevFunc)

        if type(spec) is Function: # XXX 2.1 backport hack; (isinstance)
            spec = spec.func()

        return spec

DefaultFunctionInterpreter = FunctionInterpreter()




class _ModuleDictInterpreter(AbstractInterpreter):

    def __call__(self, buildTarget, specList):
    
        for (spec,pC) in specList:

            if isSpecification(spec):
                name, bases, dict = spec.getTypeConstructorInfo()
                
            elif isinstance(spec,ModuleType):
                dict  = spec.__dict__.copy()

            else:
                raise SpecificationError(
                    "Invalid module specification for %s: %s" % (buildTarget,`spec`)
                )

            items = dict.items(); peerContext = {}
            for (name,spec) in items:
                peerContext[id(spec)] = name
                
            implementFeature = buildTarget.implementFeature
            moduleName = dict['__name__']

            for name,spec in items:
                if isClass(spec) and spec.__module__<>moduleName:
                    # Don't interpret external classes!
                    spec = Overwrite(spec)  # XXX might not work right :(

                implementFeature(name, spec, peerContext)

        dict  = {}
        for name, target in buildTarget.items():
            item = target.getOutput()
            if item is not UNDEFINED:
                dict[name] = item

        return dict
        
ModuleDictInterpreter = _ModuleDictInterpreter()


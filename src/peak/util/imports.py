"""Tools for doing dynamic imports"""

__all__ = [
    'importString', 'importObject', 'importSequence', 'importSuite',
    'lazyModule', 'joinPath', 'whenImported', 'getModuleHooks',
]

import __main__
defaultGlobalDict = __main__.__dict__

from types import StringTypes, ModuleType
from sys import modules
from peak.util.EigenData import AlreadyRead


def importSuite(specs, globalDict=defaultGlobalDict):

    """Create a test suite from import specs"""

    from unittest import TestSuite

    return TestSuite(
        [t() for t in importSequence(specs,globalDict)]
    )

def joinPath(modname, relativePath):

    """Adjust a module name by a '/'-separated, relative or absolute path"""

    module = modname.split('.')
    for p in relativePath.split('/'):

        if p=='..':
            module.pop()
        elif not p:
            module = []
        elif p!='.':
            module.append(p)

    return '.'.join(module)

def importString(name, globalDict=defaultGlobalDict):

    """Import an item specified by a string

        Example Usage::

            attribute1 = importString('some.module.attribute1')
            attribute2 = importString('other.module.nested.attribute2')

        'importString' imports an object from a module, according to an
        import specification string: a dot-delimited path to an object
        in the Python package namespace.  For example, the string
        '"some.module.attribute"' is equivalent to the result of
        'from some.module import attribute'.
    """

    if ':' in name:
        name = name.replace(':','.')

    path  = []

    for part in filter(None,name.split('.')):

        if path:

            try:
                item = getattr(item, part)
                path.append(part)
                continue

            except AttributeError:
                pass

        path.append(part)
        item = __import__('.'.join(path), globalDict, globalDict, [part])

    return item




def lazyModule(modname, relativePath=None):

    """Return module 'modname', but with its contents loaded "on demand"

    This function returns 'sys.modules[modname]', if present.  Otherwise
    it creates a 'LazyModule' object for the specified module, caches it
    in 'sys.modules', and returns it.

    'LazyModule' is a subclass of the standard Python module type, that
    remains empty until an attempt is made to access one of its
    attributes.  At that moment, the module is loaded into memory, and
    any hooks that were defined via 'whenImported()' are invoked.

    Note that calling 'lazyModule' with the name of a non-existent or
    unimportable module will delay the 'ImportError' until the moment
    access is attempted.  The 'ImportError' will occur every time an
    attribute access is attempted, until the problem is corrected.

    This function also takes an optional second parameter, 'relativePath',
    which will be interpreted as a '/'-separated path string relative to
    'modname'.  If a 'relativePath' is supplied, the module found by
    traversing the path will be loaded instead of 'modname'.  In the path,
    '.' refers to the current module, and '..' to the current module's
    parent.  For example::

        fooBaz = lazyModule('foo.bar','../baz')

    will return the module 'foo.baz'.  The main use of the 'relativePath'
    feature is to allow relative imports in modules that are intended for
    use with module inheritance.  Where an absolute import would be carried
    over as-is into the inheriting module, an import relative to '__name__'
    will be relative to the inheriting module, e.g.::

        something = lazyModule(__name__,'../path/to/something')

    The above code will have different results in each module that inherits
    it.

    (Note: 'relativePath' can also be an absolute path (starting with '/');
    this is mainly useful for module '__bases__' lists.)"""

    class LazyModule(ModuleType):

        __slots__=()
        
        def __init__(self, name):
            self.__name__ = name    # Fixes 2.2 not setting __name__ on create

        def __getattribute__(self,attr):
            if '.' in modname:
                # ensure parent is in sys.modules and parent.modname=self
                splitpos = modname.rindex('.')
                mod = importString(modname[:splitpos])
                setattr(mod,modname[splitpos+1:],self)
                
            oldGA = LazyModule.__getattribute__
            modGA = ModuleType.__getattribute__
            LazyModule.__getattribute__ = modGA

            try:
                # Get Python (or supplied 'reload') to do the real import!
                _loadAndRunHooks(self)
            except:
                # Reset our state so that we can retry later
                LazyModule.__getattribute__ = oldGA
                raise

            try:
                # Convert to a real module (if under 2.2)
                self.__class__ = ModuleType
            except TypeError:
                pass    # 2.3 will fail, but no big deal

            # Finish off by returning what was asked for
            return modGA(self,attr)


    if relativePath:
        modname = joinPath(modname, relativePath)



    if modname not in modules:
        modules[modname] = LazyModule(modname)

    return modules[modname]


postLoadHooks = {}


def _loadAndRunHooks(module):

    """Load an unactivated "lazy" module object"""

    # if this fails, we haven't called the hooks, so leave them in place
    # for possible retry of import
    
    reload(module)  

    try:
        for hook in getModuleHooks(module.__name__):
            hook(module)

    finally:
        # Ensure hooks are not called again, even if they fail
        postLoadHooks[module.__name__] = None



def getModuleHooks(moduleName):

    """Get list of hooks for 'moduleName'; error if module already loaded"""

    hooks = postLoadHooks.setdefault(moduleName,[])

    if hooks is None:
        raise AlreadyRead("Module already imported", moduleName)

    return hooks



def whenImported(moduleName, hook):

    """Call 'hook(module)' when module named 'moduleName' is first used

    The module must not have been previously imported, or 'AlreadyRead'
    is raised.  'moduleName' is a string containing a fully qualified
    module name.  'hook' must accept one argument: the imported module
    object.

    This function's name is a slight misnomer...  hooks are called when
    a module is first *used*, not when it is imported.

    This function returns 'lazyModule(moduleName)', in case you need
    the module object for future use."""

    if name in sys.modules and not name in postLoadHooks:
        raise AlreadyRead("Module already imported", name)
        
    getModuleHooks(moduleName).append(hook)
    return lazyModule(moduleName, reloader=_runHooks)





















def importObject(spec, globalDict=defaultGlobalDict):

    """Convert a possible string specifier to an object

    If 'spec' is a string or unicode object, import it using 'importString()',
    otherwise return it as-is.
    """
    
    if isinstance(spec,StringTypes):
        return importString(spec, globalDict)

    return spec


def importSequence(specs, globalDict=defaultGlobalDict):

    """Convert a string or list specifier to a list of objects.

    If 'specs' is a string or unicode object, treat it as a
    comma-separated list of import specifications, and return a
    list of the imported objects.

    If the result is not a string but is iterable, return a list
    with any string/unicode items replaced with their corresponding
    imports.
    """
    
    if isinstance(specs,StringTypes):
        return [importString(x.strip(),globalDict) for x in specs.split(',')]
    else:
        return [importObject(s,globalDict) for s in specs]

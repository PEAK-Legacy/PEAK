"""Tools for doing dynamic imports"""

__all__ = [
    'importString', 'importObject', 'importSequence', 'importSuite',
    'lazyModule', 'joinPath',
]

import __main__
defaultGlobalDict = __main__.__dict__


from types import StringTypes, ModuleType
from sys import modules


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
            attribute2 = importString('other.module:nested.attribute2')

        'importString' imports an object from a module, according to an
        import specification string: a dot-delimited path to an object
        in the Python package namespace.  For example, the string
        '"some.module.attribute"' is equivalent to the result of
        'from some.module import attribute'.

        If you need to access a sub-object of an imported object, use
        use '":"' to seperate the attribute spec from the module name.  In
        other words, '"other.module:nested.attribute"' is equivalent
        to 'from other.module import nested; nested.attribute'.

        If you want just the module itself, simply give its full dotted name.
    """

    if ':' in name:
        name = name.split(':',1)
        module = name[0]
        path = name[1].split('.')
    elif '.' in name:
        name = name.split('.')
        module = '.'.join(name[:-1])
        path = name[-1:]
    else:
        module, path = name, []

    item = __import__(module, globalDict, locals(), path[:1])

    for name in path:
        if name: item = getattr(item,name)

    return item


def lazyModule(modname, relativePath=None, reloader=reload):

    """Return module 'modname', but with its contents loaded "on demand"

    This function returns 'sys.modules[modname]', if present.  Otherwise
    it creates a 'LazyModule' object for the specified module, caches it
    in 'sys.modules', and returns it.

    'LazyModule' is a subclass of the standard Python module type, that
    remains empty until an attempt is made to access one of its
    attributes.  At that moment, the module is loaded into memory.

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
    this is mainly useful for module '__bases__' lists.)

    Finally, this function also accepts a third, optional parameter: a
    function to be used in place of the Python 'reload()' built-in.
    This can be used to trigger an action when the module is actually
    loaded.  This only takes effect if the call to 'lazyModule()'
    occurs is the first for the named module, and the module issn't
    already in 'sys.modules'."""

    class LazyModule(ModuleType):

        __slots__=()
        
        def __init__(self, name):
            self.__name__ = name    # Fixes 2.2 not setting __name__ on create

        def __getattribute__(self,attr):
            if '.' in modname:
                # ensure parent is in sys.modules and parent.modname=self
                splitpos = modname.rindex('.')
                mod = importString(modname[:splitpos]+':')
                setattr(mod,modname[splitpos+1:],self)
                
            oldGA = LazyModule.__getattribute__
            modGA = ModuleType.__getattribute__
            LazyModule.__getattribute__ = modGA

            try:
                # Get Python (or supplied 'reload') to do the real import!
                reloader(self)
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

    elif reloader is not reload:
        raise AssertionError(
            "Custom reloader specified, but module already loaded",
            modname
        )

    return modules[modname]




























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

"""Tools for doing dynamic imports"""

from types import StringTypes






































def importString(name, globalDict=None):
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

    item = __import__(module, globalDict or globals(), locals(), path[:1])

    for name in path:
        if name: item = getattr(item,name)

    return item


class lazyImport:

    """Proxy standing in for something that shouldn't import until later

        Example::
        
            aModule = lazyImport('somePackage.aModule:')
        
        Usage is like 'importString()', it just doesn't actually import
        the item until you try to access an attribute of it.  Note that
        you can't use this in situations where you need the real object!
        That is, if you need a real module (as is needed for a module's
        '__bases__' list), you can't use this.  But if all you need is
        to access attributes of the module, this will do just fine.
    """

    needsToImport = 1

    def __init__(self, what):
        self.what = what

    def __getattr__(self, attr):

        if self.needsToImport:
            self.what = importString(self.what)
            self.needsToImport = 0

        return getattr(self.what, attr)













def importObject(spec, globalDict=None):
    """Convert a possible string specifier to an object

    If 'spec' is a string or unicode object, import it using 'importString()',
    otherwise return it as-is.
    """
    
    if isinstance(spec,StringTypes):
        return importString(spec, globalDict)

    return spec


def importSequence(specs, globalDict=None):
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

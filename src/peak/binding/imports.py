"""Tools for doing dynamic imports"""

def importString(name):

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
    """

    if ':' in name:
        name = name.split(':',1)
        module = name[0]
        path = name[1].split('.')
    else:
        name = name.split('.')
        module = name[:-1].join('.')
        path = name[-1:]

    item = __import__(module,globals(),locals(),path[0])
    for name in path: item = getattr(item,name)

    return item

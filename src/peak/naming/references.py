"""Specialized references"""

__all__ = ['LinkRef', 'NNS_Reference']


class LinkRef(object):

    """Symbolic link"""

    __slots__ = 'linkName'
    
    def __init__(self, linkName):
        self.linkName = linkName

    def __repr__(self):
        return "LinkRef(%s)" % `self.linkName`


class NNS_Reference(object):

    """Next Naming System reference"""

    __slots__ = 'relativeTo'
    
    def __init__(self, relativeTo):
        self.relativeTo = relativeTo

    def __repr__(self):
        return "NNS_Reference(%s)" % `self.relativeTo`


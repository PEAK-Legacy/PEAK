"""References to Objects"""

__all__ = ['Reference', 'LinkRef', 'RefAddr']


class Reference(tuple):

    def __new__(klass, *refaddrs, **kw):
        ob = super(Reference,klass).__new__(klass,refaddrs)
        ob.__dict__.update(kw)
        return ob

    def __repr__(self):
        args = map(repr,self)
        args.extend(
            [('%s=%r' % i) for i in self.__dict__.items()]
        )
        return "Reference(%s)" % ','.join(args)


class LinkRef(Reference):

    """Simple reference whose payload is 'RefAddr("LinkAddress",linkName)'"""

    def __new__(klass, linkName):
        return super(LinkRef,klass).__new__(
            klass, RefAddr('LinkAddress',linkName)
        )

    def linkName(self):
        """Retrieve the link name"""
        return self[0].content

    linkName = property(linkName)

    def __repr__(self):
        return "LinkRef(%s)" % `self.linkName`



class RefAddr(object):

    __slots__ = ['type','content']

    def __init__(self,type,content):
        self.type, self.content = type, content

    def __eq__(self,other):
        try:
            return self.type==other.type and self.content==other.content
        except:
            return

    def __hash__(self):
        return hash((self.type,self.other))

    def __repr__(self):
        return "RefAddr(%r,%r)" % self.type, self.content


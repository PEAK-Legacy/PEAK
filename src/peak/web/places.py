from peak.api import *
from interfaces import *
from types import FunctionType, MethodType
import posixpath
from errors import NotFound, NotAllowed, WebException
from environ import allows, getTraversedURL, defaultTraversal, pathSplit
from environ import traverseAttr

__all__ = [
    'Traversable', 'Decorator', 'ContainerAsTraversable', 'MultiTraverser',
]






























class Traversable(binding.Component):

    """Basic traversable object; uses self as its subject and for security"""

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    def traverseTo(self, name, environ):
        return traverseAttr(environ, self, name)

    def preTraverse(self, environ):
        pass    # Should do any traversal requirements checks

    def getURL(self,environ):
        return getTraversedURL(environ)

























class Decorator(Traversable):

    """Traversal adapter whose local attributes add/replace the subject's"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForTypes = [object],
    )

    ob = None

    def asTraversableFor(klass, ob):
        return klass(ob = ob)

    asTraversableFor = classmethod(asTraversableFor)


    def traverseTo(self, name, environ):
        try:
            return traverseAttr(environ, self, name)
        except NotFound:
            # Not recognized, try the un-decorated object
            pass           
        except NotAllowed:           
            # Access failed, see if attribute is private
            guard = adapt(self, security.IGuardedObject, None)

            if guard is not None and guard.getPermissionForName(name):
                # We have explicit permissions defined, so reject access
                raise NotAllowed(environ, result.message)

        # attribute is absent or private, fall through to underlying object
        return traverseAttr(environ, self.ob, name)







class ContainerAsTraversable(Decorator):

    """Traversal adapter for container components"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForProtocols = [naming.IBasicContext, storage.IDataManager],
        asAdapterForTypes = [dict],
    )

    def traverseTo(self, name, environ):

        if name.startswith('@@'):
            name = name[2:]
        else:
            try:
                ob = self.ob[name]
            except KeyError:
                pass
            else:
                result = allows(environ, ob)
                if result:
                    return ob

                raise NotAllowed(environ, result.message)
                
        return super(ContainerAsTraversable,self).traverseTo(name, environ)













class MultiTraverser(Traversable):

    """Aggregate traversal across a sequence of delegate traversables"""

    protocols.advise(
        instancesProvide = [IHTTPHandler]
    )

    items = binding.Require("items to be traversed")

    def preTraverse(self, ctx):
        for item in self.items:
            IWebTraversable(item).preTraverse(ctx)

    def traverseTo(self, name, ctx):

        newItems = []

        for item in self.items:
            try:
                loc = IWebTraversable(item).traverseTo(name, ctx)
            except NotFound:
                continue
            else:
                # we should suggest the parent, since our caller won't
                binding.suggestParentComponent(item, name, loc)
                newItems.append(loc)

        if not newItems:
            raise NotFound(ctx,name)

        if len(newItems)==1:
            loc = newItems[0]
        else:
            loc = self._subTraverser(self, name, items = newItems)
        return loc

    _subTraverser = lambda self, *args, **kw: self.__class__(*args,**kw)



    def handle_http(self,environ,input,errors):

        self.subject.preTraverse(environ)
        
        name, environ = pathSplit(environ)

        if name is None:
            return defaultTraversal(environ)

        return renderHTTP(traverseName(environ,name), input, errors)



class CallableAsHTTP(protocols.Adapter):

    """Make functions/methods callable"""

    protocols.advise(
        instancesProvide = [IHTTPHandler],
        asAdapterForTypes = [FunctionType, MethodType]
    )

    def handle_http(self, environ, input, errors):
        # XXX this should return to mapply-like functionality someday
        return self.subject(environ, input, errors)

















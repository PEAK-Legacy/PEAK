from peak.api import *
from interfaces import *
from types import FunctionType, MethodType
import posixpath

__all__ = [
    'Traversable', 'Decorator', 'ContainerAsTraversable',
    'MultiTraverser', 'TraversalContext',
]
































class TraversalContext(binding.Component):

    protocols.advise(
        instancesProvide = [ITraversalContext]
    )

    interaction = binding.Acquire(IWebInteraction)
    traversable = binding.requireBinding("Traversable being traversed")

    subject = binding.Once(
        lambda s,d,a: s.traversable.getObject(s.interaction),
        suggestParent=False
    )

    renderable = binding.Once(
        lambda s,d,a: adapt(s.subject, s.interaction.pageProtocol, None)
    )

    def isNull(self):
        ob = self.subject
        return ob is NOT_FOUND or ob is NOT_ALLOWED

    def checkPreconditions(self):
        """Invoked before traverse by web requests"""
        self.traversable.preTraverse(self.interaction)

    def subcontext(self, name, ob):
        ob = adapt(ob, self.interaction.pathProtocol)
        binding.suggestParentComponent(self.traversable, name, ob)
        return self.__class__(self, name, traversable = ob)

    def asRenderable(self):
        return self.renderable

    def getObject(self):
        return self.subject





    def contextFor(self, name):
        """Return a new traversal context for 'name'"""

        if name == '..':
            parent = self.getParentComponent()
            if parent is not interaction.skin:
                return parent
            return self

        elif name=='.':
            return self

        ob = self.traversable.traverseTo(name, self.interaction)
        if ob is NOT_GIVEN or ob is NOT_FOUND:
            ob = NullTraversable(ob)

        return self.subcontext(name, ob)


    def render(self):

        """Return rendered value for context object"""

        page = self.renderable

        if page is None:
            # Render the found object directly
            return ob

        return page.render(self)











    def getAbsoluteURL(self):
        """Absolute URL for object at this location"""
        return self.traversable.getURL(self)


    def getTraversedURL(self, absolute=True):
        """Traversed-to URL"""
        if not absolute:
            return self.localPath

        return '%s/%s' % (self.interaction.baseURL, self.localPath)


    def _getLocalPath(self, d, a):

        name = self.getComponentName()

        if name:
            base = self.getParentComponent().localPath
            return posixpath.join(base, name)   # handles empty parts OK

        raise ValueError("Traversable was not assigned a name", self)

    localPath = binding.Once(_getLocalPath)

















class Traversable(binding.Component):

    """Basic traversable object; uses self as its subject and for security"""

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    def getObject(self, interaction):
        return self

    def traverseTo(self, name, interaction):

        ob = self.getObject(interaction)
        loc = getattr(ob, name, NOT_FOUND)

        if loc is not NOT_FOUND:

            if not interaction.allows(ob, name):
                return NOT_ALLOWED

        return loc

    def preTraverse(self, interaction):
        pass    # Should do any traversal requirements checks

    def _getLocalPath(self, d, a):

        name = self.getComponentName()

        if name:
            base = self.getParentComponent().localPath
            return posixpath.join(base, name)   # handles empty parts OK

        raise ValueError("Traversable was not assigned a name", self)

    localPath = binding.Once(_getLocalPath)

    def getURL(self,ctx):
        return ctx.getTraversedURL()

class NullTraversable(object):

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    __slots__ = 'ob'

    def __init__(self,ob):
        self.ob = ob

    def getObject(self, interaction):
        return self.ob

    def traverseTo(self, name, interaction):
        # We never go anywhere...
        return self

    def getURL(self,ctx):
        return ctx.getTraversedURL()

    def preTraverse(self, interaction):
        pass

    localPath = None
















class Decorator(Traversable):

    """Traversal adapter whose local attributes add/replace the subject's"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForTypes = [object],
    )

    ob = None

    def asTraversableFor(klass, ob, proto):
        return klass(ob = ob)

    asTraversableFor = classmethod(asTraversableFor)


    def getObject(self, interaction):
        return self.ob

    def traverseTo(self, name, interaction):

        loc = getattr(self, name, NOT_FOUND)

        if loc is not NOT_FOUND:

            if interaction.allows(self, name):
                return loc

            # Access failed, see if attribute is private
            guard = adapt(self,security.IGuardedObject,None)

            if guard is not None and guard.getPermissionsForName(name):
                # We have explicit permissions defined, so reject access
                return NOT_ALLOWED

        # attribute is absent or private, fall through to underlying object
        return super(Decorator,self).traverseTo(name, interaction)


class ContainerAsTraversable(Decorator):

    """Traversal adapter for container components"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForProtocols = [naming.IBasicContext, storage.IDataManager],
        asAdapterForTypes = [dict],
    )

    def traverseTo(self, name, interaction):

        if name.startswith('@@'):
            return super(ContainerAsTraversable,self).traverseTo(
                name[2:], interaction
            )

        try:
            ob = self.ob[name]
        except KeyError:
            return super(ContainerAsTraversable,self).traverseTo(
                name,interaction
            )

        if interaction.allows(ob):
            return ob

        return NOT_ALLOWED












class MultiTraverser(Traversable):

    """Aggregate traversal across a sequence of delegate traversables"""

    items = binding.requireBinding("traversables to traversed")

    def getObject(self, interaction):
        # Return the first item
        for item in self.items:
            return item.getObject(interaction)

    def preTraverse(self, interaction):
        for item in self.items:
            item.preTraverse(interaction)

    def traverseTo(self, name, interaction):

        newItems = []

        for item in self.items:

            loc = item.traverseTo(name, interaction)

            if loc is NOT_ALLOWED:
                return NOT_ALLOWED

            if loc is not NOT_FOUND:
                # we should suggest the parent, since our caller won't
                binding.suggestParentComponent(item, name, loc)
                newItems.append(loc)

        if not newItems:
            return NOT_FOUND
        if len(newItems)==1:
            loc = newItems[0]
        else:
            loc = self._subTraverser(self, name, items = newItems)
        return loc

    _subTraverser = lambda self, *args, **kw: self.__class__(*args,**kw)

class CallableAsWebPage(protocols.Adapter):

    """Make functions/methods callable"""

    protocols.advise(
        instancesProvide = [IWebPage],
        asAdapterForTypes = [FunctionType, MethodType]
    )

    def render(self, context):
        request = context.interaction.request
        from zope.publisher.publish import mapply
        return mapply(self.subject, request.getPositionalArguments(), request)





























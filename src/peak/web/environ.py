"""Functions to manipulate traversal context/environment

    TODO:

    * a function to replace outgoing MIME headers (e.g. to set content type,
      length)

    * functions to create outgoing cookies and parse incoming ones

    * Docstrings! and an intro to the 'environ' concept
"""

__all__ = [
    'Context', 'StartContext',
    'simpleRedirect', 'clientHas','parseName', 'traverseResource',
    'traverseView', 'traverseSkin', 'traverseAttr', 'traverseItem',
    'traverseDefault',
]

from interfaces import *
import protocols, posixpath, os, re
from cStringIO import StringIO
from peak.api import binding, adapt, NOT_GIVEN, NOT_FOUND
import errors
from peak.security.interfaces import IInteraction
from wsgiref.util import shift_path_info, setup_testing_defaults















ns_match = re.compile(r"\+\+([A-Za-z_]\w*)\+\+|").match

def parseName(name):
    """Return 'ns,nm' pair for 'name'

    If 'name' begins with '"@@"', 'ns' will equal 'view', and 'nm' will be
    the remainder of 'name'.  If 'name' begins with a '"++"'-bracketed
    Python identifier, such as '"++foo_27++"', the identifier will be returned
    in 'ns', and the remainder of 'name' in 'nm'.  Otherwise, 'ns' will be
    an empty string, and 'nm' will be 'name'.
    """
    if name.startswith('@@'):
        return 'view',name[2:]
    match = ns_match(name)
    return (match.group(1) or ''), name[match.end(0):]


def traverseResource(ctx, ob, ns, nm, qname, default=NOT_GIVEN):
    if qname==ctx.policy.resourcePrefix:
        return ctx.childContext(qname, ctx.skin)
    if default is NOT_GIVEN:
        raise errors.NotFound(ctx, qname, ctx.current)
    return default


def traverseSkin(ctx, ob, ns, nm, qname, default=NOT_GIVEN):
    skin = ctx.policy.getSkin(nm)
    if skin is not None:
        return ctx.clone(skin=skin, rootURL=ctx.rootURL+'/'+qname)
    if default is NOT_GIVEN:
        raise errors.NotFound(ctx, qname, ctx.current)
    return default









class Context:

    __metaclass__ = binding.Activator
    protocols.advise(instancesProvide=[ITraversalContext])

    previous = binding.Require("Parent context")
    interaction = policy = skin = rootURL = binding.Delegate('previous')
    allows = user = permissionNeeded = binding.Delegate('interaction')
    getResource = binding.Delegate('skin')

    def __init__(self,name,current,environ,previous=None,**kw):
        if kw: self._setup(kw)
        self.current = current
        self.name = name
        self.environ = environ
        if previous is not None:
            self.previous = previous
        if 'rootURL' in kw and self.previous is not None \
            and kw['rootURL']<>self.previous.rootURL:
                self.previous = self.previous.clone(rootURL=self.rootURL)

    def childContext(self,name,ob):
        return Context(name,ob,self.environ,self)

    def peerContext(self,name,ob):
        return self.clone(name=name,current=ob)

    def parentContext(self):
        return self.previous

    absoluteURL = binding.Make(
        lambda self: IWebTraversable(self.current).getURL(self)
    )

    traversedURL = binding.Make(
        lambda self: posixpath.join(    # handles empty parts OK
            self.previous.absoluteURL, self.name
        )
    )


    def renderHTTP(self):
        return IHTTPHandler(self.current).handle_http(self)


    def clone(self,**kw):
        for attr in 'name','current','environ':
            if attr not in kw:
                kw[attr] = getattr(self,attr)
        kw.setdefault('clone_from',self)
        return self.__class__(**kw)


    def _setup(self,kw):
        if 'clone_from' in kw:
            cfg = kw['clone_from'].__getattribute__
            del kw['clone_from']
            for attr in 'interaction','policy','skin','rootURL','previous':
                if attr not in kw:
                    kw[attr] = cfg(attr)

        klass = self.__class__
        for k,v in kw.iteritems():
            if hasattr(klass,k):
                setattr(self,k,v)
            else:
                raise TypeError(
                    "%s constructor has no keyword argument %s" %
                    (klass, k)
                )












    def shift(self):
        environ = self.environ       
        part = shift_path_info(environ)
        if part or part is None:
            return part

        # We got an empty string, so we just hit a trailing slash;
        # replace it with the default method:
        environ['SCRIPT_NAME'] += self.policy.defaultMethod
        return self.policy.defaultMethod

    def traverseName(self,name):
        ns, nm = parseName(name)
        if ns:
            handler = self.policy.ns_handler(ns,None)
            if handler is None:
                raise errors.NotFound(self,name,self.current)
            return handler(self, self.current, ns, nm, name)
        if name=='..':
            return self.parentContext()
        elif not name or name=='.':
            return self
        else:
            return IWebTraversable(self.current).traverseTo(name,self)

    def getView(self,name,default=NOT_GIVEN):
        ctx = traverseView(
            self, self.current, 'view', name, '@@'+name, default
        )
        if ctx is not default:
            return ctx.current
        return ctx

    def requireAccess(self,qname,*args,**kw):
        result = self.allows(*args,**kw)
        if not result:
            raise errors.NotAllowed(self,qname,
                getattr(result,'message',"Permission denied")
            )


class StartContext(Context):

    previous = None

    skin        = binding.Require("Traversal skin", adaptTo=ISkin)
    interaction = binding.Require("Security interaction", adaptTo=IInteraction)
    rootURL     = binding.Require("Application root URL")
    absoluteURL = traversedURL = binding.Obtain('rootURL')

    policy       = binding.Require("Interaction policy",
        adaptTo=IInteractionPolicy
    )

    def parentContext(self):
        return self


def simpleRedirect(environ,location):
    if (environ.get("SERVER_PROTOCOL","HTTP/1.0")<"HTTP/1.1"):
        status="302 Found"
    else:
        status="303 See Other"
    return status,[('Location',location)],()


def clientHas(environ, lastModified=None, ETag=None):
    return False    # XXX














def traverseAttr(ctx, ob, ns, name, qname, default=NOT_GIVEN):
    loc = getattr(ob, name, NOT_FOUND)
    if loc is not NOT_FOUND:
        ctx.requireAccess(qname, ob, name)
        return ctx.childContext(qname,loc)

    if default is NOT_GIVEN:
        raise errors.NotFound(ctx,qname,ob)
    return default


def traverseItem(ctx, ob, ns, name, qname, default=NOT_GIVEN):
    gi = getattr(ob,'__getitem__',None)
    if gi is not None:
        try:
            loc = ob[name]
        except (KeyError,IndexError,TypeError):
            pass
        else:
            ctx.requireAccess(qname, loc)
            return ctx.childContext(qname,loc)

    if default is NOT_GIVEN:
        raise errors.NotFound(ctx,qname,ob)
    return default


def traverseView(ctx, ob, ns, name, qname, default=NOT_GIVEN):

    p = ctx.policy.view_protocol(name)
    if p is not None:
        handler = adapt(ob,p,NOT_FOUND)
        if handler is not NOT_FOUND:
            return handler(ctx, ctx.current, ns, name, qname, default)

    if default is NOT_GIVEN:
        raise errors.NotFound(ctx,qname,ob)
    return default
    


def traverseDefault(ctx, ob, ns, name, qname, default=NOT_GIVEN):

    loc = traverseAttr(ctx,ob,ns,name,qname,NOT_FOUND)

    if loc is NOT_FOUND:
        loc = traverseItem(ctx,ob,ns,name,qname,NOT_FOUND)

        if loc is NOT_FOUND:
            return traverseView(ctx,ob,ns,name,qname,default)

    return loc


class TraversableAsHandler(protocols.Adapter):

    protocols.advise(
        instancesProvide=[IHTTPHandler],
        asAdapterForProtocols=[IWebTraversable]
    )

    def handle_http(self,ctx):

        ctx = self.subject.preTraverse(ctx)
        name = ctx.shift()

        if name is None:

            if ctx.environ['REQUEST_METHOD'] in ('GET','HEAD'):
                # Redirect to current location + '/'
                url = ctx.traversedURL+'/'
                if ctx.environ.get('QUERY_STRING'):
                    url = '%s?%s' % (url,ctx.environ['QUERY_STRING'])

                return simpleRedirect(ctx.environ,url)

            from errors import UnsupportedMethod
            raise UnsupportedMethod(ctx)

        return ctx.traverseName(name).renderHTTP()



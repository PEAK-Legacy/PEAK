"""Functions to manipulate traversal context/environment

    TODO:

    * a function to replace outgoing MIME headers (e.g. to set content type,
      length)

    * functions to create outgoing cookies and parse incoming ones

    * Docstrings! and an intro to the 'environ' concept
"""

__all__ = [
    'traverseAttr', 'default_for_testing', 'Context', 'StartContext',
    'simpleRedirect', 'clientHas','parseName', 'traverseResource',
]

from interfaces import *
import protocols, posixpath, os, re
from cStringIO import StringIO
from peak.api import binding, adapt, NOT_GIVEN, NOT_FOUND
import errors
from peak.security.interfaces import IInteraction


















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


def traverseResource(ctx, ns, nm, qname):
    return ctx.childContext(qname, ctx.skin)






















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
        path_info = environ.get('PATH_INFO','')

        if not path_info:
            return None

        path_parts = path_info.split('/')
        path_parts[1:-1] = [p for p in path_parts[1:-1] if p and p<>'.']
        name = path_parts[1] or self.policy.defaultMethod
        del path_parts[1]

        script_name = environ.get('SCRIPT_NAME','')
        script_name = posixpath.normpath(script_name+'/'+name)
        if script_name.endswith('/'):
            script_name = script_name[:-1]

        environ['SCRIPT_NAME'] = script_name
        environ['PATH_INFO']   = '/'.join(path_parts)

        # Special case: '/.' on PATH_INFO doesn't get stripped,
        # because we don't strip the last element of PATH_INFO
        # if there's only one path part left.  Instead of fixing this
        # above, we fix it here so that PATH_INFO gets normalized to
        # an empty string in the environ.

        if name=='.':
            name = None

        return name











    def traverseName(self,name):
        ns, nm = parseName(name)
        if ns:
            handler = self.policy.ns_handler(ns,None)
            if handler is None:
                raise errors.NotFound(self,name,self.current)
            return handler(self, ns, nm, name)
        if name=='..':
            return self.parentContext()
        elif not name or name=='.':
            return self
        else:
            ob = IWebTraversable(self.current).traverseTo(name,self)
            return self.childContext(name,ob)



























class StartContext(Context):

    previous = None

    skin        = binding.Require("Traversal skin",
        adaptTo=ISkin
    )
    policy      = binding.Require("Interaction policy",
        adaptTo=IInteractionPolicy
    )
    interaction = binding.Require("Security interaction",
        adaptTo=IInteraction
    )

    rootURL    = binding.Require("Application root URL")

    traversedURL = absoluteURL = binding.Obtain('rootURL')

    def parentContext(self):
        return self


def default_for_testing(environ):
    """Update 'environ' with trivial defaults for testing purposes"""

    environ.setdefault('HTTP_HOST',
        environ.setdefault('SERVER_NAME','127.0.0.1')
    )

    if 'SCRIPT_NAME' not in environ and 'PATH_INFO' not in environ:
        environ.setdefault('SCRIPT_NAME','')
        environ.setdefault('PATH_INFO','/')









def simpleRedirect(environ,location):
    if (environ.get("SERVER_PROTOCOL","HTTP/1.0")<"HTTP/1.1"):
        status="302 Found"
    else:
        status="303 See Other"
    return status,[('Location',location)],()


def clientHas(environ, lastModified=None, ETag=None):
    return False    # XXX


def traverseAttr(ctx, ob, name):

    loc = getattr(ob, name, NOT_FOUND)

    if loc is not NOT_FOUND:

        result = ctx.allows(ob, name)

        if result:
            return loc

        raise errors.NotAllowed(
            ctx, getattr(result,'message',"Permission Denied")
        )

    raise errors.NotFound(ctx,name,ob)













class TraversableAsHandler(protocols.Adapter):

    protocols.advise(
        instancesProvide=[IHTTPHandler],
        asAdapterForProtocols=[IWebTraversable]
    )

    def handle_http(self,ctx):

        self.subject.preTraverse(ctx)
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
















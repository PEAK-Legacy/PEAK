"""Functions to manipulate traversal context/environment

    TODO:

    * a function to replace outgoing MIME headers (e.g. to set content type,
      length)

    * functions to create outgoing cookies and parse incoming ones

    * Docstrings! and an intro to the 'environ' concept
"""

__all__ = [
    'shift_path_info',
    'traverseAttr', 'newEnvironment', 'Context', 'StartContext',
    'simpleRedirect', 'clientHas',
]

from interfaces import *
import protocols, posixpath, os
from cStringIO import StringIO
from peak.api import binding, adapt, NOT_GIVEN, NOT_FOUND
import errors
from peak.security.interfaces import IInteraction

















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


    def traverseName(self,name):
        if name=='..':
            return self.parentContext()
        elif not name or name=='.':
            return self
        else:
            ob = IWebTraversable(self.current).traverseTo(name,self)
            return self.childContext(name,ob)


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
    rootURL    = binding.Make(
        lambda self: self.environ['peak.web.root_url']
    )

    traversedURL = absoluteURL = binding.Obtain('rootURL')

    def parentContext(self):
        return self



def newEnvironment(environ={}):

    new_env = dict(os.environ)     # First the OS
    new_env.update(environ)   # Then the server

    new_env.setdefault('HTTP_HOST','127.0.0.1')   # XXX
    new_env.setdefault('SCRIPT_NAME','/')   # XXX
    new_env.setdefault('peak.web.root_url', # XXX
        "http://%(HTTP_HOST)s%(SCRIPT_NAME)s" % new_env
    )
    return new_env






def simpleRedirect(environ,location):
    if (environ.get("SERVER_PROTOCOL","HTTP/1.0")<"HTTP/1.1"):
        status="302 Found"
    else:
        status="303 See Other"
    return status,[('Location',location)],()


def clientHas(environ, lastModified=None, ETag=None):
    return False    # XXX


def shift_path_info(ctx):
    environ = ctx.environ
    path_info = environ.get('PATH_INFO','').split('/')

    if len(path_info)==1:
        return None

    name = path_info[1]

    if len(path_info)>2:
        path_info = '/'+'/'.join(path_info[2:])
    else:
        path_info = ''

    script_name = environ.get('SCRIPT_NAME','/')
    name = name or ctx.policy.defaultMethod

    if name=='..':
        script_name = posixpath.dirname(script_name)
    elif name != '.':
        script_name = posixpath.join(script_name,name)

    environ['SCRIPT_NAME'] = script_name
    environ['PATH_INFO']   = path_info
    return name




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
        name = shift_path_info(ctx)

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
















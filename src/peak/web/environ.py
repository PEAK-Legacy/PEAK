"""Functions to manipulate traversal context/environment

    TODO:

    * a function to replace outgoing MIME headers (e.g. to set content type,
      length)

    * functions to create outgoing cookies and parse incoming ones

    * Docstrings! and an intro to the 'environ' concept
"""

__all__ = [
    'getUser', 'getSkin', 'getInteraction', 'getPolicy', 'shift_path_info',
    'getRootURL', 'traverseAttr', 'newEnvironment', 'Context',
    'simpleRedirect', 'clientHas',
]

from interfaces import *
import protocols, posixpath, os
from cStringIO import StringIO
from peak.api import binding, adapt, NOT_GIVEN, NOT_FOUND
import errors


















class Context:

    protocols.advise(instancesProvide=[ITraversalContext])

    def __init__(self,previous,name,ob,environ):
        self.previous = previous
        self.current = ob
        self.name = name
        self.environ = environ

    def childContext(self,name,ob):
        return self.__class__(self,name,ob,self.environ)

    def peerContext(self,name,ob):
        return self.__class__(self.previous,name,ob,self.environ)

    def parentContext(self):
        if self.previous is None:
            return self
        return self.previous

    def getAbsoluteURL(self):
        if self.previous is not None:
            return IWebTraversable(self.current).getURL(self)
        else:
            return getRootURL(self.environ)

    def getTraversedURL(self):
        if self.previous is not None:
            base = IWebTraversable(self.current).getURL(self.previous)
            return posixpath.join(base, self.name)   # handles empty parts OK
        else:
            return getRootURL(self.environ)

    def allows(self,*args,**kw):
        return getInteraction(self.environ).allows(*args,**kw)





    def traverseName(self,name):
        if name=='..':
            return self.parentContext()
        elif not name or name=='.':
            return self
        else:
            # XXX error handling?
            ob = IWebTraversable(self.current).traverseTo(name,self)
            return self.childContext(name,ob)


    def renderHTTP(self):
        return IHTTPHandler(self.current).handle_http(self)


    def getResource(self,path):
        return getSkin(self.environ).getResource(path)



def newEnvironment(policy,environ={},root_url=None):

    new_env = dict(os.environ)     # First the OS
    new_env.update(environ)   # Then the server

    new_env.setdefault('HTTP_HOST','127.0.0.1')   # XXX
    new_env.setdefault('SCRIPT_NAME','/')   # XXX

    new_env['peak.web.rootURL'] = root_url or \
        "http://%(HTTP_HOST)s%(SCRIPT_NAME)s" % new_env   # XXX

    new_env['peak.web.policy']  = policy
    return new_env








def getPolicy(environ):
    return environ['peak.web.policy']

def getUser(environ):
    return getPolicy(environ).getUser(environ)

def getSkin(environ):
    try:
        return environ['peak.web.skin']
    except KeyError:
        skin = environ['peak.web.skin'] = getPolicy(environ).getSkin(
            _get_skin_name(environ)
        )
        return skin

def getInteraction(environ):
    try:
        return environ['peak.web.interaction']

    except KeyError:
        interaction = getPolicy(environ).newInteraction(user=getUser(environ))
        environ['peak.web.interaction'] = interaction
        return interaction

def getRootURL(environ):
    return environ['peak.web.rootURL']















def simpleRedirect(environ,location):
    if (environ.get("SERVER_PROTOCOL","HTTP/1.0")<"HTTP/1.1"):
        status="302 Found"
    else:
        status="303 See Other"
    return status,[('Location',location)],()


def clientHas(environ, lastModified=None, ETag=None):
    return False    # XXX


def shift_path_info(environ):

    path_info = environ.get('PATH_INFO','').split('/')

    if len(path_info)==1:
        return None, environ

    name = path_info[1]

    if len(path_info)>2:
        path_info = '/'+'/'.join(path_info[2:])
    else:
        path_info = ''

    script_name = environ.get('SCRIPT_NAME','/')
    name = name or getPolicy(environ).defaultMethod

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
        name = shift_path_info(ctx.environ)

        if name is None:

            if ctx.environ['REQUEST_METHOD'] in ('GET','HEAD'):
                # Redirect to current location + '/'
                url = ctx.getTraversedURL()+'/'
                if ctx.environ.get('QUERY_STRING'):
                    url = '%s?%s' % (url,ctx.environ['QUERY_STRING'])
        
                return simpleRedirect(ctx.environ,url)
        
            from errors import UnsupportedMethod
            raise UnsupportedMethod(ctx)

        return ctx.traverseName(name).renderHTTP()


def _get_skin_name(environ):
    return "default"    # XXX












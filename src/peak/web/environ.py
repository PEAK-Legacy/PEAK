"""Functions to manipulate traversal context/environment

    TODO:

    * a function to replace outgoing MIME headers (e.g. to set content type,
      length)

    * functions to create outgoing cookies and parse incoming ones

    * Docstrings! and an intro to the 'environ' concept
"""

__all__ = [
    'getUser', 'getSkin', 'getResource', 'getInteraction', 'getPolicy',
    'getRootURL', 'getCurrent', 'allows', 'traverseName', 'traverseAttr',
    'getAbsoluteURL', 'getTraversedURL',
    'childContext', 'peerContext', 'dupContext', 'parentContext',
    'renderHTTP', 'defaultTraversal', 'simpleRedirect', 'pathSplit',
    'clientHas',
]

from interfaces import IHTTPHandler, IWebTraversable, IResource
import protocols, posixpath
from cStringIO import StringIO
from peak.api import binding, adapt, NOT_GIVEN, NOT_FOUND
import errors















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

def getResource(environ,path):
    return getSkin(environ).getResource(path)

def allows(environ, *args, **kw):
    return getInteraction(environ).allows(*args,**kw)


def getInteraction(environ):

    try:
        return environ['peak.web.interaction']

    except KeyError:
        interaction = getPolicy(environ).newInteraction(user=getUser(environ))
        environ['peak.web.interaction'] = interaction
        return interaction


def getRootURL(environ):
    return environ['peak.web.rootURL']






def getCurrent(environ, adaptTo=None):

    current = environ['peak.web.current']

    if adaptTo is not None:
        return adapt(current,adaptTo)

    return current


def traverseName(environ,name):
    """Return a new 'environ' after traversing to 'name'"""

    if name == '..':
        return environ.get('peak.web.previous',environ)
    elif name=='.' or not name:
        return environ

    return childContext(
        environ, name,
        getCurrent(environ,IWebTraversable
            ).traverseTo(name,environ)  # XXX error handling?
    )


def getAbsoluteURL(environ):
    if 'peak.web.previous' in environ:
        return getCurrent(environ,IWebTraversable).getURL(environ)
    else:
        return getRootURL(environ)


def getTraversedURL(environ):
    if 'peak.web.previous' in environ:
        base = getAbsoluteURL(environ['peak.web.previous'])
        name = environ['peak.web.name']
        return posixpath.join(base, name)   # handles empty parts OK
    else:
        return getRootURL(environ)


def simpleRedirect(environ,location):
    location = 'Location: %s' % location
    if (environ.get("SERVER_PROTOCOL","HTTP/1.0")<"HTTP/1.1"):
        status=302
    else:
        status=303
    return status,[location],()


def clientHas(environ, lastModified=None, ETag=None):
    return False    # XXX


def childContext(environ, name, new_object):
    return dupContext(environ,
        ('peak.web.previous',environ), ('peak.web.name', name),
        ('peak.web.current', new_object)
    )


def peerContext(environ, ob):
    """Return a dupContext of 'environ' that has 'ob' as its current object"""
    return dupContext(environ,('peak.web.current',ob))


def defaultTraversal(environ):

    if environ['REQUEST_METHOD'] in ('GET','HEAD'):
        # Redirect to current location + '/'
        url = getTraversedURL(environ)+'/'
        if environ.get('QUERY_STRING'):
            url = '%s?%s' % (url,environ['QUERY_STRING'])

        return simpleRedirect(environ,url)

    from errors import UnsupportedMethod
    raise UnsupportedMethod(environ)




def pathSplit(environ):

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

    return name, dupContext(
        environ, ('SCRIPT_NAME',script_name), ('PATH_INFO',path_info)
    )

def renderHTTP(environ,input,errors):
    return getCurrent(environ, IHTTPHandler).handle_http(environ,input,errors)

def dupContext(environ,*items):
    new_environ = environ.copy()
    if items:
        new_environ.update(dict(items))
    return new_environ

def parentContext(environ,default=NOT_GIVEN):
    if default is NOT_GIVEN:
        default = environ
    return environ.get('peak.web.previous',default)


def traverseAttr(environ, ob, name):

    loc = getattr(ob, name, NOT_FOUND)

    if loc is not NOT_FOUND:

        result = allows(environ,ob, name)

        if result:
            return loc

        raise errors.NotAllowed(
            environ,getattr(result,'message',"Permission Denied")
        )

    raise errors.NotFound(environ,name,ob)

























class TraversableAsHandler(protocols.Adapter):

    protocols.advise(
        instancesProvide=[IHTTPHandler],
        asAdapterForProtocols=[IWebTraversable]
    )

    def handle_http(self,environ,input,errors):

        self.subject.preTraverse(environ)
        name, environ = pathSplit(environ)

        if name is None:
            return defaultTraversal(environ)

        environ = traverseName(environ,name)

        return IHTTPHandler(getCurrent(environ)).handle_http(
            environ, input, errors
        )

def _get_skin_name(environ):
    return "default"    # XXX



















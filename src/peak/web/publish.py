"""Publish 'peak.web' apps"""

from peak.api import *
from interfaces import *
from errors import NotFound, NotAllowed
from environ import traverseName, renderHTTP, getPolicy, getSkin
from cStringIO import StringIO
import os,sys

__all__ = [
    'NullAuthenticationService', 'InteractionPolicy', 'CGIPublisher',
    'DefaultExceptionHandler', 'TraversalPath', 'TestPolicy',
]


class DefaultExceptionHandler(binding.Singleton):

    def handleException(self,environ,error_stream,exc_info,retry_allowed=1):

        policy = getPolicy(environ)

        try:
            storage.abortTransaction(policy.app)

            # XXX note that the following assumes exc_info is available as
            # XXX sys.exc_info; will this always be the case?
            policy.log.exception("ERROR:")

            return '500',['Content-type: text/plain'],['An error occurred']

        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None







class TraversalPath(naming.CompoundName):

    """Name that knows how to do 'IWebTraversable' traversal

    NOTE: 'preTraverse()' checks are not performed!
    """

    syntax = naming.PathSyntax(
        direction=1,
        separator='/'
    )

    def traverse(self, environ, getRoot = lambda environ: environ):

        path = iter(self)
        part = path.next()

        if not part:
            environ = getRoot(environ)
        else:
            # reset to beginning
            path = iter(self)

        for part in path:
            if part:
                environ = traverseName(environ,part)

        return environ


class NullAuthenticationService:

    protocols.advise(
        instancesProvide=[IAuthService]
    )

    def getUser(self, interaction):
        return None



class InteractionPolicy(binding.Component, protocols.StickyAdapter):

    protocols.advise(
        instancesProvide = [IInteractionPolicy],
        asAdapterForProtocols = [binding.IComponent],
        factoryMethod = 'fromComponent',
    )

    attachForProtocols = (IInteractionPolicy,)

    def fromComponent(klass, ob):
        ip = klass(ob)
        protocols.StickyAdapter.__init__(ip, ob, IInteractionPolicy)
        return ip

    fromComponent = classmethod(fromComponent)

    app            = binding.Obtain('./subject')
    log            = binding.Obtain(APPLICATION_LOG)

    defaultMethod  = binding.Obtain(DEFAULT_METHOD)
    resourcePrefix = binding.Obtain(RESOURCE_PREFIX)

    _authSvc       = binding.Make(IAuthService, adaptTo=IAuthService)
    _mkInteraction = binding.Obtain(config.FactoryFor(security.IInteraction))

    root = binding.Obtain('app', adaptTo=IWebTraversable)

    getUser  = binding.Delegate('_authSvc')

    def newInteraction(self,**options):
        return self._mkInteraction(self,None,**options)









    def newEnvironment(self,environ={}):

        new_env = dict(os.environ)     # First the OS
        new_env.update(environ)        # Then the server

        new_env.setdefault('HTTP_HOST','127.0.0.1')   # XXX
        new_env.setdefault('SCRIPT_NAME','/')   # XXX

        new_env['peak.web.rootURL']     = \
            "http://%(HTTP_HOST)s%(SCRIPT_NAME)s" % new_env   # XXX
        new_env['peak.web.policy']      = self
        new_env['peak.web.current'] = getSkin(new_env)

        return new_env


    def beforeTraversal(self, environ):
        """Begin transaction before traversal"""
        storage.beginTransaction(self.app)


    def afterCall(self, environ):
        """Commit transaction after successful hit"""
        storage.commitTransaction(self.app)


    def handleException(self, environ, error_stream, exc_info, retry_allowed=1):
        """Convert exception to a handler, and invoke it"""
        try:
            handler = IWebException(exc_info[1], DefaultExceptionHandler)
            return handler.handleException(
                environ, error_stream, exc_info, retry_allowed
            )
        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None




    layerMap = binding.Make( config.Namespace('peak.web.layers') )

    def getLayer(self,layerName):
        ob = getattr(self.layerMap,layerName)
        binding.suggestParentComponent(self,layerName,ob)
        return ob

    skinMap = binding.Make( config.Namespace('peak.web.skins') )

    def getSkin(self, name):
        ob = getattr(self.skinMap,name)
        binding.suggestParentComponent(self,name,ob)
        return ob



class TestPolicy(InteractionPolicy):

    """Convenient interaction to use for tests, experiments, etc."""

    app = binding.Obtain('..')

    def simpleTraverse(self, path, run=True):

        path = adapt(path, TraversalPath)
        env = self.newEnvironment()

        for part in path:
            env = traverseName(env,part)

        if run:
            status, headers, body = renderHTTP(
                env, StringIO(''), StringIO()
            )
            return ''.join(body)

        return env




class CGIPublisher(binding.Component):

    """Use 'zope.publisher' to run an application as CGI/FastCGI

    For basic use, this just needs an 'app' parameter, and it will publish
    that application.

    'CGIPublisher' is primarily intended as a base adapter class for creating
    web applications.  To use it, you can simply subclass it, replacing the
    'app' binding with an instance of your application, and replacing any other
    parameters as needed.  The resulting class can be invoked with 'peak CGI'
    to run as a CGI or FastCGI application."""

    protocols.advise(
        instancesProvide=[running.IRerunnableCGI],
    )

    # The fromApp method is registered as an adapter factory for
    # arbitrary components to IRerunnableCGI, in peak.running.interfaces.
    # If we registered it here, it wouldn't be usable unless peak.web
    # was already imported, which leads to bootstrap problems, at least
    # with very trivial web apps (like examples/trivial_web).

    def fromApp(klass, app, protocol=None):
        return klass(app, app=app)

    fromApp = classmethod(fromApp)

    app    = binding.Require("Application root to publish")
    policy = binding.Obtain('app', adaptTo = IInteractionPolicy)











    def runCGI(self, input, output, errors, env, argv=()):

        """Process one request"""

        try:
            s,h,b = self.handle_http(env,input,errors)
        except:
            self.policy.log.exception("Unexpected error")
            s,h,b = '500',['Content-type: text/plain'],['An error occurred']

        print >>output, "Status: %s" % s
        for header in h:
            print >>output, header
        print >>output

        for data in b:
            output.write(data)

        return 0






















    def handle_http(self,environ,input,errors):

        policy  = self.policy
        environ = policy.newEnvironment(environ)

        policy.beforeTraversal(environ)

        try:
            s,h,b = renderHTTP(environ,input,errors)
            policy.afterCall(environ)
            return s,h,b
        except:
            return policy.handleException(environ, errors, sys.exc_info())





























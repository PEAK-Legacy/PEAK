"""Publish 'peak.web' apps"""

from peak.api import *
from interfaces import *
from errors import NotFound, NotAllowed
from environ import default_for_testing, StartContext
from cStringIO import StringIO
import os,sys

__all__ = [
    'NullAuthenticationService', 'InteractionPolicy', 'CGIPublisher',
    'DefaultExceptionHandler', 'TraversalPath', 'TestPolicy',
]


class DefaultExceptionHandler(binding.Singleton):

    def handleException(self,ctx,exc_info,retry_allowed=1):

        policy = ctx.policy

        try:
            storage.abortTransaction(policy.app)

            # XXX note that the following assumes exc_info is available as
            # XXX sys.exc_info; will this always be the case?
            policy.log.exception("ERROR:")

            return '500',[('Content-type','text/plain')],['An error occurred']

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

    def traverse(self, ctx, getRoot = lambda environ: environ):

        path = iter(self)
        part = path.next()

        if not part:
            ctx = getRoot(ctx)
        else:
            # reset to beginning
            path = iter(self)

        for part in path:
            if part:
                ctx = ctx.traverseName(part)

        return ctx


class NullAuthenticationService:

    protocols.advise(
        instancesProvide=[IAuthService]
    )

    def getUser(self, environ):
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

    getUser = binding.Delegate('_authSvc')

    def newInteraction(self,**options):
        return self._mkInteraction(self,None,**options)









    def newContext(self,environ=None,start=NOT_GIVEN,skin=None,interaction=None):

        if environ is None:
            environ = {}

        if skin is None:
            skin = self.getSkin("default")  # XXX

        if interaction is None:
            interaction = self.newInteraction(user=self.getUser(environ))

        if start is NOT_GIVEN:
            start = skin

        environ.setdefault('HTTP_HOST',environ['SERVER_NAME'])
        root_url = "http://%(HTTP_HOST)s%(SCRIPT_NAME)s" % environ  # XXX

        return StartContext('', start, environ,
            policy=self, skin=skin, interaction=interaction, rootURL=root_url
        )


    def beforeTraversal(self, environ):
        """Begin transaction before traversal"""
        storage.beginTransaction(self.app)


    def afterCall(self, ctx):
        """Commit transaction after successful hit"""
        storage.commitTransaction(self.app)











    def handleException(self, ctx, exc_info, retry_allowed=1):
        """Convert exception to a handler, and invoke it"""
        try:
            handler = IWebException(exc_info[1], DefaultExceptionHandler)
            return handler.handleException(
                ctx, exc_info, retry_allowed
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

    def newContext(self,environ=None,start=NOT_GIVEN,skin=None,interaction=None):
        # Set up defaults for test environment
        if environ is None:
            environ = {}
        default_for_testing(environ)
        return super(TestPolicy,self).newContext(
            environ, start, skin, interaction
        )

    def simpleTraverse(self, path, run=True):

        path = adapt(path, TraversalPath)
        ctx = self.newContext()

        for part in path:
            ctx = ctx.traverseName(part)

        if run:
            ctx.environ['wsgi.input'] = StringIO('')
            ctx.environ['wsgi.errors'] = StringIO()
            status, headers, body = ctx.renderHTTP()
            return ''.join(body)

        return ctx











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
            env['wsgi.input'] = input
            env['wsgi.errors'] = errors
            s,h,b = self._handle_http(env)
        except:
            self.policy.log.exception("Unexpected error")
            s,h,b = (
                '500 Unexpected Error',
                [('Content-type','text/plain')],
                ['An error occurred']
            )

        print >>output, "Status: %s" % s
        for header in h:
            print >>output, "%s: %s" % header
        print >>output

        for data in b:
            output.write(data)

        return 0
















    def _handle_http(self,environ):

        policy  = self.policy
        ctx = policy.newContext(environ)

        try:
            policy.beforeTraversal(ctx)
            result = ctx.renderHTTP()
            policy.afterCall(ctx)
            return result
        except:
            return policy.handleException(ctx, sys.exc_info())






























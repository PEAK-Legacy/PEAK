from peak.api import *
from interfaces import *

__all__ = ['WebException', 'NotFound', 'NotAllowed']


class WebException(Exception):

    protocols.advise(
        instancesProvide = [IWebException]
    )

    security.allow(
        httpStatus = [security.Anybody],
        args = [security.Anybody],
        template = [security.Anybody],
        exc_info = [security.Anybody],
        # ...?
    )

    httpStatus = '500'

    def __init__(self, context, *args):
        Exception.__init__(self, *args)
        self.context = context

    def template(self,d,a):
        ctx = self.context
        interaction = ctx.interaction
        skin = interaction.skin
        t = skin.getResource('/peak.web/error_%s' % self.httpStatus)
        if t is NOT_FOUND:
            t = skin.getResource('/peak.web/standard_error')
        return t

    template = binding.Once(template)





    def renderingContext(self):

        # Create a traversal context that replaces the last traversed location
        # with this exception instance.

        ctx = self.context
        parent = ctx.getParentComponent()
        name   = ctx.getComponentName()
        newCtx = parent.subcontext(name, self)


    def handleException(self, interaction, thrower, exc_info, retry_allowed=1):

        try:
            storage.abort(interaction.app)

            # XXX note that the following assumes exc_info is available as
            # XXX sys.exc_info; will this always be the case?
            interaction.log.exception("ERROR:")

            # XXX Maybe the following should be in a method on interaction?
            response = interaction.response
            response.reset()
            response.setCharsetUsingRequest(interaction.request)
            response.setStatus(self.httpStatus)

            self.exc_info = exc_info

            ctx = self.renderingContext()
            result = ctx.contextFor('template').render()

            if result is not response:
                response.setBody(result)

        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            ctx = exc_info = self.exc_info = None



class NotFound(WebException):

    httpStatus = '404'  # Not Found


class NotAllowed(WebException):

    httpStatus = '403'  # Forbidden


































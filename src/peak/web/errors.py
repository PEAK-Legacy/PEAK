from peak.api import *
from interfaces import *
from environ import peerContext, renderHTTP, traverseName, getPolicy, getSkin
from cStringIO import StringIO
import sys
__all__ = ['WebException', 'NotFound', 'NotAllowed', 'UnsupportedMethod']


class WebException(Exception):

    protocols.advise( instancesProvide = [IWebException,IHTTPHandler] )

    security.allow(
        httpStatus = security.Anybody,
        args = security.Anybody,
        template = security.Anybody,
        exc_info = security.Anybody,
        traversedName = security.Anybody,
        # ...?
    )

    httpStatus = '500'
    traversedName = None
    levelName = 'ERROR'

    def __init__(self, environ, *args):
        Exception.__init__(self, *args)
        self.environ = environ

    def template(self):
        skin = getSkin(self.environ)
        try:
            return skin.getResource('/peak.web/error_%s' % self.httpStatus)
        except NotFound:
            try:
                return skin.getResource('/peak.web/standard_error')
            except NotFound:
                return self     # XXX

    template = binding.Make(template)

    def handle_http(self,e,i,err):
        return (
            self.httpStatus, ['Content-type: text/plain'],
            [self.__class__.__name__+str(self)]
        )


    def handleException(self, environ,error_stream,exc_info,retry_allowed=1):

        try:
            policy = getPolicy(environ)
            self.exc_info = exc_info

            storage.abortTransaction(policy.app)

            # XXX note that the following assumes exc_info is available as
            # XXX sys.exc_info(); will this always be the case?
            policy.log.log(self.levelName,"ERROR:",exc_info=exc_info)

            environ = peerContext(self.environ, self)
            s,h,b = renderHTTP(
                traverseName(environ,'template'), StringIO(''), error_stream
            )

            if str(s)[:3]=='200':
                s = self.httpStatus     # replace with our error status

            return s, h, b

        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            ctx = exc_info = self.exc_info = None








class NotFound(WebException):
    httpStatus = '404'  # Not Found
    levelName = 'DEBUG'


class NotAllowed(WebException):
    httpStatus = '403'  # Forbidden
    levelName = 'INFO'


class UnsupportedMethod(WebException):
    httpStatus = '405'  # Method Not Allowed






























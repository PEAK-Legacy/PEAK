"""Support for 'zope.publisher'"""

from peak.api import *
from interfaces import *
from zope.publisher.base import DefaultPublication


__all__ = [
    'BasePublication', 'HTTP', 'XMLRPC', 'Browser',
]































class BasePublication(binding.Base, DefaultPublication):

    """Base publication policy"""

    app = binding.requireBinding("Application to be published")


    def beforeTraversal(self, request):

        """Begin transaction and attempt authentication"""

        super(BasePublication,self).beforeTraversal(request)
        storage.begin(self.app)

        # XXX try to authenticate here


    def callTraversalHooks(self, request, ob):
        pass    # XXX try local authentication if user not yet found


    def afterTraversal(self, request, ob):
        pass    # XXX try local authentication if user not yet found


    def afterCall(self, request):
        """Commit transaction after successful hit"""
        storage.commit(self.app)


    def handleException(self, object, request, exc_info, retry_allowed=1):
        """Abort transaction and delegate error handling to response"""

        try:
            storage.abort(self.app)
            request.response.handleException(exc_info)
        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None

class HTTP(BasePublication):

    def afterCall(self,request):

        """Handle "HEAD" method by truncating output"""
        
        super(HTTP,self).afterCall(request)

        if request.method=="HEAD":
            # XXX this doesn't handle streaming; there really should be
            # XXX a different response class for HEAD; Zope 3 should
            # XXX probably do it that way too.
            request.response.setBody('')


class XMLRPC(HTTP):

    """XMLRPC support"""

    def traverseName(self,request,ob,name):
        # XXX should try for a "methods" view of 'ob'
        return super(XMLRPC,self).traverseName(request,ob,name)


class Browser(HTTP):

    """DWIM features for human viewers"""

    def getDefaultTraversal(self, request, ob):
        # XXX this should figure out a default traversal for human viewers
        return ob, ()



    

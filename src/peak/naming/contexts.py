"""Base classes for naming contexts"""

from Interfaces import *
from Names import *
import SPI


def URLsNotAccepted(self, name):
    """Default operation handler for URL-type names"""
    raise InvalidNameException("Did not expect URL: %r" % name)


NNS_NAME = toName('/')

_marker = object()


























class AbstractContext(object):

    __implements__ = IBasicContext

    _envWritten = 0
    _scheme = None
    _acceptURLs = 1

    def __init__(self, env):
        self._environ = env

    def _beforeEnvWrite(self, key, value=_marker):
        if self._envWritten: return
        self._environ = self._environ.copy()
        self._envWritten = 1


    def addToEnvironment(self, key, value):
        self._beforeEnvWrite(key,value)
        self._environ[key] = value

    def removeFromEnvironment(self, key):
        self._beforeEnvWrite(key)
        del self._environ[key]

    def getEnvironment(self):

        if self._envWritten:
            return self._environ.copy()

        return self._environ


    def close(self):
        if hasattr(self,'_environ'):
            del self._environ





    def _performOp(self, name,
                    handleLocal, passThru,
                    handleURL=URLsNotAccepted, handleNNS=None):
    
        """Perform a naming operation"""

        name = toName(acceptURL = self._acceptURLs)

        if name.isURL:
            scheme = name.scheme
            
            if name.scheme != self._scheme:
                schemeCtx = SPI.getURLContext(scheme, self.getEnvironment())
    
                if schemeCtx is None:
                    raise InvalidNameException(
                        "Unknown scheme %s in %r" % (scheme,name)
                    )

                return passThru(schemeCtx, name)

            return handleURL(name)

        try:
            mine, rest = self._splitName(name)
            
            if not rest:
                # It's all local
                return handleLocal(mine)

            elif len(rest)==1 and not rest[0]:
                # Empty name for next name part (e.g. trailing /)
                # So operation is on implicit NNS pointer
                return (handleNNS or self._processJunction)(mine)
                
            else:
                # Both local and non-local parts, so work it out
                obj = self._resolveIntermediateNNS(mine,rest)
                raise self._fillInCPE(obj, mine, rest)


        except CannotProceedException, e:
            cctx = SPI.getContinuationContext(e)    # XXX
            return passThru(cctx, e.getRemainingName())


    def _resolveIntermediateNNS(self, mine, rest, newName=None):
        """Find the next naming system after resolving 'localName'"""
        pass # XXX


    def _fillInCPE(self, resolvedObj, altName, remainingName):
        """Return an appropriate CannotProceedException"""
        pass # XXX


    def _processJunction(self,name):

        """Raise a CannotProceedException targeting the appropriate junction"""

        if not name:
            ref = RefAddr("nns", self)  # XXX???
            raise self._fillInCPE(ref, NNS_NAME, None)

        else:
            try:
                target = self._lookup
            except NamingException, e:
                e.appendRemainingComponent("")  # XXX
                raise e

            raise self._fillInCPE(target, name, NNS_NAME)










    def _numberOfLocalNameParts(self, name):

        """Override this to change from "strong" to "weak" NS separation

            * For static weak separation, parse 'name' and return the number
              of elements which are considered part of the current namespace

            * For dynamic weak separation, simply 'return len(name)', which
              will treat all the name portions as local until proven otherwise.

            By default, this method assumes "strong" namespace separation,
            which means the first name component is assumed to be in the
            current namespace, and all others are assumed to be in subsequent
            namespaces.
        """

        return 1


    def _splitName(self, name):

        """Return a tuple '(localpart,nonlocalpart)' from 'name'"""

        if name.isCompound:
            return name, None

        if not name or not name[0]:
            localElements = 0
        else:
            localElements = self._numberOfLocalNameParts(name)

        return (
            CompositeName(name[:localElements]),
            CompositeName(name[localElements:])
        )






class InitialContext(AbstractContext):
    
    def lookup(self, name, requiredInterface=None):

        def lookupName(name):

            if not name:
                # Return a copy of self
                return self.__class__(self.getEnvironment())

            else:
                pass    # XXX return self._lookup(name,requiredInterface)
                
        def passThru(ctx, name):
            return ctx.lookup(name,requiredInterface)

        return self._performOp(name, lookupName, passThru)


    def asReference(self, name):
        pass # XXX

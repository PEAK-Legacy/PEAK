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
    _nameClass = CompoundName

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

    def clone(self):
        return self.__class__(self.getEnvironment())

    def _performOp(self, name,
                    handleLocal, passThru,
                    handleURL=URLsNotAccepted, handleNNS=None,
                    opInterface=IBasicContext):
    
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
                return handleLocal(mine)    # It's all local


            elif len(rest)==1 and not rest[0]:

                # Empty name for next name part (single trailing /)
                # So operation is on the NNS pointer *itself*

                return (handleNNS or self._processJunction)(mine)


            elif not mine or not filter(None,rest):

                # Name starts with "/" or ends with multiple slashes;
                # It crosses namespaces, but the operation target is
                # on the far side.  So look it up and point the CPE there.
                # We also drop the first element of 'rest' from the
                # 'remainingName' if it's empty.  This is needed because
                # we end up here if '_resolveIntermediateNNS()' finds a
                # non-junction on a non-empty 'mine'.  (Ugh!  But this
                # is how the JNDI tutorial example does it.)
                
                obj = self._lookup_nns(mine)
                if not rest[0]: rest = CompositeName(rest[1:])
                raise self._fillInCPE(obj, mine, rest)

            else:
                # We have both local and non-local parts, so work it out
                obj = self._resolveIntermediateNNS(mine,rest)
                raise self._fillInCPE(obj, mine, rest)


        except CannotProceedException, e:
            cctx = SPI.getContinuationContext(e, opInterface)    # XXX
            return passThru(cctx, e.remainingName)


    def _fillInCPE(self, resolvedObj, altName, remainingName):

        """Return an appropriate CannotProceedException"""

        return CannotProceedException(
            resolvedObj   = resolvedObj,
            altName       = altName,
            remainingName = remainingName,
            altNameCtx    = self,
            environment   = self.getEnvironment(),
        )


    def _processJunction(self,name):

        """Raise a CannotProceedException targeting the appropriate junction"""

        if not name:
            ref = RefAddr("nns", self)  # XXX???
            raise self._fillInCPE(ref, NNS_NAME, None)

        else:
            try:
                target = self._lookup_internal(name)

            except NamingException, e:
                e.remainingName += NNS_NAME
                raise e

            raise self._fillInCPE(target, name, NNS_NAME)











    def _resolveIntermediateNNS(self, mine, rest, newName=None):

        """Find the next naming system after resolving 'mine'"""

        try:
            obj = self._lookup_internal(mine)

            if isinstance(obj,self.__class__):
              
                # Same or subclass, must not be a junction

                cpe = self._fillInCPE(obj, mine, NNS_NAME+rest)
                cpe.remainingNewName = newName


            elif not IBasicContext.isImplementedBy(obj):
                
                # Not a context, make it an NNS reference
                
                ref = RefAddr("nns", obj)  # XXX???
                cpe = self._fillInCPE(ref, mine + NNS_NAME, rest)


            else:
                # It's a context, so just return it
                return obj


        except NamingException, e:
            # Make sure the remaining name portion includes the 'rest'
            e.remainingName += rest
            raise e


        # Throw the error we worked out
        raise cpe





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
            return CompositeName([name]), None

        if not name or not name[0]:
            localElements = 0
        else:
            localElements = self._numberOfLocalNameParts(name)

        nameClass = self._nameClass

        mine = CompositeName(
            [ toName(part, nameClass) for part in name[:localElements] ]
        )

        rest = CompositeName(name[localElements:])       
        return mine, rest


    # The real implementation stuff!

    def _lookup_internal(self, name, requiredInterface=None):
        """'name' is always a composite name of compound names"""

        if name:
            raise NotImplementedError
        else:
            return self.clone()


    def _lookup_nns(self, name):
        """Return next naming system for 'name'"""
        self._processJunction(name) # raises a CPE



























class InitialContext(AbstractContext):
    
    def lookup(self, name, requiredInterface=None):

        def lookupName(name):

            if not name:
                # Return a copy of self
                return self.__class__(self.getEnvironment())

            else:
                pass    # XXX return self._lookup_internal(name,requiredInterface)
                
        def passThru(ctx, name):
            return ctx.lookup(name,requiredInterface)

        return self._performOp(name, lookupName, passThru)


    def asReference(self, name):
        pass # XXX

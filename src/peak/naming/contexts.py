"""Base classes for naming contexts"""

from Interfaces import *
from Names import *
import SPI

_marker = object()


































class AbstractContext(object):

    __implements__ = IBasicContext

    _envWritten = 0
    _scheme = None
    _acceptURLs = 1
    _makeName = CompoundName

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

    def copy(self):
        return self.__class__(self.getEnvironment())

    def _getNextContext(self, operation):

        """Find the next naming system after resolving local part"""

        if not operation.localName:
        
            # It's on the NNS itself...
            
            operation.skipNNSboundary()
            return RefAddr("nns", self)  # XXX???


        obj = self._lookup(operation)

        if isinstance(obj,self.__class__):
          
            # Same or subclass, must not be a junction;
            # so delegate the NNS lookup to it
            
            operation.forceNNSboundary()
            return obj
                

        elif not IBasicContext.isImplementedBy(obj):
            
            # Not a context?  make it an NNS reference

            operation.skipNNSboundary()
            return RefAddr("nns", obj)  # XXX???

        else:
            # It's a context, so just return it
            return obj


    def _supportsScheme(self, scheme):
        return scheme==self._scheme




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

        makeName = self._makeName

        mine = CompositeName(
            [ toName(part, makeName) for part in name[:localElements] ]
        )

        rest = name[localElements:]
        return mine, rest



    # The real implementation stuff goes here...

    def _lookup(self, operation):
        raise NotImplementedError

    _search = _list = _rename = _getAttributes = _modifyAttributes = \
    _unbind = _createSubcontext = _destroySubcontext = _lookupLink = \
    _listBindings = _lookup

    def _bind(self, operation, rebind=0):
        raise NotImplementedError





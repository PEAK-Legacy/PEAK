"""Base classes for naming contexts"""

from Interfaces import *
from Names import *
import SPI


NNS_NAME = toName('/')

_marker = object()































class Operation(object):

    remainingNewName = None

    def __init__(self, ctx, name, requiredInterface=IBasicContext):

        self.ctx, self.requiredInterface = ctx, requiredInterface
        
        name = self.name = toName(name, acceptURL=ctx._acceptURLs)

        if name.isURL:

            self.localName, self.remainingName = name.scheme, name.body
            
            if not ctx._supportsScheme(name.scheme):
            
                schemeCtx = SPI.getURLContext(name.scheme,ctx.getEnvironment())
    
                if schemeCtx is None:
                    raise InvalidNameException(
                        "Unknown scheme %s in %r" % (name.scheme,name)
                    )

                self.ctx = schemeCtx
                self.resType = 'resolve_passthru'
                
            else:
                self.resType = 'resolve_url'


        else:
            mine, rest = ctx._splitName(name)
            self.localName, self.remainingName = mine, rest

            self.resType = self.getResolutionType(mine, rest)






    def getResolutionType(self, mine, rest):

        if not rest:
            # (mine=?, rest=[])
            return 'resolve_local'  # It's all local

        if mine:
            # (mine=[...], rest=[...])
            return 'resolve_intermediate'          

        elif not rest[0] and len(rest)==1:
            # (mine=[], rest=[''])
            return 'resolve_nns_ptr'

        else:
            # (mine=[], rest=[...])
            return 'resolve_intermediate'
            

    def forceNNSboundary(self):
        if not self.remainingName or self.remainingName[0]:
            self.remainingName = NNS_NAME + self.remainingName


    def skipNNSboundary(self):

        if self.remainingName and not self.remainingName[0]:
            self.remainingName = self.remainingName[1:]
            
        operation.localName += NNS_NAME











    def resolve_url(self):
        raise NotImplementedError

    resolve_local = resolve_nns_ptr = resolve_passthru = resolve_url


    def resolve_intermediate(self):
                
        # We have both local and non-local parts, so work it out

        self.resolvedObj = self.ctx._getNextContext(self)
        self.ctx = SPI.getContinuationContext(self.makeCPE())
        return self.resolve_passthru()




























    def __call__(self, *args, **kw):

        self.args, self.kw = args, kw

        try:            
            return getattr(self, self.resType)()

        except CannotProceedException, cpe:
            return self.resolve_cpe(cpe)


    def resolve_cpe(self, cpe):

        self.ctx = SPI.getContinuationContext(cpe)
        
        self.remainingName    = cpe.remainingName
        self.remainingNewName = cpe.remainingNewName

        return self.resolve_passthru()


    def makeCPE(self):
        return CannotProceedException(
            resolvedObj      = self.resolvedObj,
            altName          = self.localName,
            remainingName    = self.remainingName,
            remainingNewName = self.remainingNewName,
            altNameCtx       = self.ctx,
            environment      = self.ctx.getEnvironment(),
            requiredInterface= self.requiredInterface
        )










class NonbindingOperation(Operation):

    def resolve_nns_ptr(self):
        return self.resolve_intermediate()


class RenameOperation(NonbindingOperation):

    def __init__(self, ctx, name, newName, requiredInterface=IWriteContext):

        super(RenameOperation,self).__init__(self,ctx,name,requiredInterface)

        target = Operation(ctx, newName, requiredInterface)
        self.targetResType    = target.resType
        self.newName          = target.name
        self.newLocal         = target.localName
        self.remainingNewName = target.remainingName
        
        if self.targetResType<>self.resType \
           or self.resType not in ('resolve_url','resolve_local') \
           and self.newLocal<>self.localName:
           
                raise InvalidNameException(
                    "Incompatible names for rename", name, newName
                )


    def forceNNSboundary(self):
        super(RenameOperation,self).forceNNSboundary()
        if not self.remainingNewName or self.remainingNewName[0]:
            self.remainingNewName = NNS_NAME + self.remainingNewName


    def skipNNSboundary(self):
        super(RenameOperation,self).skipNNSboundary()
        if self.remainingNewName and not self.remainingNewName[0]:
            self.remainingNewName = self.remainingNewName[1:]




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

        nameClass = self._nameClass

        mine = CompositeName(
            [ toName(part, nameClass) for part in name[:localElements] ]
        )

        rest = name[localElements:]
        return mine, rest


    # The real implementation stuff!

    def _lookup(self, operation):
        """'mine' is always a composite name of compound names"""

        if mine:
            raise NotImplementedError
        else:
            return self.copy()





        




























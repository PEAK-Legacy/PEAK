from peak.naming.api import ParsedURL, IAddress

import re
import peak.running.lockfiles

class lockfileURL(ParsedURL):

    __implements__ = IAddress

    _supportedSchemes = (
        'lockfile', 'shlockfile', 'flockfile', 'winflockfile',
        'nulllockfile'
    )

    __fields__     = 'scheme', 'body'

    def retrieve(self, refInfo, name, context, attrs=None):
        lockfiles = peak.running.lockfiles
        
        if self.scheme == 'lockfile':
            return lockfiles.LockFile(self.body)
        elif self.scheme == 'nulllockfile':
            return lockfiles.NullLockFile()
        elif self.scheme == 'shlockfile':
            return lockfiles.SHLockFile(self.body)
        elif self.scheme == 'flockfile':
            return lockfiles.FLockFile(self.body)
        elif self.scheme == 'winflockfile':
            return lockfiles.WinFLockFile(self.body)
    
    def fromArgs(klass, scheme, body):
        return tuple.__new__(klass, (scheme, body))

    fromArgs = classmethod(fromArgs)

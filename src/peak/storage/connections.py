from peak.api import binding
from transactions import TransactionComponent
from interfaces import *

__all__ = [ 'ManagedConnection', ]


class ManagedConnection(TransactionComponent):

    __implements__ = IManagedConnection

    _connection = binding.Once(lambda s,d,a: s._open())
    _closeASAP = False


    def closeASAP(self):
        """Close the connection as soon as it's not in a transaction"""
        
        if self.inTransaction:
            self._closeASAP = True
        else:
            self.close()


    def close(self):
        """Close the connection immediately"""
        
        have = self.__dict__.has_key

        if have('_connection'):
            self._close()
            del self._connection

        if have('_closeASAP'):
            del self._closeASAP






    def finishTransaction(self, txnService, committed):

        super(ManagedConnection,self).finishTransaction(txnService, committed)
        
        if self._closeASAP:
            self.close()


    def _open(self):
        """Return new "real" connection to be saved as 'self._connection'"""
        raise NotImplementedError


    def _close(self):
        """Actions to take before 'del self._connection', if needed."""

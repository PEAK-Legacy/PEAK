from peak.api import binding
from transactions import TransactionComponent
from interfaces import *

__all__ = [ 'ManagedConnection', ]


class ManagedConnection(TransactionComponent):

    __implements__ = IManagedConnection

    connection = binding.Once(lambda s,d,a: s._open())
    _closeASAP = False

    txnAttrs = TransactionComponent.txnAttrs + ('txnTime',)

    def closeASAP(self):
        """Close the connection as soon as it's not in a transaction"""

        if self.inTransaction:
            self._closeASAP = True
        else:
            self.close()


    def close(self):
        """Close the connection immediately"""

        have = self.__dict__.has_key

        if have('connection'):
            self._close()
            del self.connection

        if have('_closeASAP'):
            del self._closeASAP





    def finishTransaction(self, txnService, committed):

        super(ManagedConnection,self).finishTransaction(txnService, committed)

        if self._closeASAP:
            self.close()


    def _open(self):
        """Return new "real" connection to be saved as 'self.connection'"""
        raise NotImplementedError


    def _close(self):
        """Actions to take before 'del self.connection', if needed."""


    def txnTime(self,d,a):
        """Per-transaction timestamp, based on this connection's clock

            Note that this default should be overridden for subclasses that
            interact with a database that has a clock!  An SQL connection,
            for example, should perform a query against the database to get
            the DB server's idea of the time.  Connections which have no
            notion of time should just return the transaction's timestamp,
            and so this default implementation will do.  Note that if you
            override this implementation, you must ensure that the
            connection has joined the transaction first!
        """
        return self.txnSvc.getTimestamp()

    txnTime = binding.Once(txnTime)


    def joinTxn(self):
        """Join the current transaction, if not already joined"""
        return self.txnSvc

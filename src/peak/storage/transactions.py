from peak.api import binding
from interfaces import *
from time import time

__all__ = [
    'NullSavepoint', 'FailureSavepoint', 'MultiSavepoint',
    'ZODBTransactionService', 'AbstractParticipant'
]


class AbstractTransactionService(binding.Component):

    """Basic implementation for stuff needed by pretty much any txn service"""
    
    __implements__ = ITransactionService


    participants = binding.New(list)

    timestamp = None

    def subscribe(self, participant):

        # XXX need state check for not past "ready" stage

        if participant not in self.participants:
            self.participants.append(participant)


    def unsubscribe(self, participant):

        if self.isActive():
            raise TransactionInProgress

        if participant in self.participants:
            self.participants.remove(participant)





    def _savepoint(self):

        """Create a savepoint

        Ask all participants if they're ready to save, up to N+1 times (where
        N is the number of participants), until all agree they are ready, or
        an exception occurs.  N+1 iterations is sufficient for any acyclic
        structure of cascading data managers.  Any more than that, and either
        there's a cascade cycle or a broken participant is always returning a
        false value from its readyForSavepoint() method.

        Once all participants are ready, assemble and return a savepoint.
        """
    
        if not self.isActive():
            raise OutsideTransaction

        tries = 0
        unready = True
        
        while unready and tries <= len(self.participants):
            unready = [
                p for p in self.participants if not p.readyForSavepoint(self)
            ]
            tries += 1

        if unready:
            raise NotReadyError(unready)

        spl = [p.getSavepoint(self) for p in self.participants]
        
        return MultiSavepoint(spl)
        








    def _prepare(self):

        """Get votes from all participants

        Ask all participants if they're ready to vote, up to N+1 times (where
        N is the number of participants), until all agree they are ready, or
        an exception occurs.  N+1 iterations is sufficient for any acyclic
        structure of cascading data managers.  Any more than that, and either
        there's a cascade cycle or a broken participant is always returning a
        false value from its readyToVote() method.

        Once all participants are ready, ask them all to vote."""
    
        tries = 0
        unready = True
        
        while unready and tries <= len(self.participants):
            unready = [p for p in self.participants if not p.readyToVote(self)]
            tries += 1

        if unready:
            raise NotReadyError(unready)

        for p in self.participants:
            p.voteForCommit(self)

        return True

    def begin(self, **info):

        if self.isActive():
            raise TransactionInProgress
            
        self.addInfo(**info)
        self.timestamp = time()

        self._begin()

        for p in self.participants:
            p.beginTransaction(self)
            
    def commit(self):

        if not self.isActive():
            raise OutsideTransaction

        self._prepare()
        self._commit()


    def _commit(self):
        for p in self.participants:
            p.commitTransaction(self)


    def abort(self):

        if not self.isActive():
            raise OutsideTransaction

        self._abort()


    def _abort(self):
        for p in self.participants:
            p.abortTransaction(self)


    def getTimestamp(self):

        """Return the time that the transaction began, in time.time()
        format, or None if no transaction in progress."""

        if self.isActive():
            return self.timestamp
            






class AbstractParticipant(object):

    def beginTransaction(self, txnService):
        pass

    def readyForSavepoint(self, txnService):
        return True

    def getSavepoint(self, txnService):
        return NullSavepoint

    def readyToVote(self, txnService):
        return True

    def voteForCommit(self, txnService):
        pass

    def commitTransaction(self, txnService):
        pass

    def abortTransaction(self, txnService):
        pass



















class _ZODBTxnProxy(object):

    def __init__(self, txnService):
        self.txnService = txnService

    def prepare(self,txn):
        return self.txnService._prepare()

    def abort(self,txn):
        self.txnService._abort()

    def commit(self,txn):
        self.txnService._commit()

    def savepoint(self,txn):
        return self.txnService._savepoint()

























class ZODBTransactionService(AbstractTransactionService):

    ztxn = None
    
    def _begin(self):
        from Transaction import get_transaction
        txn = self.ztxn = get_transaction()
        txn.join(_ZODB4TxnProxy(self))


    def abort(self):
    
        if not self.isActive():
            raise OutsideTransaction

        self.ztxn.abort()


    def commit(self):

        if not self.isActive():
            raise OutsideTransaction

        self.ztxn.commit()


    def savepoint(self):

        if not self.isActive():
            raise OutsideTransaction

        return self.ztxn.savepoint()


    def isActive(self):
        return self.ztxn is not None

    def _cleanup(self):
        self.ztxn = None


class _NullSavepoint(object):

    __implements__ = ISavepoint
    __slots__ = []

    def rollback(self):
        pass

NullSavepoint = _NullSavepoint()



class FailureSavepoint(object):

    __implements__ = ISavepoint
    __slots__ = 'dm'

    def __init__(self,dm):
        self.dm = dm

    def rollback(self):
        raise CannotRevertException(dm)
        


class MultiSavepoint(object):

    __implements__ = ISavepoint
    __slots__ = 'savepoints'

    def __init__(self,savepoints):
        self.savepoints = savepoints

    def rollback(self):
        for sp in self.savepoints:
            sp.rollback()

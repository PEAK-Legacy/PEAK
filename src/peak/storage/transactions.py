from peak.api import binding
from interfaces import *
from time import time

__all__ = [
    'NullSavepoint', 'FailureSavepoint', 'MultiSavepoint'
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






    def savepoint(self):

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

        spl = [p.getSavepoint() for p in self.participants]
        
        return MultiSavepoint(spl)
        








    def _vote(self):

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
            p.voteForCommit()


    def begin(self, **info):

        if self.isActive():
            raise TransactionInProgress
            
        self.addInfo(**info)
        self.timestamp = time()

        self._begin()





    def getTimestamp(self):

        """Return the time that the transaction began, in time.time()
        format, or None if no transaction in progress."""

        if self.isActive():
            return self.timestamp
            

































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

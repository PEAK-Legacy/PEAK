from peak.api import binding
from interfaces import *
from time import time
import sys

__all__ = [
    'TransactionService', 'AbstractParticipant', 'TransactionComponent',
    'BasicTxnErrorHandler'
]


class BasicTxnErrorHandler(object):

    """Simple error handling policy: no logging, retries, etc."""
    
    __implements__ = ITransactionErrorHandler

    def voteFailed(self, txnService, participant):
        txnService.fail()
        raise

    def commitFailed(self, txnService, participant):
        # XXX Hosed!!!
        txnService.fail()
        raise

    def abortFailed(self, txnService, participant):
        # remove and retry after fail
        txnService.removeParticipant(participant)
        raise
        
    def finishFailed(self, txnService, participant, committed):
        # ignore error
        txnService.removeParticipant(participant)







class TransactionState(binding.Base):

    """Helper object representing a single transaction's state"""

    participants = binding.New(list)
    info         = binding.New(dict)
    timestamp    = None
    safeToJoin   = True
    cantCommit   = False



class TransactionService(binding.AutoCreated):

    """Basic transaction service component"""
    
    __implements__ = ITransactionService
    _provides      = __implements__

    state          = binding.New(TransactionState)
    errorHandler   = binding.New(BasicTxnErrorHandler)
    
    def join(self, participant):

        if self.state.cantCommit:
            raise BrokenTransaction

        elif not self.isActive():
            raise OutsideTransaction

        elif self.state.safeToJoin:

            if participant not in self.state.participants:
                self.state.participants.append(participant)

        else:
            raise TransactionInProgress




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
        state = self.state

        while unready and tries <= len(state.participants):
            unready = [p for p in state.participants if not p.readyToVote(self)]
            tries += 1

        if unready:
            raise NotReadyError(unready)


        self.state.safeToJoin = False
        
        for p in state.participants:
            try:
                p.voteForCommit(self)
            except:
                self.errorHandler.voteFailed(self,p)

        return True







    def begin(self, **info):

        if self.isActive():
            raise TransactionInProgress
            
        self.state.timestamp = time()
        self.addInfo(**info)


    def commit(self):

        if not self.isActive():
            raise OutsideTransaction

        if self.state.cantCommit:
            raise BrokenTransaction

        self._prepare()

        for p in self.state.participants:
            try:
                p.commitTransaction(self)
            except:
                self.errorHandler.commitFailed(self,p)

        self._cleanup(True)


    def fail(self):

        if not self.isActive():
            raise OutsideTransaction

        self.state.cantCommit = True
        self.state.safeToJoin = False


    def removeParticipant(self,participant):
        self.state.participants.remove(participant)


    def abort(self):

        if not self.isActive():
            raise OutsideTransaction

        self.fail()
        
        for p in self.state.participants[:]:
            try:
                p.abortTransaction(self)
            except:
                self.errorHandler.abortFailed(self,p)

        self._cleanup(False)


    def getTimestamp(self):

        """Return the time that the transaction began, in time.time()
        format, or None if no transaction in progress."""

        return self.state.timestamp


    def addInfo(self, **info):
    
        if self.state.cantCommit:
            raise BrokenTransaction

        elif self.state.safeToJoin:
            self.state.info.update(info)

        else:
            raise TransactionInProgress
    


    def getInfo(self):
        return self.state.info


    def _cleanup(self, committed):

        for p in self.state.participants[:]:
            try:
                p.finishTransaction(self,committed)
            except:
                self.errorHandler.finishFailed(self,p,committed)

        del self.state


    def isActive(self):
        return self.state.timestamp is not None




























class AbstractParticipant(object):

    __implements__ = ITransactionParticipant

    def readyToVote(self, txnService):
        return True

    def voteForCommit(self, txnService):
        pass

    def commitTransaction(self, txnService):
        pass

    def abortTransaction(self, txnService):
        pass

    def finishTransaction(self, txnService, committed):
        pass























class TransactionComponent(binding.AutoCreated, AbstractParticipant):

    """Object that has a 'txnSvc' and auto-joins transactions"""

    # XXX add binding.AutoCreated.__implements__ once binding.interfaces exist

    inTransaction = False
    
    def txnSvc(self,d,a):

        """Our TransactionService (auto-joined when attribute is accessed)"""

        ts = binding.findUtility(ITransactionService)
        ts.join(self)
        self.inTransaction = True
        
        return ts

    txnSvc = binding.Once(txnSvc)


    def finishTransaction(self, txnService, committed):

        """Ensure that subsequent transactions will require re-registering"""
        
        del self.txnSvc, self.inTransaction




















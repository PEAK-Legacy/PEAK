from peak.api import binding
from interfaces import *
from transactions import TransactionComponent

__all__ = ['EntityDM']


class EntityDM(TransactionComponent):

    __implements__ = IDataManager

    resetStatesAfterTxn = True

    def __getitem__(self, oid, state=None):

        if self.resetStatesAfterTxn:
            # must always be used in a txn
            self.txnSvc
        
        ob = self.cache.get(oid,self)

        if ob is not self:
            return ob

        ob = self.ghost(oid,state)

        ob._p_jar = self
        ob._p_oid = oid

        if state is None:
            ob._p_deactivate()
        else:
            ob.__setstate__(state)

        self.cache[oid] = ob

        return ob

    preloadState = __getitem__


    def oidFor(self, ob):

        if ob._p_jar is self:

            oid = ob._p_oid

            if oid is None:
                # force it to have an ID by saving it
                ob._p_changed = 1
                self.flush(ob)
                return ob._p_oid

            else:
                return oid

        else:
            return self.thunk(ob)


    def newItem(self,klass=None):

        if klass is None:
            klass = self.defaultClass

        if klass is None:
            raise NotImplementedError

        ob=klass()
        ob.__setstate__(self.defaultState(ob))
        ob._p_jar = self

        self.register(ob)
        return ob


    # Set/state management

    dirty = binding.New(dict)
    saved = binding.New(dict)


    def flush(self, ob=None):

        markSaved = self.saved.setdefault
        dirty = self.dirty

        obs = ob is None and self.dirty.values() or [ob]

        for ob in obs:

            if ob._p_oid is None:

                # No oid, it's a new object that needs saving
                oid = ob._p_oid = self.new(ob)
                self.cache[oid]=ob

            else:
                # just save it the ordinary way
                self.save(ob)

            # Update status flags and object sets
            key = id(ob)

            markSaved(key,ob)
            del dirty[key]

            del ob._p_changed















    # Private abstract methods/attrs

    from caches import WeakCache as cache

    defaultClass = None

    def ghost(self, oid, state=None):

        klass = self.defaultClass

        if klass is None:
            raise NotImplementedError

        return klass()

    def load(self, oid):
        raise NotImplementedError

    def save(self, ob):
        raise NotImplementedError

    def new(self, ob):
        raise NotImplementedError

    def defaultState(self, ob):
        raise NotImplementedError

    def thunk(self, ob):
        raise NotImplementedError












    # Persistence.IPersistentDataManager methods

    def setstate(self, ob):

        if self.resetStatesAfterTxn:
            # must always be used in a txn
            self.txnSvc

        oid = ob._p_oid
        assert oid is not None
        ob.__setstate__(self.load(oid))


    def register(self, ob):
    
        # precondition:
        #   object has been changed since last save

        # postcondition:
        #   ob is in 'dirty' set
        #   DM is registered w/transaction if not previously registered

        key = id(ob)
        
        # Ensure it's in the 'dirty' set
        self.dirty.setdefault(key,ob)

        # Ensure that we have a transaction service and we've joined
        # the transaction in progress...
        
        return self.txnSvc


    def mtime(self, ob):
        pass    # return None






    # ITransactionParticipant methods
    
    def readyToVote(self, txnService):
        if self.dirty:
            self.flush()
            return False
        else:
            return True


    def voteForCommit(self, txnService):
        # Everything should have been written by now...  If not, it's VERY BAD
        # because the DB we're storing to might've already gotten a tpc_vote(),
        # and won't accept writes any more.  So raise holy hell if we're dirty!
        assert not self.dirty


    def commitTransaction(self, txnService):
        self.saved.clear()


    def abortTransaction(self, txnService):

        for set in self.dirty, self.saved:
            for ob in set.values():
                ob._p_deactivate()

            set.clear()

    def finishTransaction(self, txnService, committed):

        if self.resetStatesAfterTxn:

            for ob in self.cache.values():
                ob._p_deactivate()

        super(EntityDM,self).finishTransaction(txnService,committed)














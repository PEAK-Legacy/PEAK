from peak.api import binding, model
from interfaces import *
from transactions import TransactionComponent
from Persistence import Persistent
from peak.util.ListProxy import ListProxy
from lazy_loader import LazyLoader

__all__ = [
    'FacadeDM', 'QueryDM', 'EntityDM', 'PersistentQuery', 'QueryLink', 
]































class FacadeDM(binding.Component):

    """DM that just returns objects from other DM(s) via a different key"""

    __implements__ = IKeyableDM

    def __getitem__(self, oid, state=None):

        ob = self.cache.get(oid,self)

        if ob is not self:

            # double-check identity
            if oid==self.oidFor(ob):
                return ob

            # Oops, key no longer valid, drop it
            del self.cache[oid]

        ob = self.retrieve(oid, state)
        
        if ob is not None:
            self.cache[oid] = ob
            return ob

        raise KeyError, oid


    preloadState = __getitem__

    cache = binding.New('peak.storage.caches:WeakCache')

    def retrieve(self, oid, state=None):
        """Look up 'oid' in underlying storage and return it, or 'None'"""
        raise NotImplementedError

    def oidFor(self, ob):
        """Return this DM's OID for 'ob'; used to validate consistency"""
        raise NotImplementedError
        

class PersistentQuery(Persistent, ListProxy):

    """An immutable, persistent ListProxy for query results"""

    __slots__ = 'data', '__weakref__'

    def __getstate__(self):
        return self.data

    def __setstate__(self,state):
        self.data = list(state)






























class QueryLink(ListProxy):

    """PersistentQuery proxy for use in Collection, Sequence, or Reference"""

    __cacheData = None
    __localData = None

    def __init__(self, query):
        self.__query = query


    def data(self):
        # Discard cached form of query data when underlying query reloaded
        if self.__cacheData is not self.__query.data:
            self.__cacheData = self.__query.data
            self.__localData = self.__cacheData[:]
            
        return self.__localData

    data = property(data)


    def __isActive(self):
        return self.__query._p_state <> GHOST


    def __setitem__(self, i, item):
        if self.__isActive():
            self.data[i]=item

    def __delitem__(self, i):
        if self.__isActive():
            del self.data[i]


    def __setslice__(self, i, j, other):
        if self.__isActive():
            i = max(i, 0); j = max(j, 0)
            self.data[i:j] = self._cast(other)


    def __delslice__(self, i, j):
        if self.__isActive():
            i = max(i, 0); j = max(j, 0)
            del self.data[i:j]
    

    def __iadd__(self, other):
        if self.__isActive():
            self.data += self._cast(other)
        return self


    def append(self, item):
        if self.__isActive():
            self.data.append(item)


    def insert(self, i, item):
        if self.__isActive():
            self.data.insert(i, item)


    def remove(self, item):
        if self.__isActive():
            self.data.remove(item)


    def extend(self, other):
        if self.__isActive():
            self.data.extend(self._cast(other))











class QueryDM(TransactionComponent):

    resetStatesAfterTxn = True

    __implements__ = IDataManager

    def __getitem__(self, oid, state=None):

        if self.resetStatesAfterTxn:
            # must always be used in a txn
            self.joinedTxn
        
        ob = self.cache.get(oid,self)

        if ob is not self:
            return ob

        ob = self.ghost(oid,state)

        if isinstance(ob,Persistent):

            ob._p_jar = self
            ob._p_oid = oid

            if state is None:
                ob._p_deactivate()
            else:
                ob.__setstate__(state)

            self.cache[oid] = ob

        return ob

    preloadState = __getitem__







    # Private abstract methods/attrs

    cache = binding.New('peak.storage.caches:WeakCache')

    defaultClass = PersistentQuery

    def ghost(self, oid, state=None):

        klass = self.defaultClass

        if klass is None:
            raise NotImplementedError

        return klass()


    def load(self, oid, ob):
        raise NotImplementedError


    # Persistence.IPersistentDataManager methods

    def setstate(self, ob):

        if self.resetStatesAfterTxn:
            # must always be used in a txn
            self.joinedTxn

        oid = ob._p_oid
        assert oid is not None
        ob.__setstate__(self.load(oid,ob))


    def mtime(self, ob):
        pass    # return None

    def register(self, ob):
        raise TypeError("Attempt to modify query result", ob)



    # ITransactionParticipant methods

    def finishTransaction(self, txnService, committed):

        if self.resetStatesAfterTxn:

            for ob in self.cache.values():
                ob._p_deactivate()

        super(QueryDM,self).finishTransaction(txnService,committed)































class EntityDM(QueryDM):

    __implements__ = IWritableDM


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

    defaultClass = None

    def save(self, ob):
        raise NotImplementedError

    def new(self, ob):
        raise NotImplementedError

    def defaultState(self, ob):
        raise NotImplementedError

    def thunk(self, ob):
        raise NotImplementedError



    # Persistence.IPersistentDataManager methods

    def register(self, ob):

        # Ensure that we have a transaction service and we've joined
        # the transaction in progress...
        
        self.joinedTxn

        # precondition:
        #   object has been changed since last save

        # postcondition:
        #   ob is in 'dirty' set
        #   DM is registered w/transaction if not previously registered

        key = id(ob)
        
        # Ensure it's in the 'dirty' set
        self.dirty.setdefault(key,ob)

        return self.joinedTxn

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
                del ob._p_changed
                ob._p_deactivate()

            set.clear()







    









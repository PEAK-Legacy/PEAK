from peak.api import binding

__all__ = ['AbstractRack']

class AbstractRack(binding.Component):

    def __getitem__(self, oid, state=None):

        ob = self.cache.get(oid,self)

        if ob is not self:
            return ob

        ob = self.ghost(oid,state)
        ob._p_oid = oid
        ob._p_jar = self
        self.cache[oid] = ob

        return ob


    preloadState = __getitem__


    def oidFor(self, ob):

        if ob._p_jar is self:

            oid = ob._p_oid

            if oid is None:
                # force it to have an ID by saving it
                ob._p_changed = 1; self.commit(ob)
                return ob._p_oid

            else:
                return oid

        else:
            return self.thunk(ob)

    def flush(self):
        dirty = self.dirty.values()
        self.dirty.clear()
        map(self.commit, dirty)


    def newItem(self,klass=None):

        if klass is None:
            klass = self.defaultClass

        if klass is None:
            raise NotImplementedError

        ob=klass()
        ob.__setstate__(self.defaultState(ob))
        ob._p_jar = self

        return ob



    # Set/state management

    dirty            = binding.New(dict)

    committed        = binding.New(dict)

    commitInProgress = False












    # Private abstract methods/attrs

    cache = binding.requireBinding("a cache for ghosts and loaded objects")

    defaultClass = None

    def ghost(self, oid, state=None):

        klass = self.defaultClass

        if klass is None:
            raise NotImplementedError

        ob = klass()

        if state is not None:
            ob.__setstate__(state)


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
        oid = ob._p_oid
        assert oid is not None
        ob.__setstate__(self.load(oid))


    def register(self, ob):
    
        # precondition:
        #   object has been changed since last save

        # postcondition:
        #   ob is in 'dirty' set
        #   ob is registered with txn if not previously registered
        #      or if a top-level txn commit is in progress
        #      (we have to re-register ob so that it'll be saved again,
        #       since the precondition is that it changed since the last save)

        key = id(ob)
        
        # Ensure it's in the 'dirty' set
        self.dirty.setdefault(key,ob)

        if key not in self.committed or self.commitInProgress:
            pass # XXX register w/transaction here

        # ELSE: if the object has been saved before, and we're *not*
        # in a transaction commit, we don't need to register it again,
        # since the only way it could be in 'self.committed' is if it
        # was first registered via this routine.


    def mtime(self, ob):
        pass    # return None





    # Transaction.IDataManager methods
    
    def tpc_begin(self, transaction):
        self.commitInProgress = True

    def commit(self, ob, transaction=None):

        key = id(ob)
        dirty = self.dirty

        if key not in dirty:
            # ob isn't changed; this is normal because we might have written
            # it out during a flush() operation prior to transaction commit
            return

        # Ensure it's in the committed list, and not flagged dirty or changed

        del dirty[key]
        self.committed.setdefault(key,ob)
        del ob._p_changed

        if ob._p_oid is None:

            # No oid, it's a new object that needs saving
            oid = ob._p_oid = self.new(ob)
            self.cache[oid]=ob

        else:
            # just save it the ordinary way
            self.save(ob)

    def tpc_vote(self, transaction):
        # Everything should have been written by now...  If not, it's VERY BAD
        # because the DB we're storing to might've already gotten a tpc_vote(),
        # and won't accept writes any more.  So raise holy hell if we're dirty!
        assert not self.dirty

    def tpc_finish(self, transaction):
        self.committed.clear()
        self.commitInProgress = False

    def abort(self, ob, transaction):

        ob._p_deactivate()

        if self.committed:  

            # Note that 'dirty' objects don't matter here, since they will be
            # given individual abort calls by the transation.  Only if we
            # have committed objects (due to pre-commit flush() operations)
            # do we need to force their deactivation.

            self.tpc_abort(transaction)


    def tpc_abort(self, transaction):

        for set in self.dirty, self.committed:

            for ob in set.values():
                ob._p_deactivate()

            set.clear()

        self.commitInProgress = False



















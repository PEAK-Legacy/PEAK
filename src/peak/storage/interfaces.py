"""'Straw Man' Transaction Interfaces"""

from Interface import Interface
from Interface.Attribute import Attribute

__all__ = [
    'ITransactionService', 'ITransactionParticipant',
    'ITransactionErrorHandler', 'BrokenTransaction',
    'NotReadyError', 'TransactionInProgress', 'OutsideTransaction',
    'IRack', 'IRackImplementation',
]

class ITransactionService(Interface):

    """Manages transaction lifecycle, participants, and metadata.

    There is no predefined number of transactions that may exist, or
    what they are associated with.  Depending on the application
    model, there may be one per application, one per transaction, one
    per incoming connection (in server applications), or some other
    number.  The transaction package should, however, offer an API for
    managing per-thread (or per-app, if threads aren't being used)
    transactions, since this will probably be the most common usage
    scenario."""

    # The basic transaction lifecycle

    def begin(**info):
        """Begin a transaction.  Raise TransactionInProgress if
        already begun.  Any keyword arguments are passed on to the
        setInfo() method.  (See below.)"""

    def commit():
        """Commit the transaction, or raise OutsideTransaction if not in
        progress."""
        
    def abort():
        """Abort the transaction, or raise OutsideTransaction if not in
        progress."""


    def fail():
        """Force transaction to fail (i.e. no commits allowed, only aborts)"""

    # Managing participants

    def subscribe(participant):
        """Add 'participant' to the set of objects that will receive
        transaction messages.  Note that no particular ordering of
        participants should be assumed.  If the transaction is already
        active, 'participant' will receive a 'begin_txn()' message. If
        a commit or savepoint is in progress, 'participant' may also
        receive other messages to "catch it up" to the other
        participants.  However, if the commit or savepoint has already
        progressed too far for the new participant to join in, a
        TransactionInProgress error will be raised."""
        
    def removeParticipant(participant):
        """Force participant to be removed; for error handler use only"""

    # Getting/setting information about a transaction

    def isActive():
        """Return True if transaction is in progress."""
        
    def getTimestamp():
        """Return the time that the transaction began, in time.time()
        format, or None if no transaction in progress."""

    def addInfo(**info):
        """Update the transaction's metadata dictionary with the
        supplied keyword arguments.  This can be used to record
        information such as a description of the transaction, the user
        who performed it, etc. Note that the transaction itself does
        nothing with this information. Transaction participants will
        need to retrieve the information with 'getInfo()' and record
        it at the appropriate point during the transaction."""

    def getInfo():
        """Return a copy of the transaction's metadata dictionary"""
        

class ITransactionParticipant(Interface):

    """Participant in a transaction; may be a resource manager, a transactional
    cache, or just a logging/monitoring object.

    Event sequence is approximately as follows:

        subscribe(participant)
            ( readyToVote voteForCommit commitTransaction ) | abortTransaction

    An abortTransaction may occur at *any* point following subscribe(), and
    aborts the transaction.

    Generally speaking, participants fall into a few broad categories:

    * Database connections

    * Resource managers that write data to another participant, e.g. a
      storage manager writing to a database connection

    * Resource managers that manage their own storage transactions,
      e.g. ZODB Database/Storage objects, a filesystem-based queue, etc.

    * Objects which don't manage any transactional resources, but need to
      know what's happening with a transaction, in order to log it.

    Each kind of participant will typically use different messages to
    achieve their goals.  Resource managers that use other
    participants for storage, for example, won't care much about
    'voteForCommit()', while a resource manager that manages direct storage
    will care about 'voteForCommit()' very deeply!

    Resource managers that use other participants for storage, but
    buffer writes to the other participant, will need to pay close
    attention to the 'readyToVote()' message.  Specifically, they must
    flush all pending writes to the participant that handles their
    storage, and return 'False' if there was anything to flush.
    'readyToVote()' will be called repeatedly on *all* participants until
    they *all* return 'True', at which point the transaction will initiate
    the 'voteForCommit()' phase.

    By following this algorithm, any number of participants may be
    chained together, such as a persistence manager that writes to an
    XML document, which is persisted in a database table, which is
    persisted in a disk file.  The persistence manager, the XML
    document, the database table, and the disk file would all be
    participants, but only the disk file would actually use
    'voteForCommit()' and 'commitTransaction()' to handle a commit.
    All of the other participants would flush pending updates during the
    'readyToVote()' loop, guaranteeing that the disk file participant
    would know about all the updates by the time 'voteForCommit()' was
    issued, regardless of the order in which the participants received
    the messages."""       

    def readyToVote(txnService):
        """Transaction commit is beginning; flush dirty objects and
        enter write-through mode, if applicable.  Return a true
        value if nothing needed to be done, or a false value if
        work needed to be done.  DB connections will probably never
        do anything here, and thus will just return a true value.
        Object managers like Racks will write their objects and
        return false, or return true if they have nothing to write.
        Note: participants *must* continue to accept writes until
        'voteForCommit()' occurs, and *must* accept repeated writes
        of the same objects!"""

    def voteForCommit(txnService):
        """Raise an exception if commit isn't possible.  This will
        mostly be used by resource managers that handle their own
        storage, or the few DB connections that are capable of
        multi-phase commit."""

    def commitTransaction(txnService):
        """This message follows vote_commit, if no participants vetoed
        the commit.  DB connections will probably issue COMMIT TRAN
        here. Transactional caches might use this message to reset
        themselves."""





    def abortTransaction(txnService):
        """This message can be received at any time, and means the
        entire transaction must be rolled back.  Transactional caches
        might use this message to reset themselves."""

    def finishTransaction(txnService, committed):
        """The transaction is over, whether it aborted or committed."""


class ITransactionErrorHandler(Interface):

    """Policy object to handle exceptions issued by participants"""
    
    def voteFailed(txnService, participant):
        """'participant' raised exception during 'voteForCommit()'"""

    def abortFailed(txnService, participant):
        """'participant' raised exception during 'abortTransaction'"""
        
    def finishFailed(txnService, participant):
        """'participant' raised exception during 'finishTransaction()'"""
        
    def commitFailed(txnService, participant):
        """'participant' raised exception during 'commitTransaction()'"""
        

class NotReadyError(Exception):
    """One or more transaction participants were unready too many times"""

class TransactionInProgress(Exception):
    """Action not permitted while transaction is in progress"""

class OutsideTransaction(Exception):
    """Action not permitted while transaction is not in progress"""

class BrokenTransaction(Exception):
    """Transaction can't commit, due to participants breaking contracts
       (E.g. by throwing an exception during the commit phase)"""



# Rack interfaces

try:
    from Persistence.IPersistentDataManager import IPersistentDataManager

except ImportError:
    class IPersistentDataManager(Interface):
        # Temporary hack until we include Persistence in our setup.py...
        pass


class IRack(ITransactionParticipant, IPersistentDataManager):

    """Data manager for persistent objects or queries"""

    def __getitem__(oid):
        """Retrieve the persistent object designated by 'oid'"""
        
    def preloadState(oid, state):
        """Pre-load 'state' for object designated by 'oid' and return it"""
        
    def oidFor(ob):
        """Return an 'oid' suitable for retrieving 'ob' from this rack"""
        
    def newItem(klass=None):
        """Create and return a new persistent object of class 'klass'"""

    def flush(ob=None):
        """Sync stored state to in-memory state of 'ob' or all objects"""












class IRackImplementation(Interface):

    """Methods/attrs that must/may be redefined in an AbstractRack subclass"""
    
    cache = Attribute("a cache for ghosts and loaded objects")

    defaultClass = Attribute("Default class used for 'newItem()' method")

    def ghost(oid, state=None):
        """Return a ghost of appropriate class, based on 'oid' and 'state'"""

    def load(oid):
        """Load & return the state for 'oid', suitable for '__setstate__()'"""

    def save(ob):
        """Save 'ob' to underlying storage"""

    def new(ob):
        """Create 'ob' in underlying storage and return its new 'oid'"""

    def defaultState(ob):
        """Return a default '__setstate__()' state for a new 'ob'"""

    def thunk(ob):
        """Hook for implementing cross-database "thunk" references"""

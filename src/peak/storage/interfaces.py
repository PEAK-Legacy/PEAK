"""'Straw Man' Transaction Interfaces"""

from Interface import Interface
from Interface.Attribute import Attribute

__all__ = [
    'ITransactionService', 'ITransactionParticipant', 'ISavepoint'
    'NotReadyError', 'CannotRevertException', 'TransactionInProgress',
    'OutsideTransaction'
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
        TransactionInProgress error will be raised.

        Note: this is not ZODB!  Participants remain subscribed until
        they unsubscribe, or until the transaction object is
        de-allocated!"""
        
    def unsubscribe(participant):
        """Remove 'participant' from the set of objects that will
        receive transaction messages.  It can only be called when a
        transaction is not in progress, or in response to
        begin/commit/abort_txn() messages received by the
        unsubscribing participant.  Otherwise, TransactionInProgress
        will be raised."""

















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
        

    # "Sub-transaction" support
    
    def savepoint():
        """Request a write to stable storage, and return an ISavepoint
        instance for possible partial rollback via 'rollback()'.  This
        will most often be used simply to suggest a good time for in-memory
        data to be written out.  But it can also be used in conjunction
        with 'rollback()' to provide a 'nested transactions',
        if all participants support reverting to savepoints."""










class ISavepoint(Interface):

    """A point to which the transaction can be rolled back;

    (Can be used to implement nested transactions.)"""
    
    def rollback():
        """Roll state back to this savepoint, or raise CannotRevertException.

        Note that a given savepoint can only be rolled back once!  If you wish
        to retry a nested transaction, you'll need to re-issue a 'savepoint()'
        request following the rollback, and use the new savepoint object."""

    def revert(txnService):
        """Roll back to last savepoint, or raise
        CannotRevertException; Database connections whose underlying
        DB doesn't support savepoints should definitely raise
        CannotRevertException.  Resource managers that write data to other
        participants, should simply roll back state for all objects
        changed since the last savepoint, whether written through to
        the underlying storage or not.  Transactional caches may want
        to reset on this message, also, depending on their precise
        semantics. Note: this is not ZODB!  You will not get a
        revert() before an abort_txn(), just because a savepoint has
        occurred during the transaction!"""
        















class ITransactionParticipant(Interface):

    """Participant in a transaction; may be a resource manager, a
    transactional cache, or just a logging/monitoring object.

    Event sequence is approximately as follows:

        begin_txn
        ( ( begin_savepoint end_savepoint ) | revert ) *
        ( begin_commit vote_commit commit_txn ) | abort_txn 

    In other words, every transaction begins with begin_txn, and ends
    with either commit_txn or abort_txn.  A commit_txn will always be
    preceded by begin_commit and vote_commit.  An abort_txn may occur
    at *any* point following begin_txn, and aborts the transaction.
    begin/end_savepoint pairs and revert() messages may occur any time
    between begin_txn and begin_commit, as long as abort_txn hasn't
    happened.

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
    begin_txn() and vote_commit(), while a resource manager that
    manages direct storage will care about vote_commit() very deeply!

    Resource managers that use other participants for storage, but
    buffer writes to the other participant, will need to pay close
    attention to the begin_savepoint() and begin_commit() messages.
    Specifically, they must flush all pending writes to the
    participant that handles their storage, and enter a
    "write-through" mode, where any further writes are flushed
    immediately to the underlying participant.  This is to ensure that
    all writes are written to the "root participant" for those writes,
    by the time end_savepoint() or vote_commit() is issued.

    By following this algorithm, any number of participants may be
    chained together, such as a persistence manager that writes to an
    XML document, which is persisted in a database table, which is
    persisted in a disk file.  The persistence manager, the XML
    document, the database table, and the disk file would all be
    participants, but only the disk file would actually use
    vote_commit() and commit_txn() to handle a commit.  All of the
    other participants would flush pending updates and enter
    write-through mode at the begin_commit() message, guaranteeing that
    the disk file participant would know about all the updates by the
    time vote_comit() was issued, regardless of the order in which the
    participants received the messages."""
        

    def beginTransaction(txnService):
        """Transaction is beginning; nothing special to be done in
        most cases. A transactional cache might use this message to
        reset itself.  A database connection might issue BEGIN TRAN
        here."""
        

    def readyForSavepoint(txnService):
        """Savepoint is beginning; flush dirty objects and enter
        write-through mode, if applicable.  Note: this is not ZODB!
        You will not get savepoint messages before a regular commit,
        just because another savepoint has already occurred!"""
        

    def getSavepoint(txnService):
        """Savepoint is finished, it's safe to return to buffering
        writes; a database connection would probably issue a
        savepoint/checkpoint command here."""


    def readyToVote(txnService):
        """Transaction commit is beginning; flush dirty objects and
        enter write-through mode, if applicable.  DB connections will
        probably do nothing here.  Note: participants *must* continue
        to accept writes until vote_commit() occurs, and *must*
        accept repeated writes of the same objects!"""

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



class CannotRevertException(Exception):
    """A data manager does not support reverting to a savepoint"""

class NotReadyError(Exception):
    """One or more transaction participants were unready too many times"""

class TransactionInProgress(Exception):
    """Action not permitted while transaction is in progress"""

class OutsideTransaction(Exception):
    """Action not permitted while transaction is not in progress"""


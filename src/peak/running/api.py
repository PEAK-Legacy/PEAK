"""Runtime environment tools for logging, locking, process control, etc.

Please see the individual modules for useful classes, etc."""

from peak.naming.names import PropertyName

CLUSTER = PropertyName('peak.running.cluster').of(None)

del PropertyName

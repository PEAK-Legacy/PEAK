"""Object Naming subsystem, analagous to Java's JNDI (javax.naming)

    This package is intended to be a rough equivalent to the 'javax.naming'
    package for implementing JNDI in Java.  The idea is to be a conceptual
    match, rather than a 100% compatible API.  Pythonic naming conventions
    and operating idioms are preferred over their Java equivalents.


    Implementation Phases

        1. 'InitialContext' implementation, configurable with an environment,
           supporting URL lookups only.

        2. Full 'Context' interface and implementations, without the extended
           "directory" and "event" interface versions.


"""

from Interfaces import *
from API        import *

import SPI

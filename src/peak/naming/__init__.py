"""Object Naming subsystem, analagous to Java's JNDI (javax.naming)

    This package is intended to be a rough equivalent to the 'javax.naming'
    package for implementing JNDI in Java.  The idea is to be a conceptual
    match, rather than a 100% compatible API.  Pythonic naming conventions
    and PEAKish operating idioms are preferred over their Java equivalents.

    To Do (no particular ordering)

        * create FederationContext, set up to handle '+:' URL scheme, whose
          operations simply do a series of lookup/lookup_nns operations on the
          composite name path in order to implement all the "standard" operations

        * 'MappingContext', 'ConfigContext', 'FSContext', etc.

        * Unit tests!!!!

        * Directory attribute support, and other remaining interface methods

        * Detailed interface and subclassing docs
"""


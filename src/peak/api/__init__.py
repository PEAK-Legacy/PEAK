"""The TransWarp Software Automation API

 Component Construction and Specification (aka the "kernel API")

    The TransWarp kernel API provides primitives which can be used to implement
    any of the following approaches to automation-assisted development and
    code reuse:

     * Aspect-Oriented Programming (AOP) and Subject-Oriented Programming (SOP)
    
     * Generic and Generative Programming (GP)
    
     * Template Classes

     * Metaprogramming

    Most of these facilities are provided via the concepts of "module
    inheritance", "module advice", and "inheritance of metaclass constraints".
    Many generally useful base classes and metaclasses are also provided.
    
    **To Be Continued**

 The TW.API Package
    
    The API package exports all the relevant contents from its contained
    modules.  Normal usage is just 'from TW.API import *', but of course you
    can always do 'import TW.API' or 'from TW import API as foo', if you
    prefer.  All of the TW.API modules define '__all__' lists to limit their
    exports.  Please see individual modules for more detailed documentation and
    usage info.
"""

NOT_GIVEN = []
NOT_FOUND = []

from Modules import *
import SEF

__all__ = [item for item in dir() if not item.startswith('_')]; del item
__all__.append('__proceed__')

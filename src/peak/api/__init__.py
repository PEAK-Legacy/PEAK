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










# Convenience singletons

NOT_GIVEN = []
NOT_FOUND = []

__all__ = ['NOT_GIVEN', 'NOT_FOUND']


# Import module inheritance support first, because almost everything uses it

from Modules import *
from Modules import __all__ as ModulesAll

__all__.extend(ModulesAll)


# Core metaclasses and misc. API's come next; many things use them...

import Meta
__all__.append('Meta')

from Misc import *
from Misc import __all__ as MiscAll
__all__.extend(MiscAll)


# Last, but very far from least, Service-Element-Feature support.

from TW.Utils.Import import lazyImport

SEF = lazyImport('TW.SEF.Basic')
__all__.append('SEF')

del lazyImport

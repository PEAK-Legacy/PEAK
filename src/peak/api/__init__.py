"""The PEAK API

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

 The peak.api Package
    
    The API package exports all the relevant contents from its contained
    modules.  Normal usage is just 'from peak.api import *', but of course you
    can always do 'import peak.api' or 'from peak import api as foo', if you
    prefer.  All of the 'peak.api' modules define '__all__' lists to limit
    their exports.  Please see individual modules for more detailed
    documentation and usage info.
"""










# Convenience singletons

NOT_GIVEN = []
NOT_FOUND = []

__all__ = ['NOT_GIVEN', 'NOT_FOUND']


# Import module inheritance support first, because almost everything uses it

from modules import *
from modules import __all__ as ModulesAll
__all__.extend(ModulesAll)


# Misc. API's come next; many things use them...

from misc import *
from misc import __all__ as MiscAll
__all__.extend(MiscAll)


# And last, but not least, subpackage API proxies

from peak.binding.imports import lazyImport

binding = lazyImport('peak.binding.api')
naming = lazyImport('peak.naming.api')
model = lazyImport('peak.model.api')

__all__ += ['binding','naming','model']

del lazyImport

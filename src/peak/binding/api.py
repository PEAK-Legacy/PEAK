"""Component Binding Services

    The PEAK binding API provides primitives which can be used to implement
    any of the following approaches to automation-assisted development and
    code reuse:

     * Aspect-Oriented Programming (AOP) and Subject-Oriented Programming (SOP)
    
     * Generic and Generative Programming (GP)
    
     * Template Classes

     * Metaprogramming

    Most of these facilities are provided via the concepts of "module
    inheritance", "module advice", and "inheritance of metaclass constraints".
    (See 'peak.binding.modules' for details on these.)

"""

from meta import *
from once import *
from components import *
from modules import *

"""The TransWarp Software Automation API

 Component Construction and Specification (aka the "kernel API")

    The TransWarp kernel API provides primitives which can be used to implement
    any of the following approaches to automation-assisted development and
    code reuse:

     * Aspect-Oriented Programming (AOP) and Subject-Oriented Programming (SOP)
    
     * Generic and Generative Programming (GP)
    
     * Template Classes

     * Metaprogramming

    These primitives are based on a metaphor of software "components" which
    are built according to "specifications" which are combined in "recipes",
    and built by "build targets", as directed by "interpreters" and "advisors".
    
    
    Definitions

        component -- an object which can be created according to one or
            more specifications.  Components can be classes, instances,
            simple objects, or entire families of nested classes.
        
        specification -- a declaration or set of declarations describing how
            a component is to be constructed.  A component can be considered
            to be its own specification (e.g. "make a component exactly like
            this").  Any object can potentially be used as a specification,
            if supported by the builder object used to interpret it.

        recipe -- a sequence of specifications, to be applied in order when
            constructing a component.  Later specifications override earlier
            specifications.  Recipes can be added together, have specifications
            added to them, or be added to specifications to form new recipes.

        build target -- an object which co-ordinates specifications, advisors,
            and an interpreter, to create an output component.

        advisor -- an object which can alter the specifications of a component
            as it is being built, or alter the component itself as it is being
            finished.  The kernel provides a wide variety of generic advisors
            for your use, or you can create your own by subclassing them.  See
            'Interfaces.IBuildAdvisor' for the requirements, and the 'Advisors'
            module for implementation detail.

        interpreter -- an object which interprets zero or more specifications
            to create a component.  Different interpreters can interpret the
            same specifications in different ways, according to the nature of
            the interpreter.  The kernel includes two interpreters: one which
            interprets "simple" objects, and one to interpret more complex
            specifications by merging namespaces.  It is unusual to need to
            create a specialized interpreter, since these two ways of
            interpreting specifications address the vast majority of AOP and
            GP needs.

 The TW.API Package
    
    The API package exports all the relevant contents from these modules:
    
        TW.API.Interfaces -- All the interfaces used by the package are
            defined and documented here, and many helper functions, constants,
            etc.  Be sure to look at the interface details if you plan to
            implement your own build tools like advisors or interpreters.
            PyDoc doesn't display interfaces or their documentation, however,
            so be sure to look at the source directly.
        
        TW.API.Specifications -- Everything you need to specify complex
            components, such as 'Template', 'Bundle', and 'Recipe'.
        
        TW.API.Advisors -- Several useful advisor classes, such as 'Eval',
            'Postprocessor', 'Preprocessor', 'RegistryMaker', and so on.
        
        TW.API.Targets -- The 'build' function, and the 'BuildTarget' class

    Normal usage is just 'from TW.API import *', but of course you can always
    do 'import TW.API' or 'from TW import API as foo', if you prefer.  All of
    the TW.API modules define '__all__' lists to limit their exports.  Please
    see individual modules for more detailed documentation and usage info.

    For your information, however, here's an inheritance tree for the major
    classes and interfaces in the package, which covers almost everything
    that's exported here::

        IMetaInfo                       |
            ISpecification              |
                ICatalyst               |
                IBundle                 |
                IComponentInstance      | These are all found in  
            ISpecInterpreter            | TW.API.Interfaces
            IBuildAdvisor               |
                                        |
        ILazyIngredient                 |
        IBuildHandler                   |
            IBuildTarget                |

        BuildTarget (implements IBuildTarget)       | TW.API.Targets

        Instance (implements IComponentInstance)    |
                                                    |
        Ingredient                                  |
            Template (implements ISpecification)    | These can be found in
                Configure                           | TW.API.Specifications
                ClassRef                            |
                Catalyst (implements ICatalyst)     |
                    Bundle                          |
                                                    |
            Recipe (implements IMetaInfo)           |
                Import (implements ILazyIngredient) |

            AbstractInterpreter (implements ISpecInterpreter) | TW.API
                ComponentInterpreter                          | .Interpreters

            AbstractAdvisor (implements IBuildAdvisor)  |
                SubclassDefault                         |
                ComponentName                           |
                Eval                                    | TW.API.Advisors
                Postprocessor                           |
                Preprocessor                            |
                RegistryMaker                           |"""

NOT_GIVEN = []
NOT_FOUND = []

from Interfaces import *
from Specifications import *
from Advisors import *
from Targets import *
from SEF_hooks import *
from Modules import *    

"""The TransWarp Software Automation Framework

 The base package imports all the "kernel" objects and methods, so that you
 don't have to refer to things like 'TW.Interfaces.IBuilder' or
 'TW.Components.build'.  Instead, 'TW.build' or 'from TW import build' suffices.

 The current kernel modules are 'TW.Interfaces', 'TW.Components', 'TW.Builders',
 and 'TW.Specifications' - any public item available directly from them is
 available here.


 Component Construction and Specification (aka the "kernel")

    The TransWarp kernel provides primitives which can be used to implement
    any of the following approaches to automation-assisted development and
    code reuse:

     * Aspect-Oriented Programming (AOP) and Subject-Oriented Programming (SOP)
    
     * Generic and Generative Programming (GP)
    
     * Template Classes

     * Metaprogramming

    These primitives are based on a metaphor of software "components" which
    are built according to "specifications" combined in "recipes" and
    executed by "builders".
    
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

        builder -- an object which interprets one or more specifications to
            create a component.  Different builders can interpret the same
            specification in different ways, according to the nature of the
            builder.  For example, one could create a builder object which
            implemented specifications by printing them, instead of actually
            building a component!






























    The kernel's class and interface hierarchy::

        ISpecification
            ICatalyst
            IComponentInstance

        IBuilder
            IParentBuilder
            
        Instance (IComponentInstance)
        
        Ingredient
        
            Template (ISpecification)
                Catalyst (ICatalyst)
                    ClassRef

                Configure
                
            AbstractBuilder (IBuilder)
        
                ComponentBuilder (IParentBuilder)
                
                DefaultBuilder
                    OverwritingBuilder

                SimplePostProcessor
                    RegistryBuilder            

                Eval
            
            Recipe
"""








from TW.Interfaces import *
from TW.Specifications import *
from TW.Components import *
from TW.Builders import *

import SEF

NOT_GIVEN = []
NOT_FOUND = []


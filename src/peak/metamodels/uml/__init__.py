"""
UML Models
"""

from TW.API import Recipe, Import, SEF

UMLRecipe = Recipe(
    Import('TW.UML.Model:MetaModel'),
    Import('TW.UML.Model:UMLModel'),

    SEF,

    Import('TW.StructuralModel.Queries:ModelQuerying'),
    Import('TW.XMI.Reading:XMIReading'),   
)


# Only you can prevent namespace corruption...  only you.  :)

del Recipe, Import, SEF


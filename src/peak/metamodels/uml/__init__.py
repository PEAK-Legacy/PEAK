"""
UML Models
"""

from TW import Recipe, Import, SEF

UMLRecipe = Recipe(
    Import('TW.UML.Model:MetaModel'),
    Import('TW.UML.Model:UMLModel'),

    SEF.AcquisitionModel,

    Import('TW.StructuralModel.Queries:ModelQuerying'),
    Import('TW.XMI.Reading:XMIReading'),   
)


"""
UML Models
"""

from TW import Recipe, Import

UMLRecipe = Recipe(
    Import('TW.UML.Model:MetaModel'),
    Import('TW.UML.Model:UMLModel'),

    Import('TW.StructuralModel.Basic:StructuralFeatures'),
    Import('TW.StructuralModel.Basic:AcquisitionModel'),

    Import('TW.StructuralModel.Queries:ModelQuerying'),
    Import('TW.XMI.Reading:XMIReading'),   
)


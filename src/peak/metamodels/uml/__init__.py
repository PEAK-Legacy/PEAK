"""
UML Models
"""

from TW import Recipe, Import

UMLRecipe = Recipe(
    Import('TW.UML.Model:MetaModel'),
    Import('TW.UML.Model:UMLModel'),
    Import('TW.StructuralModel.Features:StructuralFeatures'),
    Import('TW.StructuralModel.InMemory:InMemory'),
    Import('TW.StructuralModel.Queries:ModelQuerying'),
    Import('TW.XMI.Reading:XMIReading'),   
)


"""Bulletin board example: domain model"""

from peak.api import *

__all__ = ['User', 'Bulletin', 'Category']


class User(model.Element):

    class loginId(model.Attribute):
        referencedType = model.String

    class fullName(model.Attribute):
        referencedType = model.String


class Bulletin(model.Element):

    class category(model.Attribute):
        referencedType = 'Category'
        referencedEnd = 'bulletins'

    class fullText(model.Attribute):
        referencedType = model.String

    class postedBy(model.Attribute):
        referencedType = User

    class editedBy(model.Attribute):
        referencedType = User


class Category(model.Element):

    class bulletins(model.Collection):
        referencedType = Bulletin
        referencedEnd = 'category'



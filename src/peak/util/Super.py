"""Workaround for 2.2 'super()' bug when working with classmethods"""

class Super(object):

    """super() replacement, adapted from the 2.2 "descrintro" example"""

    def __init__(self, type, obj=None):
        self.__type__ = type
        self.__obj__ = obj

    def __get__(self, obj, type=None):
        if self.__obj__ is None and obj is not None:
            return Super(self.__type__, obj)
        else:
            return self

    def __getattr__(self, attr):

        obj, typ = self.__obj__, self.__type__

        if isinstance(obj, typ):
            starttype = obj.__class__
        else:
            starttype = obj

        mro = iter(starttype.__mro__)

        for cls in mro:
            if cls is typ:
                break

        for cls in mro:
            if attr in cls.__dict__:
                x = cls.__dict__[attr]
                if hasattr(x, "__get__") and not hasattr(x,"__set__"):
                    x = x.__get__(obj, obj)
                return x

        raise AttributeError, attr


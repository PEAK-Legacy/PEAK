"""Support for creating instance methods"""

from new import instancemethod

class MethodWrapper(object):

    """MethodWrapper(function) -- create an instance-method descriptor"""

    def __init__(self, im_func):
        self.im_func = im_func
        
    def __get__(self, ob, typ=None):
        if typ is None: typ = ob.__class__
        return makeMethod(self.im_func, ob, typ)



























class makeMethod(object):

    """Replacement for new.instancemethod() that works w/new-style classes

        This is just a workaround until Python 2.2.1 lands in enough places
        that it can be required.
    """

    def __new__(klass, im_func, im_self, im_class):

        """Return an instancemethod if that works, or an instance of us if not"""

        try:
            return instancemethod(im_func, im_self, im_class)

        except TypeError:
            return super(makeMethod,klass).__new__(klass, im_func, im_self, im_class)


    def __init__(self, im_func, im_self, im_class):
        self.im_func, self.im_self, self.im_class = im_func, im_self, im_class


    def __call__(self, *__args, **__kwargs):

        im_self = self.im_self

        if im_self is None:
            return self.im_func(*__args, **__kwargs)
        else:
            return self.im_func(im_self, *__args, **__kwargs)


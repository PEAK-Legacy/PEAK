"""Simple predicate-driven query support oriented towards in-memory models

    This module wants to be a much more general and powerful query framework
    for Python objects, but it's mostly based on code that pre-dates the
    availability of a decent Interface package, let alone the kind of
    interface adaptation that's really needed to do it right.  Maybe as
    Zope 3X gets a little further along, I'll take a look at creating an
    enhanced version using interfaces and the adapter registry from the
    Zope Component Architecture.  (If I have app(s) that need that sort of
    thing, that is.)  Meanwhile, this is relatively unmaintained, except for
    what's needed to keep the unit tests running.
"""


from UserList import UserList
# import Query


class ComputedFeature(object):

    def __init__(self,func):
        self.func = func

    def __get__(self, obj, typ=None):
        if obj is not None:
            newSelf = self.__class__(self.func)
            newSelf.parent = obj
            return newSelf
        return self
        
    def values(self):
        return self.func(self.parent).data

    __call__ = values







class StructuralFeature:

    def Get(self,name,recurse=None):
        return NodeList(self.values()).Get(name,recurse)
        
    def Where(self,criteria=None):
        return NodeList(self.values()).Where(criteria)

class Classifier:

    def Get(self,name,recurse=None):
        return NodeList([self]).Get(name,recurse)
        
    def Where(self,criteria=None):
        return NodeList(filter(criteria,[self]))
        
    def ElementType(self):
        return NodeList([self._ElementType])
        
    ElementType = ComputedFeature(ElementType)


class App:

    def Get(self,name,recurse=None):
        return NodeList(self.values()).Get(name,recurse)
        
    def Where(self,criteria=None):
        return NodeList(self.values()).Where(criteria)












class NodeList(UserList):

    def __init__(self,data=None):
        if data is None: data=[]
        self.data=data

    def Get(self,name,recurse=None):

        if name[-1:]=='*':
            name=name[:-1]
            recurse = 1
           
        output=[]
        input=[self.data]
        empty = {}
        
        while input:
            data = input.pop()
            for item in data:
                values = getattr(item,name,empty).values()
                if values:
                    output.extend(list(values))
                    if recurse: input.append(values)
                    
        return self.__class__(output)

    def Where(self,criteria=None):
        return self.__class__(filter(criteria,self.data))













class Predicate(object):
    # we use explicit so that rebinding methods will work,
    # but we don't need normal acquisition

    def _compiledForm(self):
        return self

    def __init__(self,func):
        self.func = func
        
    def __getitem__(self,ob):
        return self.func(ob)
        
    def __call__(self,ob):
        compiled = self._compiledForm()
        if compiled is self:
            self.__call__ = self.__class__.__getitem__
        else:
            self.__call__ = self.__getitem__ = compiled
        return compiled[ob]
        
    def __and__(self,other):
        return And(self,other)

    def __or__(self,other):
        return Or(self,other)

    def __inv__(self):
        return Not(self)












class And(Predicate):

    def __init__(self,*args):
        self.predicates = args

    def __getitem__(self,ob):
        for pred in self.predicates:
            if not pred[ob]: return None
        return 1

    def __and__(self,other):
        return apply(And,self.predicates+(other,))

    #def _compiledForm(self):
    #    return apply(Query.And,tuple(map(lambda x:x._compiledForm(), self.predicates)))


class Or(Predicate):

    def __init__(self,*args):
        self.predicates = args

    def __getitem__(self,ob):
        for pred in self.predicates:
            if pred[ob]: return 1
        return None

    def __or__(self,other):
        return apply(Or,self.predicates+(other,))
        
    #def _compiledForm(self):
    #    return apply(Query.Or,tuple(map(lambda x:x._compiledForm(), self.predicates)))









class Not(Predicate):

    def __init__(self,arg):
        self.predicate = arg

    def __getitem__(self,ob):
        return not self.predicate[ob]
            
    def __inv__(self,other):
        return self.predicate


class Feature(Predicate):

    def __init__(self,name,predicate):
        self.name = name
        self.predicate = predicate

    def __getitem__(self,ob,_empty={}):
        return self.predicate[ob.Get(self.name)]


class ANY(Feature):
    def __getitem__(self,ob):
        predicate = self.predicate
        for value in ob.Get(self.name):
            if predicate[value]: return 1
        return None


class ALL(Feature):
    def __getitem__(self,ob):
        predicate = self.predicate
        for value in ob.Get(self.name):
            if not predicate[value]: return None
        return 1

class EXISTS(Predicate):
    def __init__(self,name): self.name=name
    def __getitem__(self,ob): return ob.Get(self.name)
        
class Value(Predicate):

    def __init__(self,value):
        self.value = value

    def __getitem__(self,ob):
        return ob==self.value


class Equals(Value):
    pass
    #def _compiledForm(self):
    #    return Query.Cmp(self.value)


class Type(Value):

    def __getitem__(self,ob):
        name = self.value
        classes = [(ob.__class__,)]
        
        while classes:
            for klass in classes.pop():
                if getattr(klass,'_ElementType','') == name: return 1
                if name in getattr(klass,'_XMINames',()):    return 1
                classes.append(klass.__bases__)
                
class Is(Value):

    def __getitem__(self,ob):
        return ob is self.value
        

class IsNot(Value):

    def __getitem__(self,ob):
        return ob is not self.value




class NotEqual(Value):

    def __getitem__(self,ob):
        return ob != self.value


class LessThan(Value):

    def __getitem__(self,ob):
        return ob < self.value


class GreaterThan(Value):

    def __getitem__(self,ob):
        return ob > self.value


class Between(Predicate):

    def __init__(self,lo,hi):
        self.lo = lo
        self.hi = hi        

    def __getitem__(self,ob):
        return self.lo <= ob <= self.hi

    #def _compiledForm(self):
    #    return Query.Range(self.lo,self.hi)

from peak.running.config.modules import setupModule
setupModule()

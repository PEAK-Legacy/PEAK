from weakref import WeakValueDictionary
from types import ClassType

__all__ = []

metaReg = WeakValueDictionary()

def derivedMeta(metaclasses):
    derived = metaReg.get(metaclasses)

    if derived is None:

        normalized = normalizeBases(metaclasses)
        derived = metaReg.get(normalized)
        
        if derived is None:
        
            if len(normalized)==1:
                derived = normalized[0]
            else:
                derived = metaFromBases(normalized)(
                    '_'.join([n.__name__ for n in normalized]),
                    metaclasses, {}
                )
            try: metaReg[normalized] = derived
            except TypeError: pass

        try: metaReg[metaclasses] = derived
        except TypeError: pass
            
    return derived

def normalizeBases(allBases):
    bases = []
    for b in allBases:
        if b is ClassType or b is makeClass: continue
        bases = [bc for bc in bases if not issubclass(b,bc)]
        bases.append(b)
    return tuple(bases)


def metaFromBases(bases):
    meta = tuple([getattr(b,'__class__',type(b)) for b in bases])
    if meta==bases: raise TypeError("Incompatible root metatypes",bases)
    return derivedMeta(meta)


def makeClass(name,bases,dict):

    # Create either a plain Python class or an ExtensionClass,
    # based on the nature of the base classes involved

    name = str(name)  # De-unicode

    metaclasses = [getattr(b,'__class__',type(b)) for b in bases]

    if dict.has_key('__metaclass__'):
        metaclasses.insert(0,dict['__metaclass__'])
        del dict['__metaclass__']

    if dict.has_key('__metaclasses__'):
        metaclasses[0:0] = list(dict['__metaclasses__'])
        del dict['__metaclasses__']

    metaclasses = normalizeBases(metaclasses)
    
    if metaclasses:
        metaclass = derivedMeta(metaclasses)
        return metaclass(name,bases,dict)

    from new import classobj; return classobj(name,bases,dict)













if __name__=='__main__':

    class MMM2(type):
        pass

    class MM1(type):
        pass

    class MM2(type):
        __metaclass__ = MMM2

    class M1(type):
        __metaclass__ = MM1

    class M2(type):
        __metaclass__ = MM2

    class C1:
        __metaclass__ = M1

    class C2:
        __metaclass__ = M2

    class C3(C1,C2):
        __metaclass__ = makeClass

    from ExtensionClass import Base

    class X:
        __metaclass__ = makeClass
        
    class Foo(Base):
        __metaclass__ = makeClass

    class Y(X,Foo):
        __metaclass__ = makeClass

    #The below would fail with a TypeError - can't combine ExtCls and 'type'
    #class Z(Y,C3):
    #    __metaclass__ = makeClass


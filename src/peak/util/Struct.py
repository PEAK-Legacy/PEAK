"""It's a tuple...  it's a dictionary...  it's super struct!"""

from types import StringTypes


class structType(type):

    """Sets up __fieldmap__ and field properties"""

    def __new__(klass, name, bases, cdict):

        cdict = cdict.copy()
        cdict['__slots__']=[]

        fields = cdict.get('__fields__', ())
        fzip = zip(fields, range(len(fields)))

        baseMap = {}

        for b in bases:
            # this isn't true __mro__ order, but we shouldn't need it...
            baseMap = getattr(b,'__fieldmap__',baseMap)
            if baseMap: break      
        
        if fields:
            cdict['__fieldmap__'] = fieldMap = dict(fzip)

        elif baseMap:
            # If __fields__ isn't specified, we want to inherit the map
            fieldMap = baseMap











        for fieldName, fieldNum in fzip:

            if fieldName in cdict or baseMap.get(fieldName)==fieldNum:
                # don't override any explicitly supplied properties
                # or inherited ones based on the same field number
                continue
                
            def get(self,fieldNum=fieldNum):
                try:
                    return tuple.__getitem__(self,fieldNum)
                except IndexError:
                    pass

            cdict[fieldName] = property(get)

        return super(structType,klass).__new__(klass, name, bases, cdict)

























class struct(tuple):

    """Record-like data structure

    Usage::

        class myRecord(struct):
            __fields__ = 'first', 'second', 'third'

        # the following will now all produce identical objects
        # and they'll all compare equal to the tuple (1,2,3):
        
        r = myRecord([1,2,3])
        r = myRecord(first=1, second=2, third=3)
        r = myRecord({'first':1, 'second':2, 'third':3})
        r = myRecord.fromMapping({'first':1, 'second':2, 'third':3})
        r = myRecord.extractFromMapping(
            {'first':1, 'second':2, 'third':3, 'blue':'lagoon'}
        )

        # the following will all print the same thing for any 'r' above:
        
        print r
        print (r.first, r.second, r.third)
        print (r[0], r[1], r[2])
        print (r['first'], r['second'], r['third'])

    If you want to define your own properties in place of the automagically
    generated ones, just include them in your class.  Your defined properties
    will be inherited by subclasses, as long as the field of that name is at
    the same position in the record.  If a subclass changes the field order,
    the inherited property will be overridden by a generated one, unless the
    subclass supplies a replacement as part of the class dictionary.

    Note: if you define custom properties, they only determine the attributes
    of the instance.  All other behaviors including string representation,
    iteration, item retrieval, etc., will be unaffected.  It's probably best
    to define a 'fromMisc' classmethod to manage the initial construction
    of the fields instead.
    """

    __metaclass__ = structType


    def __new__(klass, *__args, **__kw):

        if __args:
            arg = __args[0]
            if isinstance(arg,StringTypes):
                return klass.fromString(*__args, **__kw)
            elif isinstance(arg,dict):
                return klass.fromMapping(*__args, **__kw)

        elif __kw:
            return klass.fromMapping(__kw)
                    
        return klass.defaultCreate(*__args, **__kw)


    def defaultCreate(klass, *args, **kw):
        """You can define a classmethod here, to be used in place of
            'tuple.__new__' when the struct is being created from something
            other than a dict, keywords, or a string.  This is also a good
            place to do any calculations or manipulations on the field values
            before they're cast in stone.
        """
        # this is just a dummy so HappyDoc will document the method,
        # we'll replace it with tuple.__new__ below for performance

    defaultCreate = classmethod(tuple.__new__, __doc__= defaultCreate.__doc__)


    def fromString(klass, arg):
        """Override this classmethod to enable parsing from a string"""
        raise NotImplementedError

    fromString = classmethod(fromString)





    def fromMapping(klass, arg):
    
        """Create a struct from a mapping
        
            This method checks that the mapping doesn't contain any field names
            the struct won't accept.  This prevents silent unintentional loss
            of information during conversions.  If you want extra data in the
            mapping to be ignored, you should use 'extractFromMapping' instead.

            Note that although this method will raise 'ValueError' for fields
            that would be dropped, it uses a default value of 'None' for any
            fields which are missing from the mapping.  If you want a stricter
            policy, you'll need to override this.
        """

        fm = klass.__fieldmap__; nfm = fm.copy(); nfm.update(arg)

        if len(nfm)>len(fm):
            raise ValueError(
                ("Mapping contains keys which are not fields of %s"
                 % klass.__name__), arg
            )

        return tuple.__new__(klass, map(arg.get, klass.__fields__))


    fromMapping = classmethod(fromMapping)


    def extractFromMapping(klass, arg):
        """Fast extraction from a mapping; ignores undefined fields"""    
        return tuple.__new__(klass, map(arg.get, klass.__fields__))

    extractFromMapping = classmethod(extractFromMapping)







    def __getitem__(self, key):

        if isinstance(key,StringTypes):
            
            # will raise KeyError for us if it's not found
            i = self.__fieldmap__[key]

            if i>=len(self):
                raise KeyError,key
            else:
                key = i

        # this will raise IndexError instead of KeyError, which we want
        # if it was a number...
        return tuple.__getitem__(self,key)


    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError,IndexError):
            return default

    def copy(self):         return dict(self.items())
    def keys(self):         return list(self.__fields__[:len(self)])
    def iterkeys(self):     return iter(self.__fields__[:len(self)])
    def items(self):        return zip(self.__fields__,self)
    def iteritems(self):    return iter(self.items())
    def values(self):       return list(self)
    def itervalues(self):   return iter(self)
    
    __safe_for_unpickling__ = True

    def __reduce__(self):   return self.__class__, (tuple(self),)

    def __contains__(self, key):
        myLen = len(self)
        return self.__fieldmap__.get(key,myLen) < myLen
    
    has_key = __contains__

def makeStructType(name, fields, baseType=struct, **kw):
    bases = bases or (struct,)
    kw['__fields__'] = fields
    return structType(name or 'anonymous_struct', (baseType,), kw)




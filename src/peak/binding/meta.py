"""Frequently Useful Metaclasses (And Friends)"""

__all__ = [
    'ClassInit', 'AssertInterfaces', 'ActiveDescriptors', 'ActiveDescriptor',
    'Singleton',
]

from kjbuckets import *
from types import FunctionType

class ActiveDescriptors(type):

    """Type which gives its descriptors a chance to find out their names,
       and supports tracking volatile attributes for __getstate__ filtering"""
    
    def __init__(klass, name, bases, dict):

        va = kjSet()
        e  = kjSet()

        for k in klass.__mro__:
            va += getattr(k,'__volatile_attrs__',e)
            
        klass.__volatile_attrs__ = va

        for k,v in dict.items():
            if isinstance(v,ActiveDescriptor):
                v.activate(klass,k)

        super(ActiveDescriptors,klass).__init__(name,bases,dict)


class ActiveDescriptor(object):
    """This is just a (simpler sort of) interface assertion class""" 

    def activate(self,klass,attrName):
        """Informs the descriptor that it is in 'klass' with name 'attrName'"""
        raise NotImplementedError



class ClassInit(type):

    """Lets classes have a '__class_init__(thisClass,newClass,next)' method"""
    
    class _sentinel:
        def __class_init__(thisClass, newClass, next):
            pass

    sentinel = _sentinel()
    

    def __new__(meta, name, bases, dict):
        
        try:
            ci = dict['__class_init__']
        except KeyError:
            pass
        else:
            # Guido take note: a legitimate use for 'classmethod'!
            dict['__class_init__'] = classmethod(ci)

        return super(ClassInit, meta).__new__(meta,name,bases,dict)


    def __init__(newClass, name, bases, dict):

        super(ClassInit, newClass).__init__(name,bases,dict)

        initSupers = iter(
            [base for base in newClass.__mro__
                   if base.__dict__.has_key('__class_init__')
             ]+[ClassInit.sentinel]
        )

        next = initSupers.next
        next().__class_init__(newClass, next)





class AssertInterfaces(type):

    """Work around Zope Interface package's new-style class/metaclass bug
    
        Use this as a metaclass of any new-style class you'd like to have
        properly support '__implements__' and '__class_implements__', as
        current versions of the Zope 'Interface' package can't tell that
        a metaclass instance is really a class-like thing.

        Basically, this does two tricks.  First, it converts any
        '__implements__' value in the class dictionary to an
        'interfaceAssertion' attribute descriptor.  Second, it provides
        'instancesImplements' and 'instancesImplement' methods to its
        instances, so that when looking for 'isImplementedByInstancesOf',
        the 'Interface' package will get the right thing.  There are two
        spellings of the method because the Zope 2.x and Zope 3X versions
        of the package spell it differently.  :(
    """
    
    def __init__(klass, name, bases, dict):
    
        """Convert '__implements__' to a descriptor"""
        
        if dict.has_key('__implements__'):
            imp = dict['__implements__']
            if not isinstance(imp, klass.interfaceAssertion):
                klass.__implements__ = klass.interfaceAssertion(imp)

        super(AssertInterfaces, klass).__init__(name, bases, dict)
        











    def instancesImplements(klass):

        """Tell 'Interface' what our (non-metaclass) instances implement"""

        ia = klass.interfaceAssertion

        for k in klass.__mro__:

            i = k.__dict__.get('__implements__')

            if i is None:
                continue

            elif isinstance(i,ia):
                return i.implements

            else:
                return i

    instancesImplement = instancesImplements


    class interfaceAssertion(object):
    
        """Smart descriptor that returns the right '__implements__'"""
        
        def __init__(self, implements, *extra):
            self.implements = (implements,) + extra

        def __get__(self, ob, typ=None):
        
            """Return '__class_implements__' if retrieved from the class,
                or '__implements__' if retrieved from the instance."""
                
            if ob is None:
                from Interface.Standard import Class
                return getattr(typ,'__class_implements__',Class)

            return self.implements


class MethodExporter(ActiveDescriptor, type):

    """Support for generating "verbSubject()" methods from template functions

        MethodExporter is a metaclass whose instances are singletons that
        install "verbSubject()"-style methods in classes which contain them.
        The verbs are implemented as method templates in the class statement
        which defines the MethodExporter, and the subject name comes from
        the name of the class being defined.

        Usage example::

            class slappableFeature(object):

                __metaclass__ = MethodExporter

                message = "Ow, that hurts!"
                
                def slap(self, extra):
                    feature = self.__class__.__feature__
                    print "%s: %s (%s)" % (self.name, feature.message, extra)

                slap.namingConvention = "slap%(initCap)s"


            class Person(object):

                def __init__(self,name):
                    self.name = name

                class face(slappableFeature):
                    message = "Watch out for my glasses!"

                class back(slappableFeature):
                    pass

            joe = Person('Joe')
            
            # Prints: "Joe: Watch out for my glasses! (Thanks, I needed that!)"
            joe.slapFace("Thanks, I needed that!")

            # Prints: "Joe: Ow, that hurts!  (Am I great or what?)"
            joe.slapBack("Am I great or what?")

        While a bit silly, this demonstrates how the method template 'slap()'
        is used to generate 'slapFace()' and 'slapBack()' methods, using
        a 'namingConvention' function attribute, and the special name
        '__feature__'.

        Typically, you will define MethodExporters with multiple verbs, and
        you may also use template variants, which are chosen by metadata in
        subclasses.  For example, suppose we wanted 'slappableFeatures' to
        implement slap differently depending on skin thickness::
      
            class slappableFeature(object):

                __metaclass__ = MethodExporter

                thickness = 5
                
                def slap_thick(self):
                    feature = self.__class__.__feature__
                    print "THUD!", feature.thickness

                slap_thick.namingConvention = "slap%(initCap)s"

                slap_thick.installIf = \
                    lambda feature,func: feature.thickness > 10

                slap_thick.verb = "slap"

                def slap_thick(self):
                    feature = self.__class__.__feature__
                    print "SMACK!", feature.thickness

                slap_thin.namingConvention = "slap%(initCap)s"

                slap_thin.installIf = \
                    lambda feature,func: feature.thickness <= 10

                slap_thin.verb = "slap"

            class Person(object):

                class face(slappableFeature):
                    thickness = 5

                class back(slappableFeature):
                    thickness = 15

            joe = Person()

            # two ways to print "SMACK! 5"
            joe.slapFace()
            Person.face.slap(joe)

            # two ways to print "THUD! 15"
            joe.slapBack()
            Person.back.slap(joe)

        As you can see from this example, 'face' and 'back' actually do exist
        as real attributes of the 'Person' class.  They are instances of
        MethodExporter, class-like objects created by their respective class
        statements.  MethodExporter instances are singleton-like: any functions
        defined in a MethodExporter which are not templates (i.e., do not
        have a 'namingConvention') will become methods of the MethodExporter
        itself, rather than methods of the containing object.  To distinguish
        such methods, and to keep clear the distinction between the feature
        and its container, we suggest using 'feature' as the first parameter
        of such methods.  For example, we could rewrite the slap verb as::

            def yelp(feature):
                # This will be a method of the feature, because it has no
                # 'namingConvention'.
                print 'Y%sow!  My %s hurts!" % (
                    'e'*(20-feature.thickness), feature.__name__
                )

            def slap(self):
                feature = self.__class__.__feature__
                feature.yelp()
                
            slap.namingConvention = "slap%(initCap)s"

        This will print "Yeeeeeeeeeeeeeeeow!  My face hurts!" or
        "Yeeeeeow!  My back hurts!", as is appropriate for the specific
        feature.  We could also simply call 'Person.back.yelp()' or
        'Person.face.yelp()' to obtain the same results.

        By now, the sharp-eyed reader will be wondering about the bits of
        magic code that keep showing up, such as 'self.__class__.__feature__'
        and 'slap.namingConvention = "slap%(initCap)s"'.  Not to mention
        our earlier usage of the 'installIf' and 'verb' attributes.  So let's
        move on to the reference sections...

        namingConvention

            The 'namingConvention' function attribute designates the function
            as a method template.  It is a format string that describes the
            method name that it is a template for.  It is applied to a
            dictionary supplied by MethodExporter's 'subjectNames()' method;
            see that method for details.  'initCap' is the most commonly used
            name in that dictionary: it supplies the MethodExporter instance's
            name, with the first character capitalized.

        installIf

            The 'installIf' function attribute, if supplied, is a callable that
            takes two arguments: the feature (i.e. the MethodExporter instance
            which is being created), and the function.  If the callable returns
            a true value, the function will be used as the template for the
            method its 'namingConvention' designates.  If not, the function will
            not be used.

        verb

            The normal use of 'installIf' is to select variant implementations
            of the same verb, based on metadata supplied in a subclass.  However,
            since the variants must have different function names, the 'verb'
            function attribute is used to indicate the name which will be used
            in the finished MethodExporter.  Thus, in our "thick and thin" slap
            example, using 'slap_thick.verb="slap"' and 'slap_thin.verb="slap"'
            caused either 'slap_thick' or 'slap_thin' to be installed as the
            'slap' method of the MethodExporter.  If you do not supply a
            'verb' function attribute, the function's name within the class
            is used.  Note that this does not have to be the function name;
            for example, the below defines a 'baz' verb, not 'foo'::

                def foo(self): pass

                class bar(object):
                    __metaclass__ = MethodExporter
                    baz = foo

        __feature__

            You've probably noticed that our method templates refer to
            'self.__class__.__feature__' in order to access the feature
            object itself.  And you may be wondering, "How does __feature__
            know whether to be 'face' or 'back'?"  The answer is in the
            magic of code rebinding.

            Functions used as method templates are *templates* for the
            methods.  They are not used directly.  Instead, the code is
            copied and the 'func_code.co_names' attribute is rewritten
            so that '__feature__' is replaced with the actual feature
            name.  Thus, 'face' ends up with a different 'slap()' method
            than 'back()', and their code effectively says
            'self.__class__.face' or 'self.__class__.back', respectively.
            However, because the code objects came from the same lines of
            code, any errors will refer to the original file and line
            numbers of that code.

        Inner and Outer Method Definitions

            Sometimes, one needs to modify an "off-the-shelf" method
            exported by a MethodExporter.  For this reason, MethodExporters
            do not overwrite methods which are already defined in their
            containing class.  For example, if we defined Person as follows::

                class Person(object):

                    class face(slappableFeature):
                        thickness = 5

                    class back(slappableFeature):
                        thickness = 15

                    def slapBack(self):
                        self.__class__.back.slap()
                        print "Do you really have to do that?"

                    def slapFace(self):
                        print "Don't even think about it!"

            Then 'aPerson.slapFace()' would print "Don't even think about it",
            while 'aPerson.slapBack()' would carry out the generated behavior,
            and then ask, "Do you really have to do that?".  Subclasses of
            Person will retain these modified behaviors, even if 'back' is
            redefined in the subclass.  (In which case, the redefined behavior
            will be followed by the "Do you really have to do that?" question.)

        Why 'self.__class__.__feature__'?

            Sharp-eyed Pythonistas may wonder why we don't just say
            'self.__feature__' and be done with it.  The reason is that
            features can also be properties, so 'self.__feature__' might
            actually be the instance value of the property defined by
            the feature.  'self.__class__.__feature__' will always be
            the class' definition of the feature, which is what we want.

            The SEF framework adds '__get__', '__set__', and '__delete__'
            methods to a subclass of MethodExporter, which lets you create
            features that are properties; look at the TW.SEF.Basic.FeatureMC
            class for more details.

        Implementation Notes
        
            It's amazing that it takes so much documentation to describe so
            little code.  The combined docstrings for this metaclass are over
            *three times the size of the actual code*.  So if you've already
            read this far, you might as well read the source if you have a need
            to understand the actual implementation.  :)
    """


    def getMethod(self, ob, verb):

        """Look up a method dynamically
        
        Sometimes, one wishes to access a possibly-overridden method of a
        feature, knowing the verb and subject, but not the method name.
        That is, one knows about 'slap', and 'face', but not 'slapFace'.
        In that case, 'face.getMethod(object,"slap") can be used to obtain
        the 'object.slapFace' method, without needing to know the naming
        convetions used by the object.

        Note that this is different than simply accessing 'face.slap',
        because the containing class might have defined its own
        'slapFace()' method.  That method would refer to 'face.slap'
        in order to call the original, un-overridden method generated
        by the 'face' feature."""

        return getattr(ob,self.methodNames[verb])


    def activate(self,klass,attrName):

        """Install the feature's "verbSubject()" methods upon use in a class"""

        if attrName != self.__name__:
            raise TypeError(
                "Feature %s installed in %s as %s; must be named %s" %
                (self.__name__,klass,attrName,self.__name__)
            )

        for verb,methodName in self.methodNames.items():
            old = getattr(klass, methodName, None)
            if old is None or hasattr(
                getattr(old,'im_func',None),'namingConvention'
            ):
                setattr(klass, methodName, getattr(self,verb))





    def __init__(self, className, bases, classDict):

        """Set up method templates, name mapping, etc."""

        super(MethodExporter,self).__init__(className, bases, classDict)

        from TW.Utils.Code import Function
        items = []; d={}

        for b in bases:
            items.extend(getattr(b,'methodTemplates',d).items())

        items.reverse()
        mt = self.methodTemplates = dict(items)

        for methodName, method in classDict.items():
            if not isinstance(method,FunctionType): continue

            nc = getattr(method,'namingConvention',None)
            if nc:
                mt[methodName]=method
                setattr(self,methodName,staticmethod(method))
            else:
                setattr(self,methodName,classmethod(method))

        names = self.subjectNames()

        mn = self.methodNames = {}

        for methodName,func in mt.items():
            verb       = getattr(func,'verb',methodName)
            installIf  = getattr(func,'installIf',None)

            if installIf is None or installIf(self,func):
                mn[verb] = func.namingConvention % names
                f=Function(func)
                f.co_names[f.co_names.index('__feature__')] = className
                setattr(self,verb,staticmethod(f.func()))



    def subjectNames(self):

        """Return a dictionary usable for formatting by 'namingConvention'"""

        names = self.__dict__.copy()
        className = self.__name__

        names.update(
            {
                'name':    className,
                'upper':   className.upper(),
                'lower':   className.lower(),
                'capital': className.capitalize(),
                'initCap': className[:1].upper()+className[1:]
            }
        )
        return names
























class Singleton(type):

    """Class whose methods are all class methods"""

    def __new__(metaclass, name, bases, dict):

        d = dict.copy()

        for k,v in dict.items():
            if isinstance(v,FunctionType):
                d[k]=classmethod(v)

        return super(Singleton,metaclass).__new__(metaclass,name,bases,d)

    def __call__(klass, *args, **kw):
        raise TypeError("Singletons cannot be instantiated")

from peak.api import *
from dispatch import functions, combiners
from protocols.advice import addClassAdvisor, add_assignment_advisor

class _OptionCombiner(combiners.MapCombiner):

    """Method combiner for options"""

    def getItems(self,signature,method):
        return method       # The methods are key-val pairs already

    def shouldStop(self,signature,method):
        return not method   # () means stop, as per 'reject_inheritance' below

OptionRegistry = functions.Dispatcher(['ob'], _OptionCombiner)



def reject_inheritance(*names):
    """Reject inheritance of the named options, or all options if none named"""
    def callback(klass):
        # if no names are spec'd, 'method' will equal '()',
        #    which is the sentinel for "don't inherit anything"
        method = tuple([(name,(None, None)) for name in names])
        OptionRegistry[(klass,)] = method
        return klass
    addClassAdvisor(callback)


def option_names(ob):
    """List of option names that are applicable for 'ob'"""
    data = OptionRegistry[ob,]
    names = [k for k in data if data[k]<>(None,None)]
    names.sort()
    return names






class AbstractOption:
    """Base class for option metadata objects"""

    sortKey = None
    help = value = type = metavar = repeatable = option_names = NOT_GIVEN

    def __init__(self,*option_names,**kw):
        kw['option_names'] = option_names
        binding.initAttrs(self,kw.iteritems())
        if not option_names:
            raise TypeError(
                "%s must have at least one option name"
                % self.__class__.__name__
            )
        for option in option_names:
            if not option.startswith('-') or option.startswith('---'):
                raise ValueError(
                    "Invalid option name %r:"
                    " option names must begin with '-' or '--'" % (option,)
                )
        if (self.type is NOT_GIVEN) == (self.value is NOT_GIVEN):
            raise TypeError(
                "%s options must have a value or a type, not both or neither"
                % self.__class__.__name__
            )

        if self.type is NOT_GIVEN and self.metavar is not NOT_GIVEN:
            raise TypeError(
                "'metavar' is meaningless for options without a type"
            )
        if self.metavar is NOT_GIVEN and self.type is not NOT_GIVEN:
            self.metavar = self.type.__name__.upper()









class Set(AbstractOption):
    """Set the attribute to the argument value or a constant"""
    repeatable = False

class Add(AbstractOption):
    """Add the argument value or a constant to the attribute"""
    repeatable = True

class Append(AbstractOption):
    """Append the argument value or a constant to the attribute"""
    repeatable = True

class Handler(AbstractOption):
    """Invoke a handler method when the option appears on the command line"""
    pass

def option_handler(*option_names, **kw):
    """Decorate a method to be called when option is encountered"""

    option = Handler(*option_names,**kw)

    def class_callback(klass):
        binding.declareAttribute(klass,None,option)
        return klass

    def decorator(frame,name,func,old_locals):
        # option.function = func
        addClassAdvisor(class_callback,frame=frame)
        return func

    return add_assignment_advisor(decorator)

[binding.declareAttribute.when(AbstractOption)]
def declare_option(classobj,attrname,option):
    OptionRegistry[(classobj,)] = tuple(
        [(optname,(attrname,option)) for optname in option.option_names]
    )





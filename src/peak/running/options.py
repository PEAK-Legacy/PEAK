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














class AbstractOption:
    """Base class for option metadata objects"""

    repeatable = True
    sortKey = metavar = help = None
    value = type = option_names = NOT_GIVEN

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

        if self.type is NOT_GIVEN and self.metavar is not None:
            raise TypeError(
                "'metavar' is meaningless for options without a type"
            )
        if self.type is not NOT_GIVEN:
            self.nargs = 1
            if self.metavar is None:
                self.metavar = self.type.__name__.upper()
        else:
            self.nargs = 0




    def makeOption(self, attrname,optmap=None):
        options = self.option_names

        if optmap is not None:
            options = [opt for opt in options if optmap.get(opt) is self]

        from peak.util.optparse import make_option
        return make_option(
            action="callback", nargs=self.nargs, callback_args=(attrname,),
            callback = self.callback, metavar=self.metavar, help=self.help,
            type=(self.type is not NOT_GIVEN and "string" or None),*options
        )

    def convert(self,value):
        if self.value is NOT_GIVEN:
            return self.type(value)
        else:
            return self.value























class Set(AbstractOption):
    """Set the attribute to the argument value or a constant"""

    repeatable = False

    def callback(self, option, opt, value, parser, attrname):
        setattr(parser.values, attrname, self.convert(value))


class Add(AbstractOption):
    """Add the argument value or a constant to the attribute"""

    def callback(self, option, opt, value, parser, attrname):
        value = getattr(parser.values, attrname) + self.convert(value)
        setattr(parser.values, attrname, value)


class Append(AbstractOption):
    """Append the argument value or a constant to the attribute"""

    def callback(self, option, opt, value, parser, attrname):
        getattr(parser.values, attrname, value).append(self.convert(value))


class Handler(AbstractOption):
    """Invoke a handler method when the option appears on the command line"""

    def callback(self, option, opt, value, parser, attrname):
        self.function(
            parser.values, parser, opt, self.convert(value), parser.rargs
        )










def parse(ob,args):
    parser = make_parser(ob)
    opts, args = parser.parse_args(args, ob)
    return args


def exit_parser(status=0, msg=None):   
    if msg:
        from commands import InvocationError
        raise InvocationError(msg.strip())
    if status:
        raise SystemExit(status)


def make_parser(ob):
    """Make an 'optparse.OptionParser' for 'ob'"""

    from peak.util.optparse import OptionParser
    parser = OptionParser("", add_help_option=False)
    parser.exit = exit_parser

    optinfo = OptionRegistry[ob,].items()
    optmap = dict([(k,opt)for k,(a,opt) in optinfo if opt is not None])
    optsused = {}
    for optname,(attrname,option) in optinfo:
        if option in optsused or option is None:
            continue
        parser.add_option( option.makeOption(attrname,optmap) )
        optsused[option] = True

    return parser

def get_help(ob):
    return make_parser(ob).format_help().strip()








def option_handler(*option_names, **kw):
    """Decorate a method to be called when option is encountered"""

    option = Handler(*option_names,**kw)

    def class_callback(klass):
        binding.declareAttribute(klass,None,option)
        return klass

    def decorator(frame,name,func,old_locals):
        option.function = func
        addClassAdvisor(class_callback,frame=frame)
        return func

    return add_assignment_advisor(decorator)


[binding.declareAttribute.when(AbstractOption)]
def declare_option(classobj,attrname,option):
    OptionRegistry[(classobj,)] = tuple(
        [(optname,(attrname,option)) for optname in option.option_names]
    )




















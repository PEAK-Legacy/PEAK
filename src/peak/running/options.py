from peak.cli.options import *
from peak.api import binding

__all__ = [
    'parse', 'make_parser', 'get_help', 'Group',
    'Set', 'Add', 'Append', 'Handler', 'reject_inheritance', 'option_handler',
    'AbstractOption', 'OptionsRegistry',
]

[binding.declareAttribute.when(AbstractOption)]
def _declare_option(classobj,attrname,option):
    option.register(OptionsRegistry(classobj), attrname)



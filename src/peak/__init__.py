"""The TransWarp Software Automation Framework

The base package imports all the "kernel" objects and methods, so that you
don't have to refer to things like 'TW.Interfaces.IBuilder' or
'TW.Components.build'.  Instead, 'TW.build' or 'from TW import build' suffices.

The current kernel modules are 'TW.Interfaces', 'TW.Components', and
'TW.Builders' - any public item available directly from them is available here.
"""


# Version-independent support for '__all__' in modules

import sys

if sys.version<'2.1':

    def importAllFrom(name,g=None):

        g = g or globals()
        exec "import %s; __all__=getattr(%s,'__all__',['*'])" % (name,name)

        import string
        exec "from %s import %s" % (name,string.join(__all__,",")) in g

else:
    def importAllFrom(name,g=None):
        g = g or globals()
        exec "from %s import *" % name in g


importAllFrom('TW.Interfaces')
importAllFrom('TW.Components')
importAllFrom('TW.Builders')
import SEF

NOT_GIVEN = []
NOT_FOUND = []

del sys

from peak.api import *
from types import ModuleType

class DemoCGI(binding.Component):

    protocols.advise(
        instancesProvide = [running.IRerunnableCGI]
    )

    runCount = 0

    def runCGI(self, input, output, errors, env, argv=()):

        self.runCount += 1

        print >>output, 'Content-Type: text/plain'
        print >>output

        print >>output, "I've been run %d times." % self.runCount
        print >>output
        print >>output, "Environment"
        print >>output, "-----------"

        for k,v in env.items():
            print >>output, '%-20s = %r' % (k,v)

        print >>output

        import sys
        names = dict(
            [(mod.__name__,None)
                for mod in sys.modules.values() if type(mod) is ModuleType
            ]
        ).keys()

        names.sort()

        print >>output, "Modules Loaded (%d total)" % len(names)
        print >>output, "--------------------------"

        for n in names:
            print >>output, n

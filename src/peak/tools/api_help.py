"""Implements the 'peak help' command"""

from peak.api import *
from peak.running.commands import AbstractCommand, InvocationError

class APIHelp(AbstractCommand):

    usage = "Usage: peak help expression [expr2 expr3...]"

    def _run(self):
        if len(self.argv)>1:
            for arg in self.argv[1:]:
                help(eval(arg))
        else:
            raise InvocationError("No expression specified")


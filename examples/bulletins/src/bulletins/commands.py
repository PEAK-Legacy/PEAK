from peak.api import *

from peak.running.commands import AbstractCommand, Bootstrap


class BulletinsCmd(Bootstrap):

    usage = """
Usage: bulletins command arguments...


Available commands:

  createdb -- create an empty bulletins database
  purge    -- purge expired bulletins
"""


class CreateDB(AbstractCommand):

    def run(self):
        print "This would've created the DB"



class PurgeDB(AbstractCommand):

    def run(self):
        print "This would've purged the DB"

from peak.api import *

from peak.running.commands import AbstractCommand, Bootstrap

from bulletins.app import BulletinsApp



class BulletinsCmd(BulletinsApp, Bootstrap):

    usage = """
Usage: bulletins command arguments...


Available commands:

  createdb -- create an empty bulletins database
  purge    -- purge expired bulletins
"""


class CreateDB(BulletinsApp, AbstractCommand):

    def run(self):
        self.log.info("Creating %s using DDL from %s",
            self.dbURL, self.dbDDL
        )
        storage.beginTransaction(self)
        for ddl in open(self.dbDDL,'rt').read().split('\n;\n'):
            if not ddl.strip(): continue
            self.db(ddl)
        storage.commitTransaction(self)


class PurgeDB(BulletinsApp, AbstractCommand):

    def run(self):
        print "This would've purged the DB"

from peak.api import *

from peak.running.commands import AbstractCommand, Bootstrap, InvocationError

from bulletins.app import BulletinsApp



class BulletinsCmd(BulletinsApp, Bootstrap):

    usage = """
Usage: bulletins command arguments...


Available commands:

  createdb  -- create an empty bulletins database
  purge     -- purge expired bulletins
  showusers -- list current users
  adduser   -- add a user to the database
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







class ShowUsers(BulletinsApp, AbstractCommand):

    def run(self):
        print "User          Name"
        print "------------  -----------------------------------"
        storage.beginTransaction(self)
        for user in self.Users.getAll():
            print "%-12s  %s" % (user.loginId, user.fullName)
        storage.commitTransaction(self)


class AddUser(BulletinsApp, AbstractCommand):

    usage = """Usage: bulletins adduser login password [full name]"""

    def run(self):
        try:
            if len(self.argv)<3:
                raise InvocationError("missing argument(s)")

            storage.beginTransaction(self)
            user = self.Users.newItem()
            user.loginId, user.password = self.argv[1:3]
            user.fullName = ' '.join(self.argv[3:]) or user.loginId
            storage.commitTransaction(self)

        except SystemExit, v:
            return v.args[0]

        except InvocationError, msg:
            return self.invocationError(msg)


class PurgeDB(BulletinsApp, AbstractCommand):

    def run(self):
        print "This would've purged the DB"

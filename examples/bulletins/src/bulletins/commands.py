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










class AddCategory(BulletinsApp, AbstractCommand):

    usage = """Usage: bulletins addcat category [title]"""

    def run(self):
        try:
            if len(self.argv)<2:
                raise InvocationError("missing argument(s)")

            storage.beginTransaction(self)

            cat = self.Categories.newItem()
            cat.pathName = self.argv[1]
            cat.title = ' '.join(self.argv[2:]) or cat.pathName

            storage.commitTransaction(self)

        except SystemExit, v:
            return v.args[0]

        except InvocationError, msg:
            return self.invocationError(msg)


















            
class Post(BulletinsApp, AbstractCommand):

    usage = """Usage: bulletins post userid category <posting.txt"""

    def run(self):
        try:
            if len(self.argv)<>3:
                raise InvocationError("missing or extra argument(s)")

            userId, categoryId = self.argv[1:]
            text = self.stdin.read()

            storage.beginTransaction(self)
            
            user = self.Users[userId]
            category = self.Categories[categoryId]
            category.post(user, text)

            storage.commitTransaction(self)

        except SystemExit, v:
            return v.args[0]

        except InvocationError, msg:
            return self.invocationError(msg)
        

class PurgeDB(BulletinsApp, AbstractCommand):

    def run(self):
        print "This would've purged the DB"

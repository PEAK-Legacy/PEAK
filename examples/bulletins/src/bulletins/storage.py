from peak.api import *
from bulletins.model import *

__all__ = [
    'BulletinsForCategoryDM', 'CategoryDM', 'UserDM', 'BulletinDM',
]


class BulletinsForCategoryDM(storage.QueryDM):

    db         = binding.bindTo(PropertyName('bulletins.db'))
    BulletinDM = binding.bindTo('../Bulletins')  # XXX

    def _load(self, oid, ob):

        data = []
        preload = self.BulletinDM.preloadState
        stateFor = self.BulletinDM.stateForRow

        for row in self.db(
            "select * from bulletins where category = %s", (oid,)
        ):
            data.append(
                preload(row.id, stateFor(row))
            )

        return data














class UserDM(storage.EntityDM):

    db           = binding.bindTo(PropertyName('bulletins.db'))
    defaultClass = User

    def _load(self, oid):
        row = ~self.db("select * from users where loginId = %s", (oid,))
        return self.stateFromRow(row)

    def stateFromRow(self,row):
        return dict(
            Items(
                loginId = row.loginId,
                fullName = row.fullName,
                password = row.password,
            )
        )

    def _save(self, ob):
        self.db("""INSERT OR REPLACE INTO users
                (loginId, fullName, password) VALUES (%s, %s, %s)""",
            (ob.loginId, ob.fullName, ob.password)
        )

    def _new(self, ob):
        oid = ob._p_oid = ob.loginId
        self._save(ob)
        return oid

    def getAll(self):
        return [self.preloadState(row.loginId, self.stateFromRow(row))
            for row in self.db("select * from users")
        ]








class BulletinDM(storage.EntityDM):

    db           = binding.bindTo(PropertyName('bulletins.db'))
    CategoryDM   = binding.bindTo('../Categories')    # XXX
    UserDM       = binding.bindTo('../Users')         # XXX
    defaultClass = Bulletin

    def _load(self, oid):
        row = ~self.db("select * from bulletins where id = %d", (oid,))
        return self.stateFromRow(row)

    def stateFromRow(self,row):
        return dict(
            Items(
                id = row.id,
                category = self.CategoryDM[row.category],
                fullText = row.fullText,
                postedBy = self.UserDM[row.postedBy],
                postedOn = row.postedOn,
                editedBy = self.UserDM[row.editedBy],
                editedOn = row.editedOn,
                hidden = row.hidden <> 0,
            )
        )

    def _save(self, ob):
        self.db("""INSERT OR REPLACE INTO bulletins
                (id, category, fullText, postedBy, postedOn, editedBy,
                 editedOn, hidden) VALUES (%d, %s, %s, %s, %s, %s, %s, %d)""",
            (ob.id, ob.category, ob.fullText, ob.postedBy.loginId,
             ob.postedOn, ob.editedBy.loginId, ob.editedOn, ob.hidden)
        )
        
    def _new(self,ob):
        ct, = ~self.db('SELECT MAX(id) FROM bulletins')
        ct = (ct or 0) + 1
        ob._p_oid = ct
        self._save(ob)
        return ct


class CategoryDM(storage.EntityDM):

    db = binding.bindTo(PropertyName('bulletins.db'))

    bulletinsForCategory = binding.bindTo('../BulletinsForCategory')

    defaultClass = Category

    def _load(self, oid, ob):
        row = ~db("select * from categories where pathName = %s", (oid,))
        return self.stateFromRow(row)

    def stateFromRow(self,row):
        return dict(
            Items(
                pathName = row.pathName,
                title = row.title,
                sortPosn = row.sortPosn,
                bulletins = self.bulletinsForCategory[oid],
                sortBulletinsBy = SortBy[row.sortBulletinsBy],
                postingTemplate = row.postingTemplate,
                editingTemplate = row.editingTemplate,              
            )
        )

    def _save(self, ob):
        self.db("""INSERT OR REPLACE INTO categories
                (pathName, title, sortPosn, sortBulletinsBy, postingTemplate,
                editingTemplate) VALUES (%s, %s, %d, %s, %s, %s)""",
            (ob.pathName, ob.title, ob.sortPosn, ob.sortBulletinsBy.value,
             ob.postingTemplate, ob.editingTemplate)
        )

    def _new(self, ob):
        ob._p_oid = ob.pathName
        self._save(ob)
        return ob.pathName




    def getAll(self):
        return [self.preloadState(row.pathName, self.stateFromRow(row))
            for row in self.db("select * from categories")
        ]



from peak.api import *

class BulletinsApp(binding.Component):

    dbURL = binding.bindTo(PropertyName('bulletins.databaseURL'))
    dbDDL = binding.bindTo(PropertyName('bulletins.databaseDDL'))

    db = binding.Once(
        lambda self,d,a: self.lookupComponent(
            self.dbURL, adaptTo=storage.ISQLConnection
        ),
        offerAs = [PropertyName('bulletins.db')]
    )

    log = binding.bindTo('logging.logger:bulletins.app')

    Bulletins  = binding.New('bulletins.storage:BulletinDM')
    Categories = binding.New('bulletins.storage:CategoryDM')
    Users      = binding.New('bulletins.storage:UserDM')

    BulletinsForCategory = binding.New(
        'bulletins.storage:BulletinsForCategoryDM'
    )

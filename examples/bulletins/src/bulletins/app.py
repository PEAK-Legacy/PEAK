from peak.api import *
from model import *

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

    Bulletins = binding.New(
        'bulletins.storage:BulletinDM',
        offerAs=[storage.DMFor(Bulletin)]
    )

    Categories = binding.New(
        'bulletins.storage:CategoryDM',
        offerAs=[storage.DMFor(Category)]
    )

    Users = binding.New(
        'bulletins.storage:UserDM',
        offerAs=[storage.DMFor(User)]
    )



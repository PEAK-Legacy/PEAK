from peak.api import *
from model import *

class BulletinsApp(binding.Component):

    dbURL = binding.Obtain(PropertyName('bulletins.databaseURL'))
    dbDDL = binding.Obtain(PropertyName('bulletins.databaseDDL'))

    db = binding.Make(
        lambda self: self.lookupComponent(
            self.dbURL, adaptTo=storage.ISQLConnection
        ),
        offerAs = [PropertyName('bulletins.db')]
    )

    log = binding.Obtain('logging.logger:bulletins.app')

    Bulletins = binding.Make(
        'bulletins.storage:BulletinDM',
        offerAs=[storage.DMFor(Bulletin)]
    )

    Categories = binding.Make(
        'bulletins.storage:CategoryDM',
        offerAs=[storage.DMFor(Category)]
    )

    Users = binding.Make(
        'bulletins.storage:UserDM',
        offerAs=[storage.DMFor(User)]
    )



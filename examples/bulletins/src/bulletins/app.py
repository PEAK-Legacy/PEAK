from peak.api import *

class BulletinsApp(binding.Component):

    dbURL = binding.bindTo(PropertyName('bulletins.databaseURL'))
    dbDDL = binding.bindTo(PropertyName('bulletins.databaseDDL'))

    db = binding.Once(
        lambda self,d,a: self.lookupComponent(
            self.dbURL, adaptTo=storage.ISQLConnection
        )
    )

    log = binding.bindTo('logging.logger:bulletins.app')


from peak.api import *

import peak.web.publish     # XXX ugly hack!

class WebApp(binding.Component):

    security.allow(
        index_html = [security.Anybody]
    )
     
    def index_html(self):
        return "Hello world!"


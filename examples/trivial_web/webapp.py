from peak.api import *

class WebApp(binding.Component):

    security.allow(
        index_html = security.Anybody
    )
     
    def index_html(self):
        return "Hello world!"


from peak.api import *

class AnonInteraction(web.BaseInteraction):

    user = None
    
    def getDefaultTraversal(self, request, ob):

        """Default / to /index_html"""

        if adapt(ob.getObject(), self.behaviorProtocol, None) is not None:
            # object is renderable, no need for further traversal
            return ob, ()
            
        # Not renderable, try for 'index_html'
        return ob, ('index_html',)
        

class WebApp(binding.Component):

    security.allow(
        index_html = [security.Anybody]
    )
     
    def index_html(self):
        return "Hello world!"
        
    interactionClass = binding.Constant(
        AnonInteraction, offerAs=[web.INTERACTION_CLASS]
    )


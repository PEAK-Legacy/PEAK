from peak.naming.api import *

class OpenableURL(ParsedURL):

    def retrieve(self, refInfo, name, context, attrs=None):
        import urllib2
        return urllib2.urlopen(str(self))



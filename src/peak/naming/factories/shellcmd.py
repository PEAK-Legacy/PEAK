from peak.api import *
import os

class ShellCommandURL(naming.URL.Base):

    supportedSchemes = 'shellcmd',

    def retrieve(self, refInfo, name, context, attrs=None):

        def invoke():
            return os.system(self.body)

        return invoke


from peak.api import *
import os

class ShellCommandURL(naming.URL.Base):

    supportedSchemes = 'shellcmd',

    def __call__(self):
        return os.system(self.body)


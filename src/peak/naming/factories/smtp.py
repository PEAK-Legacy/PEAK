from peak.naming import *
from peak.naming.contexts import AbstractContext
import re, smtplib


class smtpURL(ParsedURL):
    _supportedSchemes = ('smtp', )
    
    pattern = re.compile('(?P<server>.*)')



class smtpContext(AbstractContext):
    _supportedSchemes = ('smtp', )
    _makeName = smtpURL
    
    def _get(self, name, default=None, retrieve=1):
        if retrieve:
            return (RefAddr('smtp', name.server), None)
        else:
            return name



def smtpFactory(refInfo, name, context, environment, attrs=None):
    return smtplib.SMTP(refInfo.content)

from peak.naming.names import ParsedURL
from peak.naming.contexts import AbstractContext
from peak.naming.references import RefAddr
from peak.naming.interfaces import IObjectFactory
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

from peak.naming.api import *
from peak.naming.contexts import AbstractContext

import re, smtplib


class smtpURL(ParsedURL):
    _supportedSchemes = ('smtp', )
    
    pattern = re.compile(
        '//((?P<user>[^;]+)(;AUTH=(?P<auth>.+))?@)?(?P<host>[^:]*)(:(?P<port>[0-9]+))?',
        re.IGNORECASE
    )

    def _fromURL(self, url):
        super(smtpURL, self)._fromURL(url)
        if self.port:
            self.port = int(self.port)
        else:
            self.port = smtplib.SMTP_PORT



class smtpContext(AbstractContext):
    _supportedSchemes = ('smtp', )
    _makeName = smtpURL
    
    def _get(self, name, default=None, retrieve=1):
        if retrieve:
            return (RefAddr('smtp', name), None)
        else:
            return name



def smtpFactory(refInfo, name, context, environment, attrs=None):
    return smtplib.SMTP(refInfo.content.host, refInfo.content.port)

from peak.naming.api import *
from peak.naming.contexts import AbstractContext

import re, smtplib


class smtpURL(ParsedURL):

    _supportedSchemes = ('smtp', )

    __fields__     = 'port','host','scheme','body','user','auth'
    __converters__ = int,
    __defaults__   = smtplib.SMTP_PORT,

    pattern = re.compile(
        '//((?P<user>[^;]+)(;AUTH=(?P<auth>.+))?@)?(?P<host>[^:]*)(:(?P<port>[0-9]+))?',
        re.IGNORECASE
    )




class smtpContext(AbstractContext):
    _supportedSchemes = ('smtp', )
    _makeName = smtpURL
    
    def _get(self, name, default=None, retrieve=1):
        if retrieve:
            return (RefAddr('smtp',name), None)
        else:
            return name



def smtpFactory(refInfo, name, context, environment, attrs=None):
    return smtplib.SMTP(refInfo.content.host, refInfo.content.port)

from peak.naming.api import ParsedURL

import re, smtplib


class smtpURL(ParsedURL):

    def _defaultObjectFactory(self, refInfo, name, context, environment, attrs=None):
        return smtplib.SMTP(refInfo.host, refInfo.port or smtplib.SMTP_PORT)
    
    _supportedSchemes = ('smtp', )

    __fields__     = 'port','host','scheme','body','user','auth'
    __converters__ = int,
    __defaults__   = smtplib.SMTP_PORT,

    pattern = re.compile(
        '//((?P<user>[^;]+)(;AUTH=(?P<auth>.+))?@)?(?P<host>[^:]*)(:(?P<port>[0-9]+))?',
        re.IGNORECASE
    )


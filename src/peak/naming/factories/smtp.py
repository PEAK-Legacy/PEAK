from peak.naming.api import ParsedURL, IAddress

import re, smtplib


class smtpURL(ParsedURL):

    __implements__ = IAddress

    def retrieve(self, refInfo, name, context, environment, attrs=None):
        return smtplib.SMTP(self.host, self.port)
    
    _supportedSchemes = ('smtp', )

    __fields__     = 'host','port','user','auth','scheme','body',


    def fromArgs(klass,
        host, port=smtplib.SMTP_PORT, user=None, auth=None, scheme='smtp', body=None
    ):
        port = port and int(port) or smtplib.SMTP_PORT
        return tuple.__new__(klass, (host,port,user,auth,scheme,body))

    fromArgs = classmethod(fromArgs)

    pattern = re.compile(
        '//((?P<user>[^;]+)(;AUTH=(?P<auth>.+))?@)?(?P<host>[^:]*)(:(?P<port>[0-9]+))?',
        re.IGNORECASE
    )


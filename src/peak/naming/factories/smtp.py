from peak.naming.api import ParsedURL

import smtplib


class smtpURL(ParsedURL):

    def retrieve(self, refInfo, name, context, attrs=None):
        return smtplib.SMTP(self.host, self.port)
    
    _supportedSchemes = ('smtp', )

    __fields__        = 'host','port','user','auth','scheme','body',


    def fromArgs(klass,
        host, port=smtplib.SMTP_PORT, user=None, auth=None,
        scheme='smtp', body=None
    ):
        port = port and int(port) or smtplib.SMTP_PORT
        return tuple.__new__(klass, (host,port,user,auth,scheme,body))


    pattern = """
        (?iX)   # ignore case, use verbose formatting

        //((?P<user>[^;]+)(;AUTH=(?P<auth>.+))?@)?  # authorization
        (?P<host>[^:]*)(:(?P<port>[0-9]+))?         # host + port
    """


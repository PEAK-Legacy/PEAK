from peak.naming.api import ParsedURL

import smtplib


class smtpURL(ParsedURL):

    _defaultScheme = 'smtp'
    
    _supportedSchemes = ('smtp', )


    pattern = """(?ix)   # ignore case, use verbose formatting

        //((?P<user>[^;]+)(;AUTH=(?P<auth>.+))?@)?  # authorization
        (?P<host>[^:]*)(:(?P<port>[0-9]+))?         # host + port
    """

    def __init__(self, scheme=None, body=None,
        host=None, port=smtplib.SMTP_PORT, user=None, auth=None,
    ):
        self.setup(locals())

    def parse(self,scheme,body):

        d = super(smtpURL,self).parse(scheme,body)

        if 'port' in d:
            d['port'] = int(d['port'])
        return d

    def retrieve(self, refInfo, name, context, attrs=None):
        return smtplib.SMTP(self.host, self.port)
   



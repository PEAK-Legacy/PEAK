from peak.api import naming, model
import smtplib


class smtpURL(naming.URL.Base):

    supportedSchemes = ('smtp', )

    pattern = """(?ix)   # ignore case, use verbose formatting

        //((?P<user>[^;]+)(;AUTH=(?P<auth>.+))?@)?  # authorization
        (?P<host>[^:]*)(:(?P<port>[0-9]+))?         # host + port
    """

    class user(naming.URL.Field):
        pass

    class port(naming.URL.IntField):
        defaultValue=smtplib.SMTP_PORT

    class host(naming.URL.Field):
        pass

    class auth(naming.URL.Field):
        pass

    def retrieve(self, refInfo, name, context, attrs=None):
        return smtplib.SMTP(self.host, self.port)




from peak.api import naming, model
import smtplib


class smtpURL(naming.ParsedURL):

    supportedSchemes = ('smtp', )

    pattern = """(?ix)   # ignore case, use verbose formatting

        //((?P<user>[^;]+)(;AUTH=(?P<auth>.+))?@)?  # authorization
        (?P<host>[^:]*)(:(?P<port>[0-9]+))?         # host + port
    """

    class user(model.structField):
        referencedType=model.String
        defaultValue=None

    class port(model.structField):
        referencedType=model.Integer
        defaultValue=smtplib.SMTP_PORT

    class host(model.structField):
        referencedType=model.String
        defaultValue=None

    class auth(model.structField):
        referencedType=model.String
        defaultValue=None

    def retrieve(self, refInfo, name, context, attrs=None):
        return smtplib.SMTP(self.host, self.port)




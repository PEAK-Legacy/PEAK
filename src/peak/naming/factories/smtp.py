from peak.api import naming, model
import smtplib


class smtpURL(naming.URL.Base):

    supportedSchemes = ('smtp', )

    class user(naming.URL.Field):
        pass

    class port(naming.URL.IntField):
        defaultValue=smtplib.SMTP_PORT

    class host(naming.URL.RequiredField):
        pass

    class auth(naming.URL.Field):
        pass

    syntax = naming.URL.Sequence(
        '//',
        (   user,
            (naming.URL.StringConstant(';AUTH=',False), auth),
            '@',
        ),
        host, (':', port)
    )

    # XXX def retrieve(self, refInfo, name, context, attrs=None):
    # XXX    return smtplib.SMTP(self.host, self.port)




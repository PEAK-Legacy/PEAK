"""LDAP tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *

from peak.storage.LDAP import LDAPCursor, LDAPConnection

class TestCursor(LDAPCursor):

    msgid = 9999

    def fooCvt(name,values):
        if values: return values[0]

    fooCvt = binding.Constant(
        PropertyName('peak.ldap.field_converters.foo'), fooCvt
    )

    def barCvt(name,values):
        if values: return int(values[0])

    barCvt = binding.Constant(
        PropertyName('peak.ldap.field_converters.bar'), barCvt
    )

    class _conn(object):

        def result(msgid, getall, timeout):
            return 'RES_SEARCH_RESULT', [
                ('uid=thing1', {'foo':[], 'baz':['a','b']}),
                ('uid=thing2', {'foo':['spam'], 'bar':['999']}),
            ]

        result = staticmethod(result)







class LDAPSchemaTest(TestCase):

    def checkConversions(self):
        ob = TestCursor(LDAPConnection(), None)
        assert list(ob)==[
            ('uid=thing1', None, ['a','b']),
            ('uid=thing2', 'spam', None, 999),
        ]


TestClasses = (
    LDAPSchemaTest,
)


def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])

































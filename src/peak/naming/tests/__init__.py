"""Naming system tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *


parse = naming.InitialContext(objectFactories=[]).lookup

validNames = {

    'smtp://foo':
        Items(host='foo',port=25),

    'ldap://localhost:9912':
        Items(host='localhost',port=9912),

    'uuid:6ba7b810-9dad-11d1-80b4-00c04fd430c8':
        Items(uuid='6ba7b810-9dad-11d1-80b4-00c04fd430c8', quals=()),

    'uuid:00000000-0000-0000-0000-000000000000;ext1=1;ext2=2':
        Items(uuid='00000000-0000-0000-0000-000000000000',
              quals=(('ext1','1'), ('ext2','2'))
        ),
        
    'sybase:foo:bar@baz/spam':
        Items(server='baz', db='spam', user='foo', passwd='bar'),
        
    'import:bada.bing':
        Items(body='bada.bing'),
        
    'lockfile:c:\\spam.lock':
        Items(body='c:\\spam.lock'),
}








class NameParseTest(TestCase):

    def checkValid(self):
        map(parse,validNames.keys())

    def checkData(self):
        for name,values in validNames.items():
            obj = parse(name)
            for (k,v) in values:
                assert getattr(obj,k)==v, (k,getattr(obj,k),v)



TestClasses = (
    NameParseTest,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































"""Naming system tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *

validNames = {

    'smtp://foo':
        Items(host='foo', port=25),

    'smtp://foo.bar:8025':
        Items(host='foo.bar', port=8025),

    'ldap://localhost:9912':
        Items(host='localhost', port=9912),

    'uuid:6ba7b810-9dad-11d1-80b4-00c04fd430c8':
        Items(uuid='6ba7b810-9dad-11d1-80b4-00c04fd430c8', quals=()),

    'uuid:00000000-0000-0000-0000-000000000000;ext1=1;ext2=2':
        Items(uuid='00000000-0000-0000-0000-000000000000',
              quals=(('ext1','1'), ('ext2','2'))
        ),
        
    'sybase:foo:bar@baz/spam':
        Items(server='baz', db='spam', user='foo', passwd='bar'),

    'sybase://user:p%40ss@server':
        Items(server='server', db=None, user='user', passwd='p@ss'),

    'gadfly://drinkers@c:\\temp':
        Items(db='drinkers', dir=r'c:\temp'),
        
    'import:bada.bing':
        Items(body='bada.bing'),
        
    'lockfile:c:\\spam.lock':
        Items(body='c:\\spam.lock'),
}


parse = naming.InitialContext(objectFactories=[]).lookup

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

































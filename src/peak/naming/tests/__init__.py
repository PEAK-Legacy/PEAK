"""Naming system tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

validNames = {

    'smtp://foo':
        Items(host='foo', port=25),

    'smtp://foo.bar:8025':
        Items(host='foo.bar', port=8025),

    'ldap://cn=root:somePw@localhost:9912/cn=monitor':
        Items(
            host='localhost', port=9912, basedn=('cn=monitor',),
            extensions={'bindname':(1,'cn=root'), 'x-bindpw':(1,'somePw')}
        ),

    'ldap://localhost/cn=Bar,ou=Foo,o=eby-sarna.com':
        Items(
            host='localhost', port=389,
            basedn=('o=eby-sarna.com','ou=Foo','cn=Bar'),
        ),

    'ldap:///cn="A \\"quoted\\", and obscure thing",ou=Foo\\,Bar':
        Items(
            basedn=('ou=Foo\\,Bar','cn="A \\"quoted\\", and obscure thing"'),
        ),

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

    'gadfly://drinkers@c:\\temp': Items(db='drinkers', dir=r'c:\temp'),

    'import:bada.bing':
        Items(body='bada.bing'),

    'lockfile:c:\\spam.lock':
        Items(body='c:\\spam.lock'),

    'config:environ.TMP/':
        Items(scheme='config', body=(('environ','TMP'),'') ),
}


def parse(url):
    return naming.parseURL(testRoot(),url)


class NameParseTest(TestCase):

    def checkValid(self):
        map(parse,validNames.keys())

    def checkData(self):
        for name,values in validNames.items():
            obj = parse(name)
            for (k,v) in values:
                assert getattr(obj,k)==v, (k,getattr(obj,k),v)








from peak.naming.api import CompoundName as lname, CompositeName as gname
from peak.storage.LDAP import ldapURL as LU, distinguishedName as dN

additions = [
    ( dN('ou=foo,o=eby-sarna.com'), dN('cn=bar'),
        dN('cn=bar,ou=foo,o=eby-sarna.com')
    ),
    ( LU('ldap','///ou=foo,o=eby-sarna.com'), dN('cn=bar'),
        LU('ldap','///cn=bar,ou=foo,o=eby-sarna.com')
    ),
    ( LU('ldap','///ou=foo,o=eby-sarna.com'), gname([dN('cn=bar')]),
        LU('ldap','///cn=bar,ou=foo,o=eby-sarna.com')
    ),
    ( lname(['x','y']), lname(['z']), lname(['x','y','z']) ),
    ( '', lname(['foo']), lname(['foo']) ),
    ( gname(['a','b','']), lname(['x']), gname(['a','b',lname(['x'])]) ),
    ( gname(['a','b','']), gname(['','c']), gname(['a','b','','c']) ),
]


class NameAdditionTest(TestCase):
    def checkAdds(self):
        for n1,n2,res in additions:
            assert n1+n2==res, (n1,n2,n1+n2,res)


TestClasses = (
    NameParseTest, NameAdditionTest
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)





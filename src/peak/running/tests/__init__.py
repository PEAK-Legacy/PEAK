"""Running system tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *

from peak.running.clusters import loadCluster

test = binding.Component()

loadCluster(test, config.fileNearModule(__name__,'test_cluster.txt'))

pm = running.CLUSTER.of(test)


groupToHosts = Items(

    __all__= (
            'foo.baz.com', 'bar.baz.com', 'one.baz.com', 'three.baz.com',
            'five.baz.com', 'two.baz.com','four.baz.com','six.baz.com',
            'frob.baz.com'
    ),

    __orphans__ = ('foo.baz.com', 'bar.baz.com'),

    odd     = ('one.baz.com','three.baz.com','five.baz.com'),
    even    = ('two.baz.com','four.baz.com','six.baz.com'),
    prime   = ('one.baz.com','three.baz.com','five.baz.com','two.baz.com'),
    qux     = ('one.baz.com','frob.baz.com'),
    
    weird   = (
        'one.baz.com','three.baz.com','five.baz.com','two.baz.com',
        'frob.baz.com'
    ),
)






        
class ClusterTests(TestCase):

    def checkHosts(self):
        assert pm.hosts()==pm.groups['__all__']

    def checkGroups(self):
        assert pm.groups()==('odd','even','prime','qux','weird')

    def checkMembers(self):
        for group, members in groupToHosts:
            assert pm.groups[group] == members, (group,members,pm.groups[group])

    # XXX need host->group tests, plus ???


TestClasses = (
    ClusterTests,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)

































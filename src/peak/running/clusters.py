"""Utilities for dealing with clusters of loosely-coupled systems.

 Many enterprise applications will be run, rather than on a single
 computer, in a loosely-coupled cluster of machines.  A set of several
 web-servers, for example.  We have found the
 "clusterit tools":http://www.garbled.net/clusterit.html to be very useful
 in such situations.  Clusterit, inspired by the tools provided in IBM's
 PSPP, is simple to set up and use, if somewhat quirky in implementation.

 PEAK supports the cluster definition file used by Clusterit, providing
 the information contained therein via the properties mechanism.  Note
 that you don't have to have the Clusterit tools installed to make use of
 this, or for it to be useful.  Nor will anything break if you make use
 of these properties in your application and they haven't been set up.
 In the abscence of a cluster definition file, PEAK will behave as if
 the local hostname was listed in the cluster file, without being part
 of a group.

 Then environment variable 'CLUSTER' (or, in PEAK's case, the property
 'peak.running.cluster._filename', if it exists, else 'environ.CLUSTER')
 specifies a file defining the cluster.  A cluster may be subdivided into
 groups.  In PEAK it is allowable for groups to have overlapping
 membership.  Let's look at a fairly complicated example::

    foo.baz.com
    bar.baz.com
    GROUP:odd
    one.baz.com
    three.baz.com
    five.baz.com
    GROUP:even
    two.baz.com
    four.baz.com
    six.baz.com
    GROUP:prime
    one.baz.com
    two.baz.com
    three.baz.com
    five.baz.com
    GROUP:qux
    frob.baz.com
    one.baz.com
    LUMP:weird
    qux
    prime

 PEAK treats this file as if it had seven groups.  The existance and
 memberships of the first four groups, 'odd', 'even', 'prime', and 'qux',
 should be clear.  A "lump" is a group defined in terms of other groups or
 lumps.  In this case the group 'weird' contains the union of the groups
 'qux' and 'prime'.  Note that one.baz.com is a member of both qux and prime. 
 The group 'weird' will contain it only once, however -- duplicates are
 removed automatically.  Another group, '__orphans__', contains any hosts
 that were listed at the beginning of the file before any 'GROUP:' lines. 

 Each group is exported as a property 'peak.running.cluster.groups.<groupname>'
 (for example, 'peak.running.cluster.groups.prime') with it's value a tuple of
 strings of the hostnames of the members.

 The property 'peak.running.cluster.groups' will contain a tuple of strings
 naming each group except the '__orphans__' group.

 The property 'peak.running.cluster.hosts.<hostname>' will be a tuple of
 strings of the names of all groups the host belongs to.  For example, in
 the example above, 'peak.running.cluster.hosts.one.baz.com'
 is '("odd", "prime", "qux", "wierd")'.

 Finally, the property 'peak.running.cluster.hostname' is a string with
 the local machine's network hostname (per 'socket.gethostname()'), and
 'peak.running.cluster.shortname' is the the same, truncated after the
 first '"."', if any. 
"""

from peak.api import *
import os

from kjbuckets import *





def parseCluster(prefix, fn):

    props = {}

    try:
        import socket
        hn =socket.gethostname()

    except:
        hn = 'NO_NAME'

    props[prefix + 'hostname'] = hn
    props[prefix + 'shortname'] = hn.split('.', 1)[0]

    if fn is None or not os.path.exists(fn):
        props[prefix + 'hosts'] = (hn,)
        props[prefix + 'groups.__orphans__'] = (hn,)
        props[prefix + 'groups'] = ()
        
        return props


    all    = kjGraph()
    groups = kjSet()
    hosts  = kjSet()

    gname  = '__orphans__'
    inLump = False


    for l in open(fn, 'r'):

        l = l.strip()

        if not l or l.startswith('#'):
            continue

        lumpline = l.startswith('LUMP:')



        if lumpline or l.startswith('GROUP:'):

            inLump  = lumpline
            gname = l.split(':', 1)[1] 

            groups.add(gname)

        else:
            all.add(l, gname)

            if inLump:
                groups.add(l)
            else:
                hosts.add(l)


    host_pre  = prefix+'hosts.'
    group_pre = prefix+'groups.'

    for host in hosts.values():
        props[host_pre + host]   = tuple(all.reachable(host).values())


    g = ~all    # get reverse mappping from groups to hosts

    for group in groups.values() + ['__orphans__']:

        props[group_pre + group] = tuple(
            # don't include groups in groups' membership
            (g.reachable(group) - groups).values()
        )


    props[prefix + 'groups']           = tuple(groups.values())
    props[prefix + 'hosts']            = tuple(hosts.values())
    props[prefix + 'groups.__all__']   = tuple(hosts.values())

    return props




cache = {}


def loadCluster(propertyName, prefix, targetObj=None):

    prefix = naming.PropertyName(prefix).asPrefix()
    
    r = cache.get((prefix, targetObj))

    if r is None:
        fn = config.getProperty(prefix + '_filename', targetObj)
        r = parseCluster(prefix, fn)
            
        cache[(prefix, targetObj)] = r
    
    return r.get(propertyName, NOT_FOUND)

    

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
 the local hostname was listed in the cluster file (as a member of
 '_orphans' or '_all').

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
    LUMP:wierd
    qux
    prime

 PEAK treats this file as if it had seven groups.  The existance and
 memberships of the first four groups, 'odd', 'even', 'prime', and 'qux',
 should be clear.  A "lump" is a group defined in terms of other groups or
 lumps.  In this case the group 'wierd' contains the union of the groups
 qux and prime.  Note that one.baz.com is a member of both qux and prime. 
 The group "wierd" will contain it only once, however -- duplicates are
 removed automatically.  Another group, '_orphans', contains any hosts
 that were listed at the beginning of the file before any 'GROUP:' lines. 
 Finally, the group '_all' contains the union of all hosts from all groups
 (including '_orphans').

 Each group is exported as a property 'peak.running.cluster.<groupname>'
 (for example, 'peak.running.cluster._all') with it's value a tuple of
 strings of the hostnames of the members.

 The property 'peak.running.cluster._groups' will contain a
 tuple of strings naming each explicit group (that is, leaving out
 '_orphans' and '_all'). 

 The property 'peak.running.cluster._host.<hostname>' will be a tuple of
 strings of the names of all groups the host belongs to (except '_all')
 For example, in the example above, 'peak.running.cluster._host.one.baz.com'
 is '("odd", "prime", "qux", "wierd")'.

 Finally, the property 'peak.running.cluster._hostname' is a string with
 the local machine's network hostname (per 'socket.gethostname()'), and
 'peak.running.cluster._shortname' is the the same, truncated after the
 first '"."', if any. 
"""

from peak.api import *
import os




def union(t1, t2):
    d = {}
    
    for k in t1:
        d[k] = 1
    l = list(t1)
    for k in t2:
        if k not in d:
            l.append(k)

    return tuple(l)






























def parseCluster(prefix, fn):

    all = {}; gname = '_orphans'; group = (); groups = []
    props = {prefix + gname : group}
    lump = 0
    
    try:
        import socket
        hn =socket.gethostname()
    except:
        hn = 'NO_NAME'

    props[prefix + '_hostname'] = hn
    props[prefix + '_shortname'] = hn.split('.', 1)[0]

    if fn is None or not os.path.exists(fn):
        props[prefix + '_all'] = (hn,)
        props[prefix + '_orphans'] = (hn,)
        props[prefix + '_groups'] = ()
        
        return props
       
    for l in open(fn, 'r'):

        l = l.strip()

        if not l or l.startswith('#'):
            continue

        lumpline = l.startswith('LUMP:')
        
        if lumpline or l.startswith('GROUP:'):
            lump = lumpline
            group = ()
            gname = l.split(':', 1)[1] 
            props[prefix + gname] = group
            groups.append(gname)



            
        else:
            if lump:
                na = props.get(prefix + l, ())
                props[prefix + gname] = union(props[prefix + gname], na)
                for h in na:
                    all[h] = union(all[h], (gname,))
            else:
                all.setdefault(l, []).append(gname)
                props[prefix + gname] += l,

    for k, v in all.items():
        props[prefix + '_host.' + k] = tuple(v)

    props[prefix + '_groups'] = tuple(groups)
    props[prefix + '_all'] = tuple(all.keys())

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

    

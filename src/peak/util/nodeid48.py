"""
Get a unique 48 bit identifier for the current machine, suitable for use
in generating UUIDS. The result of getnodeid48() is a 12 character
lowercase hexadecimal string.

We use the algorithms from draft-leach-uuids-guids-01.  We return an
ethernet address of the host if possible, but there is no guarantee that
we can do so.  Do *NOT* assume that you will get the ethernet address. 
The host may not have one, or may have more than one.  In fact, if the
host has more than one, there is no guarantee that you will get the same
one every time. 
"""

import sys, os, time, re
try:
    import posix
except:
    posix = None

__all__ = ['getnodeid48']

_hid48 = None

r = ':'.join(["([0-9a-f]{2})"]*6)
r = re.compile(r, re.IGNORECASE)

def from_ifconfig():
    try:
        f = os.popen('/sbin/ifconfig -a')
        s = f.read()
        f.close()
        m = r.search(s)
        if m:
            m = ''.join(m.groups())
            return m.lower()
    except:
        pass
    
    return None


def from_6bytes(s):
    try:
        s = [ord(x) for x in s]
        s[0] = s[0] | 128
        s = ["%02x" % x for x in s]
        s = ''.join(s)
        return s.lower()
    except:
        pass
        
    return None

       
def from_devrandom():
    try:
        f = open('/dev/urandom')
        s = f.read(6)
        f.close()
        if len(s) != 6:
            return None

        return from_6bytes(s)
    except:
        return None
        
    
def from_fallback():
    try:
        import socket
        hn = socket.gethostname()
    except:
        hn = ""

    try:
        p = os.getpid()
    except:
        p = 42
                
    try:
        import whrandom
        r = whrandom.random()
    except:
        r = 17 # the least random number

    s = "%s-%s-%s-%s" % (p, time.time(), id(time), id(os))
    s = "%s-%s-%s-%s-%s" % (s, sys.version, sys.byteorder, hn, hash(hash))
    s = "%s-%s-%s-%s-%s" % (s, sys.getrefcount(None), id(None), id(r), id(p))
    s = "%s-%s-%s-%s-%s" % (s, id(time.time()), id(s), id(hn), r)
    
    try:
        import sha
        s = sha.sha(s).digest()
    except:
        try:
            import md5
            s = md5.md5(s).digest()
        except:
            pass

    return from_6bytes(s[:6])


def from_win32():
    return None # XXX


methods = [from_fallback]

# Unixy
#
# The unix-dependand ways of finding an ID should fail gracefully if the
# system is not supported, but the below contains sys.platform values
# for which we shouldn't even bother trying.

not_unixy_enough = ['win32']

if posix is not None and sys.platform not in not_unixy_enough:
    methods = [from_ifconfig, from_devrandom] + methods

# Win32
if sys.platform == 'win32':
    methods = [from_win32] + methods

# Add others here...



def getnodeid48():
    global _hid48, methods
    
    if _hid48 is None:
        for method in methods:
            _hid48 = method()
            if _hid48 is not None:
                break

    return _hid48

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


def from_random():
    from peak.util.random import randbytes

    s = randbytes(6)
    s = [ord(x) for x in s]
    s[0] = s[0] | 128
    s = ["%02x" % x for x in s]
    s = ''.join(s)
    return s.lower()


def from_win32():
    try:
        from pywintypes import CreateGuid
    except ImportError:
        try:
            from pythoncom import CreateGuid
        except ImportError:
            return None

    # take last 12 chars before closing '}'
    return CreateGuid()[-13:-1]


methods = [from_random]

if posix is not None and sys.platform != 'win32':
    methods = [from_ifconfig] + methods

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

from TW.API import *

import testM1

__bases__ = testM1,

class BaseClass:
    foo = 2

class Subclass:

    class NestedSub:
        spam = 'Nested'
        
aGlobal1 = 'M2'

def aFunc2(aParam):
    return 'after(%s)' % __proceed__('before(%s)' % aParam)

setupModule()

from peak.api import *
from interfaces import *
from places import Location
from peak.util.imports import lazyModule
from peak.util import SOX

def isRoot(data):
    return 'previous' not in data

def finishComponent(parser,data):
    if 'sm.component' in data:
        return data['sm.component']

def getGlobals(data):
    cur = data
    while 'sm_globals' not in cur:
        cur = cur['previous']
    return data.setdefault('sm_globals',cur['sm_globals'].copy())

def findComponentData(data):
    prev = data['previous']
    while 'sm.component' not in prev:
        prev = prev.get('previous')
    return prev

def assertNotTop(parser,data):
    if isRoot(data['previous']):
        parser.err(
            "%(name)r element cannot be top-level in the document" % data
        )

def evalObject(data,expr):
    g = getGlobals(data['previous'])
    return eval(expr,g,g)







def acquirePermission(data,attrs):
    if 'permission' in attrs:
        perm = data['sm.permission'] = evalObject(data,attrs['permission'])
        return perm
    while data is not None and 'sm.permission' not in data:
        data = data.get('previous')
    if data is not None:
        return data['sm.permission']
    return security.Anybody


locRequired = ()
locOptional = 'name','class','id','permission',

def startLocation(parser,data):
    attrs = SOX.validatedAttributes(parser,data,locRequired,locOptional)
    acquirePermission(data,attrs)
    prev = findComponentData(data)
    parent = prev['sm.component']
    name = attrs.get('name')
    if isRoot(prev):
        if name is not None:
            parser.err("Root location cannot have a 'name'")
    elif not name:
        parser.err("Non-root locations must have a 'name'")

    if 'class' in attrs:
        loc = evalObject(data,attrs['class'])(parent,name)
    else:
        loc = Location(parent,name)

    if 'id' in attrs:
        loc.registerLocation(attrs['id'],'.')

    data['sm.component'] = loc
    data['sm.sublocations'] = subloc = {}
    loc.addContainer(subloc)




def defineLocation(parser,data):
    data['finish'] = finishComponent
    data['start'] = startLocation
    prev = findComponentData(data)

    def addLocation(loc):
        data['sm.sublocations'][loc.getComponentName()] = loc
    data['child'] = addLocation


def doImport(parser,data):
    attrs = SOX.validatedAttributes(parser,data,('module',),('as',))
    module = attrs['module']
    as_ = attrs.get('as', module.split('.')[-1])
    getGlobals(data['previous'])[as_] = lazyModule(module)

def defineImport(parser,data):
    assertNotTop(parser,data)
    data['start'] = doImport
    data['empty'] = True


def doContainer(parser,data):
    attrs = SOX.validatedAttributes(parser,data,('object',),('permission',))
    prev = findComponentData(data)
    perm = acquirePermission(data,attrs)
    prev['sm.component'].addContainer(evalObject(data,attrs['object']),perm)

def defineContainer(parser,data):
    assertNotTop(parser,data)
    data['start'] = doContainer
    data['empty'] = True









def doOffer(parser,data):
    attrs = SOX.validatedAttributes(parser,data,('path','as',))
    prev = findComponentData(data)
    perm = acquirePermission(data,attrs)
    prev['sm.component'].registerLocation(attrs['as'],attrs['path'])

def defineOffer(parser,data):
    assertNotTop(parser,data)
    data['start'] = doOffer
    data['empty'] = True


def doRequire(parser,data):
    attrs = SOX.validatedAttributes(parser,data,('permission',))    #, helper
    acquirePermission(data,attrs)

def defineRequire(parser,data):
    assertNotTop(parser,data)
    data['start'] = doRequire


def setupDocument(parser,data):

    def setRoot(ob):
        data['sm.component'] = ob

    data['child'] = setRoot
    data['finish'] = finishComponent
    data['sm.component'] = data['parent']













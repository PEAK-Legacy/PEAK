from peak.api import *
from interfaces import *
from places import Location
from peak.util.imports import lazyModule
from peak.util import SOX

def isRoot(data):
    return 'previous' not in data

def acquire(data,key,default=None):
    """Find 'key' in 'data' or its predecessors"""
    while data is not None:
        if key in data:
            return data[key]
        data = data.get('previous')
    else:
        return default
    
def finishComponent(parser,data):
    if 'sm.component' in data:
        return data['sm.component']

def getGlobals(data):
    return data.setdefault('sm_globals',acquire(data,'sm_globals').copy())

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
    return acquire(data,'sm.permission',security.Anybody)

def acquireHelper(data,attrs):
    if 'helper' in attrs:
        helper = data['sm.helper'] = evalObject(data,attrs['helper'])
        return helper
    return acquire(data,'sm.helper')

def assertOutsideContent(parser,data):
    content = acquire(data,'sm.content_type',NOT_GIVEN)
    if content is not NOT_GIVEN:
        parser.err(
            "%(name)r element cannot be nested inside 'content' block" % data
        )

def choose(parser, names, attrs):

    found = False

    for name in names:
        if name in attrs:
            if found:
                break
            found = True
            result = name,attrs[name]
    else:
        if found:
            return result

    parser.err(
        "Element must include *exactly* one of these attributes: "
        + ', '.join(names)
    )            




def addPermission(handler,permission):
    def guarded_handler(ctx, ob, namespace, name, qname, default=NOT_GIVEN):
        ctx.requireAccess(qname,ob,permissionNeeded=permission)
        return handler(ctx, ob, namespace, name, qname, default)
    return guarded_handler

def addHelper(handler,helper):
    def helped_handler(ctx, ob, namespace, name, qname, default=NOT_GIVEN):
        return handler(ctx, helper(ob), namespace, name, qname, default)
    return helped_handler

def attributeView(attr):
    from environ import traverseAttr
    def handler(ctx, ob, namespace, name, qname, default=NOT_GIVEN):
        loc = getattr(ob, attr, NOT_FOUND)
        if loc is not NOT_FOUND:
            return ctx.childContext(qname,loc)
        if default is NOT_GIVEN:
            raise web.NotFound(ctx,qname,ob)
        return default
    return handler
    
def objectView(target):
    def handler(ctx, ob, namespace, name, qname, default=NOT_GIVEN):
        return ctx.childContext(qname,target)
    return handler

def resourceView(path):
    def handler(ctx, ob, namespace, name, qname, default=NOT_GIVEN):
        return ctx.childContext(qname,ctx.getResource(path))
    return handler

def locationView(spec):
    keyPath,locId = str(spec).split('@',1)
    locId = '++id++'+locId
    def handler(ctx, ob, namespace, name, qname, default=NOT_GIVEN):
        path = str(ctx.clone(current=ob).traverseName(keyPath).current)
        base = ctx.traverseName(locId).absoluteURL     
        return ctx.childContext(qname,base+'/'[:not base.endswith('/')]+path)
    return handler

def registerView(name,handler,data,attrs):
    perm = acquirePermission(data,attrs)
    helper = acquireHelper(data,attrs)
    loc = acquire(data,'sm.component')
    typ = acquire(data,'sm.content_type')

    if helper is not None:
        handler = addHelper(handler,helper)

    if perm is not security.Anybody:
        handler = addPermission(handler,perm)

    #if typ is None:
    #    pass # XXX register direct w/location?
    loc.registerView(typ,str(name),handler)


def doAllow(parser,data):
    attrs = SOX.validatedAttributes(
        parser,data,('attributes',),('permission','helper')
    )        

    for attr in attrs['attributes'].split(','):
        registerView(attr,attributeView(attr.strip()),data,attrs)


def defineAllow(parser,data):
    assertNotTop(parser,data)    #assertInsideContent(parser,data)?
    data['start'] = doAllow
    data['empty'] = True











locRequired = ()
locOptional = 'name','class','id','permission', 'extends', 'config'

def makeLocation(parser,data,attrs,parent,name):

    if 'extends' in attrs:
        factory = naming.lookup(parent,
            naming.parseURL(parent, attrs['extends'], parser._url)
        )
        return config.processXML(
            web.SITEMAP_SCHEMA(parent),
            relativeResource(parser,attrs['extends'],parent),
            parent=parent, sm_included_from=attrs, sm_globals=globals(), #XXX
        )

    if 'class' in attrs:
        return evalObject(data,attrs['class'])(parent,name)

    return Location(parent,name)
    

def relativeResource(parser, attr, parent):
    return naming.lookup(parent,
        # Might be a relative URL, so parse w/parser URL as base
        naming.parseURL(parent, attr, parser._url)
    )
    














def startLocation(parser,data):
    attrs = SOX.validatedAttributes(parser,data,locRequired,locOptional)
    acquirePermission(data,attrs)
    prev = findComponentData(data)
    parent = prev['sm.component']
    name = attrs.get('name')

    if isRoot(prev):
        if name is not None:
            parser.err("Root location cannot have a 'name'")

        if 'sm_included_from' in prev:
            inclattrs = prev['sm_included_from']
            name = inclattrs.get('name')
            if 'class' in inclattrs:
                attrs['class'] = inclattrs['class']
    elif not name:
        parser.err("Non-root locations must have a 'name'")

    loc = makeLocation(parser,data,attrs,parent,name)
    if 'id' in attrs:
        loc.registerLocation(str(attrs['id']),'.')
    if 'config' in attrs:
        config.loadConfigFile(
            loc,relativeResource(parser,attrs['config'],parent)
        )
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


content_req = ('type',)
content_opt = ('permission','helper','location')

def doContent(parser,data):
    attrs = SOX.validatedAttributes(parser,data,content_req,content_opt)
    acquirePermission(data,attrs)
    acquireHelper(data,attrs)
    data['sm.content_type'] = evalObject(data,attrs['type'])
    if 'location' in attrs:
        registerView(
            'peak.web.url',locationView(attrs['location']),data,attrs
        )

def defineContent(parser,data):
    assertNotTop(parser,data)
    assertOutsideContent(parser,data)
    data['start'] = doContent

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
    assertOutsideContent(parser,data)
    data['start'] = doContainer
    data['empty'] = True

view_required = 'name',
view_one_of   = 'resource','attribute','object', 'function', 'expr'
view_optional = view_one_of + ('permission','helper')

def doView(parser,data):
    attrs = SOX.validatedAttributes(parser,data,view_required,view_optional)

    mode,expr = choose(parser,view_one_of,attrs)
    if mode=='object':
        handler = objectView(evalObject(data,expr))
    elif mode=='function':
        handler = evalObject(data,expr)
    elif mode=='expr':
        g = getGlobals(data['previous'])
        def handler(ctx, ob, namespace, name, qname, default=NOT_GIVEN):
            return ctx.childContext(qname, eval(expr,locals(),g))
    elif mode=='attribute':
        handler = attributeView(expr)
    elif mode=='resource':
        handler = resourceView(expr)

    registerView(attrs['name'],handler,data,attrs)
    

def defineView(parser,data):
    assertNotTop(parser,data)
    data['start'] = doView
    data['empty'] = True













def doOffer(parser,data):
    attrs = SOX.validatedAttributes(parser,data,('path','as',))
    prev = findComponentData(data)
    prev['sm.component'].registerLocation(attrs['as'],attrs['path'])

def defineOffer(parser,data):
    assertNotTop(parser,data)
    assertOutsideContent(parser,data)
    data['start'] = doOffer
    data['empty'] = True


def doRequire(parser,data):
    attrs = SOX.validatedAttributes(parser,data,('permission',),('helper',))
    acquirePermission(data,attrs)
    acquireHelper(data,attrs)

def defineRequire(parser,data):
    assertNotTop(parser,data)
    data['start'] = doRequire


def setupDocument(parser,data):

    def setRoot(ob):
        data['sm.component'] = ob

    data['child'] = setRoot
    data['finish'] = finishComponent
    data['sm.component'] = data['parent']

class SiteMap(binding.Singleton):
    protocols.advise(classProvides=[naming.IObjectFactory])
    def getObjectInstance(klass, context, refInfo, name, attrs=None):
        url, = refInfo.addresses
        return config.processXML(
            web.SITEMAP_SCHEMA(context), str(url),
            parent=context, sm_globals=globals(), #XXX
        )



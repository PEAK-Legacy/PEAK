from __future__ import generators
from peak.api import *
from interfaces import *
from places import Traversable
from publish import TraversalPath
from templates import TemplateDocument
from peak.naming.factories.openable import FileURL
from peak.util.imports import importString
import os.path, posixpath, sys
from errors import UnsupportedMethod, NotFound, NotAllowed
from environ import clientHas, traverseItem
from urlparse import urljoin

__all__ = [
    'Resource', 'FSResource', 'ResourceDirectory', 'FileResource',
    'ImageResource', 'DefaultLayer', 'bindResource', 'TemplateResource',
]

RESOURCE_BASE     = 'peak.web.file_resource.'
RESOURCE_DEFAULTS = PropertyName('peak.web.resourceDefaultsIni')
RESOURCE_CONFIG   = PropertyName('peak.web.resourceConfigFile')
FILE_FACTORY      = PropertyName('peak.web.file_resources.file_factory')
DIR_FACTORY       = PropertyName('peak.web.file_resources.dir_factory')
RESOURCE_VISIBLE  = PropertyName('peak.web.file_resources.visible')
ALLOWED_PACKAGES  = PropertyName('peak.web.resource_packages')
PACKAGE_FACTORY   = PropertyName('peak.web.packageResourceFactory')
PERMISSION_NS     = PropertyName(RESOURCE_BASE+'permission')
MIMETYPE_NS       = PropertyName(RESOURCE_BASE+'mime_type')

def filenameAsProperty(name):
    """Convert a filename (base, no path) into a usable property name"""
    parts = filter(None,name.split('.'))
    parts.reverse()
    return PropertyName.fromString('.'.join(parts), keep_wildcards=True)

def parseFileResource(parser, section, name, value, lineInfo):
    """Handle a line from a [Files *.foo] section"""
    prefix = PropertyName('peak.web.file_resources.'+name).asPrefix()
    for pattern in section.split()[1:]:
        parser.add_setting(prefix,filenameAsProperty(pattern),value,lineInfo)

class Resource(Traversable):

    protocols.advise(
        instancesProvide = [IPlace]
    )

    permissionNeeded = binding.Require("Permission needed for access")


    def preTraverse(self, ctx):
        perm = self.permissionNeeded
        ctx.requireAccess('', self, permissionNeeded=perm)
        return ctx


    def getURL(self, ctx):
        # Root-relative URL
        base = ctx.rootURL+'/'[ctx.rootURL.endswith('/'):]
        return urljoin(base,self.place_url)


    def _getResourcePath(self):
        name = self.getComponentName()
        if name is None:
            # We must be the root, unless it's an error
            return ''

        base = IPlace(self.getParentComponent(),None)
        if base is not None:
            if name:
                return posixpath.join(base.place_url, name)
            else:
                return base.place_url

        return name

    place_url = binding.Make(_getResourcePath)




class FSResource(Resource):

    protocols.advise(
        classProvides=[naming.IObjectFactory],
    )

    security.allow(security.Anybody, basename=security.Anybody) # XXX

    filename = binding.Require("OS-specific full filename")

    filenameAsProperty = binding.Make(
        lambda self: filenameAsProperty(self.basename)
    )

    permissionNeeded = binding.Make(
        lambda self: PERMISSION_NS.of(self)[self.filenameAsProperty]
    )

    mime_type = binding.Make(
        lambda self: MIMETYPE_NS.of(self)[self.filenameAsProperty]
    )

    def getObjectInstance(klass, context, refInfo, name, attrs=None):
        url, = refInfo.addresses
        url = naming.parseURL(context, url)
        return klass(filename = url.getFilename())

    getObjectInstance = classmethod(getObjectInstance)

    basename = binding.Make(lambda self: os.path.basename(self.filename))











class ResourceDirectory(FSResource, binding.Configurable):

    isRoot = False      # Are we the topmost FSResource here?

    cache = binding.Make(dict)

    def __onSetup(self,d,a):

        if self.isRoot:
            # default permissionNeeded to Anybody
            if not self._hasBinding('permissionNeeded'):
                self.permissionNeeded = security.Anybody

            # load resource_defaults.ini
            config.loadConfigFile(self, RESOURCE_DEFAULTS(self))

        # load resources.ini, if found
        config.loadConfigFiles(self,
            [os.path.join(self.filename, RESOURCE_CONFIG(self))]
        )

    __onSetup = binding.Make(__onSetup, uponAssembly=True)


    def filenames(self):    # XXX need a way to invalidate this!
        nms = {}
        for filename in os.listdir(self.filename):
            if filename in ('.','..'):
                continue
            parts = filename.split('.')
            for i in range(1,len(parts)+1):
                nms.setdefault('.'.join(parts[:i]),[]).append(filename)
        return nms

    filenames = binding.Make(filenames)


    def getURL(self, ctx):
        return Resource.getURL(self,ctx)+'/'   # avoid unnecessary redirects


    def __getitem__(self,name):
        targets = self.filenames.get(name,())
        if len(targets)<1:
            # <1 means no match
            raise KeyError,name
        elif len(targets)>1 and name not in targets:
            # >1 and name isn't in there, it's ambiguous
            raise KeyError,name

        if name in self.cache:
            result = self.cache[name]
            if result is NOT_FOUND:
                raise KeyError,name
            return result

        if name in targets:
            filename = name
        else:
            filename, = targets

        # XXX warn if name is overspecified
        prop = filenameAsProperty(filename)
        # check if name is visible; if false, drop it
        if not RESOURCE_VISIBLE.of(self)[prop]:
            self.cache[name] = NOT_FOUND
            raise KeyError,name

        # look up factory for name
        path = os.path.join(self.filename, filename)
        if os.path.isdir(path):
            factory = DIR_FACTORY.of(self)[prop]
        else:
            factory = FILE_FACTORY.of(self)[prop]

        # create a reference, and dereference it
        ref = naming.Reference(factory, addresses=[FileURL.fromFilename(path)])
        obj = ref.restore(self,None)
        obj.setParentComponent(self, filename)
        self.cache[name] = obj
        return obj

def findPackage(pkg):

    """Find containing package (module w/'__path__') for module named 'pkg'"""

    mod = importString(pkg)

    while not hasattr(mod,'__path__') and '.' in pkg:
        pkg = '.'.join(pkg.split('.')[:-1])
        mod = importString(pkg)

    return pkg, mod


class ResourceProxy(object):

    __slots__ = 'path'

    protocols.advise(instancesProvide = [IHTTPHandler, IWebTraversable])

    def __init__(self, path):
        self.path = path

    def handle_http(self, ctx):
        return IHTTPHandler(ctx.getResource(self.path)).handle_http(ctx)

    def preTraverse(self, ctx):
        return IWebTraversable(ctx.getResource(self.path)).preTraverse(ctx)

    def traverseTo(self, name, ctx):
        return IWebTraversable(ctx.getResource(self.path)).traverseTo(name,ctx)

    def getURL(self,ctx):
        return IWebTraversable(ctx.getResource(self.path)).getURL(ctx)








def bindResource(path, pkg=None, **kw):

    """Attribute binding to look up a resource"""

    kw.setdefault('suggestParent',False)

    path = adapt(path, TraversalPath)

    if not str(path).startswith('/'):

        if pkg is None:
            pkg = sys._getframe(1).f_globals['__name__']
            pkg, module = findPackage(pkg)

        # /package/whatever
        path = TraversalPath('/'+pkg) + path

    proxy = ResourceProxy(path)
    return binding.Make(lambda: proxy, **kw)






















class DefaultLayer(Resource):

    cache = fileCache = binding.Make(dict)
    permissionNeeded = security.Anybody

    def traverseTo(self, name, ctx):
        if name in self.cache:
            result = self.cache[name]
            if result is NOT_FOUND:
                raise NotFound(ctx,name)
            return ctx.childContext(name,result)

        # convert name to a property name
        name = PropertyName.fromString(name)

        # look it up in allowed-packages namespace
        ok = ALLOWED_PACKAGES.of(self).get(name,None)
        if not ok:
            self.cache[name]=NOT_FOUND
            raise NotFound(ctx,name)

        try:
            pkg, mod = findPackage(name)
        except ImportError:
            self.cache[name] = NOT_FOUND
            raise NotFound(ctx,name)
        else:
            filename = os.path.dirname(mod.__file__)
            if filename in self.fileCache:
                d = self.fileCache[filename]
            else:
                d = PACKAGE_FACTORY(self)(
                    self, pkg, filename=filename, isRoot=True
                )
                self.fileCache[filename] = d

        # cache and return it
        self.cache[name] = self.cache[pkg] = d
        return ctx.childContext(name,d)


class TemplateResource(FSResource):

    """Template used as a method (via 'bindResource()')"""

    protocols.advise(
        instancesProvide = [IHTTPHandler]
    )

    def handle_http(self, ctx):
        name = ctx.shift()
        if name is not None:
            raise NotFound(ctx,name,self)   # No traversal to subobjects!
        s,h,b = IHTTPHandler(self.theTemplate).handle_http(ctx)
        # XXX replace content-type header w/self.mime_type
        return s,h,b

    def preTraverse(self, ctx):
        # Templates may not be accessed directly via URL!
        raise NotFound(ctx,name)

    def theTemplate(self):
        """Load and parse the template on demand"""

        doc = TemplateDocument(self,None)
        stream = open(self.filename, 'rt')

        try:
            doc.parseFile(stream)
        finally:
            stream.close()
        return doc

    theTemplate = binding.Make(theTemplate)

    def traverseTo(self, name, ctx):
        return IWebTraversable(self.theTemplate).traverseTo(name, ctx)

    def getURL(self, ctx):
        # We're a method, so use our context URL, not container URL
        return ctx.traversedURL

class FileResource(FSResource):

    protocols.advise( instancesProvide = [IHTTPHandler] )

    lastModified = None
    ETag         = None
    blocksize    = 16384

    def getStreamAndSize(self):
        return open(self.filename, 'rb'), os.stat(self.filename).st_size

    def handle_http(self, ctx):
        name = ctx.shift()
        if name is not None:
            raise NotFound(ctx,name,self)   # No traversal to subobjects!

        method = ctx.environ['REQUEST_METHOD'].upper()

        if method not in ('GET','HEAD'):
            raise UnsupportedMethod(ctx)

        if clientHas(self.lastModified, self.ETag):
            return '304 Not Modified',[],[]     # XXX test this

        stream, size = self.getStreamAndSize()

        def dump_data():
            if method=='GET':   # HEAD doesn't need the data
                size = self.blocksize
                while 1:
                    data = stream.read(size)
                    if not data: break
                    yield data
            stream.close()

        headers = [('Content-Length', str(size))]
        if self.mime_type:
            headers.append(('Content-Type', self.mime_type))
        return '200 OK', headers,  dump_data()


class ImageResource(FileResource):
    pass








































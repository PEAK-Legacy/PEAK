from peak.api import *
from interfaces import *
from places import Traversable
from publish import TraversalPath
from templates import DOMletAsWebPage, TemplateDocument
from peak.naming.factories.openable import FileURL
from peak.util.imports import importString
import os.path, posixpath, sys
from errors import UnsupportedMethod

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

ALLOWED_PACKAGES = PropertyName('peak.web.resource_packages')
PACKAGE_FACTORY  = PropertyName('peak.web.packageResourceFactory')


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
        instancesProvide = [IResource]
    )

    permissionsNeeded = binding.requireBinding("Permissions needed for access")

    def preTraverse(self, ctx):
        perms = self.permissionsNeeded
        if not ctx.interaction.allows(self, permissionsNeeded = perms):
            ctx.interaction.notAllowed(self, self.getComponentName())

    def traverseTo(self, name, interaction):
        return NOT_FOUND


    def getURL(self, ctx):
        # We want an absolute URL based on the interaction
        return ctx.interaction.getAbsoluteURL(self)


    def _getResourcePath(self, d, a):

        name = self.getComponentName()

        if name:
            base = self.getParentComponent().resourcePath
            return posixpath.join(base, name)   # handles empty parts OK

        raise ValueError("Traversable was not assigned a name", self)

    resourcePath = binding.Once(_getResourcePath)








class FSResource(Resource):

    protocols.advise(
        classProvides=[naming.IObjectFactory],
    )

    filename = binding.requireBinding("OS-specific full filename")

    filenameAsProperty = binding.Once(
        lambda self,d,a: filenameAsProperty(os.path.basename(self.filename))
    )

    permissionsNeeded = binding.bindToProperty(RESOURCE_BASE+'permissions')
    mime_type         = binding.bindToProperty(RESOURCE_BASE+'mime_type')

    def getObjectInstance(klass, context, refInfo, name, attrs=None):
        url, = refInfo.addresses
        url = naming.parseURL(context, url)
        return klass(filename = url.getFilename())

    getObjectInstance = classmethod(getObjectInstance)




















class ResourceDirectory(FSResource):

    isRoot = False      # Are we the topmost FSResource here?
    includeURL = False  # Include our name in URL even if we're a root
    cache = binding.New(dict)

    def __onSetup(self,d,a):

        if self.isRoot:
            if not self._hasBinding('permissionsNeeded'):
                self.permissionsNeeded = [security.Anybody]
            # load resource_defaults.ini
            config.loadConfigFile(self, RESOURCE_DEFAULTS(self))

            # default permissionsNeeded to Anybody

        # load resources.ini, if found
        config.loadConfigFiles(self,
            [os.path.join(self.filename, RESOURCE_CONFIG(self))]
        )

    __onSetup = binding.whenAssembled(__onSetup)


    def filenames(self,d,a):    # XXX need a way to invalidate this!
        nms = {}
        for filename in os.listdir(self.filename):
            if filename in ('.','..'):
                continue
            parts = filename.split('.')
            for i in range(1,len(parts)+1):
                nms.setdefault('.'.join(parts[:i]),[]).append(filename)
        return nms

    filenames = binding.Once(filenames)






    def traverseTo(self, name, interaction):

        targets = self.filenames.get(name,())

        if len(targets)<1:
            # <1 means no match
            return NOT_FOUND
        elif len(targets)>1 and name not in targets:
            # >1 and name isn't in there, it's ambiguous
            return NOT_FOUND

        if name in self.cache:
            return self.cache[name]

        if name in targets:
            filename = name
        else:
            filename, = targets

        # XXX warn if name is overspecified
        prop = filenameAsProperty(filename)

        # check if name is visible; if false, drop it
        if not RESOURCE_VISIBLE.of(self)[prop]:
            self.cache[name] = NOT_FOUND
            return NOT_FOUND

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
        self.cache[name] = obj = adapt(obj,interaction.pathProtocol)    #XXX
        return obj

    def resourcePath(self,d,a):

        if self.isRoot and not self.includeURL:
            # Our name doesn't count in the URL
            return self.getParentComponent().resourcePath

        # use original definition
        return self._getResourcePath(d,a)

    resourcePath = binding.Once(resourcePath)































def findPackage(pkg):

    """Find containing package (module w/'__path__') for module named 'pkg'"""

    mod = importString(pkg)

    while not hasattr(mod,'__path__') and '.' in pkg:
        pkg = '.'.join(pkg.split('.')[:-1])
        mod = importString(pkg)

    return pkg, mod


class ResourceProxy(object):

    __slots__ = 'path', 'resourcePath'

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    def __init__(self, path, resourcePath):
        self.path = path
        self.resourcePath = resourcePath

    def getObject(self, interaction):
        return interaction.skin.getResource(self.path)

    def preTraverse(self, ctx):
        self.getObject(ctx.interaction).preTraverse(ctx)

    def traverseTo(self, name, interaction):
        ob = adapt(self.getObject(interaction),interaction.pathProtocol)
        return ob.traverseTo(name, interaction)

    def getURL(self,ctx):
        return self.getObject(ctx.interaction).getURL(ctx)




def bindResource(path, pkg=None, **kw):

    """Attribute binding to look up a resource"""

    path = adapt(path, TraversalPath)

    if not str(path).startswith('/'):

        if pkg is None:
            pkg = sys._getframe(1).f_globals['__name__']
            pkg, module = findPackage(pkg)

        # /package/whatever
        path = TraversalPath('/'+pkg) + path

    def getResource(self, d, a):
        return ResourceProxy(path, RESOURCE_PREFIX(self)+'/'+str(path))

    kw.setdefault('suggestParent',False)
    return binding.Once(getResource, **kw)





















class DefaultLayer(Traversable):

    cache = fileCache = binding.New(dict)

    def traverseTo(self, name, interaction):

        if name in self.cache:
            return self.cache[name]

        # convert name to a property name
        name = PropertyName.fromString(name)

        # look it up in allowed-packages namespace
        ok = ALLOWED_PACKAGES.of(self).get(name,None)
        if not ok:
            self.cache[name]=NOT_FOUND
            return NOT_FOUND

        try:
            pkg, mod = findPackage(name)
        except ImportError:
            d = NOT_FOUND
        else:
            filename = os.path.dirname(mod.__file__)

            if filename in self.fileCache:
                d = self.fileCache[filename]
            else:
                d = PACKAGE_FACTORY(self)(
                    self, pkg, filename=filename, isRoot=True, includeURL=True
                )
                self.fileCache[filename] = d

        # cache and return it
        self.cache[name] = self.cache[pkg] = d
        return d

    # Our name doesn't count in the URL
    resourcePath = binding.bindTo('../resourcePath')


class TemplateResource(FSResource):

    """Template used as a method (via 'bindResource()')"""

    def preTraverse(self, ctx):
        # Templates may not be accessed directly via URL!
        ctx.interaction.notFound(self, self.getComponentName())


    def theTemplate(self,d,a):

        """Load and parse the template on demand"""

        doc = TemplateDocument(self,None)
        stream = open(self.filename, 'rt')

        try:
            doc.parseFile(stream)
        finally:
            stream.close()
        return doc

    theTemplate = binding.Once(theTemplate)


    def getObject(self, interaction):
        return self.theTemplate

    def getURL(self, ctx):
        # We're a method, so use our context URL, not container URL
        return ctx.traversedURL










class FileResource(FSResource):

    protocols.advise(
        instancesProvide = [IWebPage]
    )

    lastModified = None
    ETag         = None
    blocksize    = 16384

    def render(self, ctx):
        interaction = ctx.interaction
        response = interaction.response

        if not interaction.request.method in ('GET','HEAD'):
            raise UnsupportedMethod(ctx)

        if interaction.clientHas(self.lastModified, self.ETag):
            return response

        # Set response mimetype (wait till now, or above would be corrupted)
        size = os.stat(self.filename).st_size
        response.setHeader('Content-Type', self.mime_type)
        response.setHeader('Content-Length', str(size))

        if interaction.request.method == 'GET':
            write = response.write
            size = self.blocksize
            stream = open(self.filename, 'rb')
            try:
                # read/write data in size-N blocks
                while 1:
                    data = stream.read(size)
                    if not data: break
                    write(data)
            finally:
                stream.close()

        return response


class ImageResource(FileResource):
    pass








































from peak.api import *
from peak.naming import URL

justPath = URL.Sequence(
    URL.MatchString(), ':',
    ('//', URL.MatchString(pattern='[^/]*')),
    URL.Named('path'),
    ('?', URL.MatchString()), ('#', URL.MatchString()),
)

def pathFromURL(url):
    return URL.parse(str(url),justPath)['path']





























class GenericPathURL(URL.Base):

    nameAttr = 'path'
    supportedSchemes = 'http','https','ftp','file',

    class user(URL.Field): pass
    class password(URL.Field): pass

    class hostname(URL.Field):
        defaultValue = ''
        syntax = URL.Conversion(
            URL.ExtractQuoted(URL.MatchString(pattern='[^/:]*')),
            canBeEmpty = True
        )

    class port(URL.IntField): pass

    class path(URL.NameField):
        referencedType = naming.CompositeName
        canBeEmpty = True

    class query(URL.Field): pass

    class fragment(URL.Field): pass

    # Make syntax usable w/subclasses that redefine individual fields

    syntax = binding.classAttr(
        binding.Once(
            lambda s,d,a: URL.Sequence(
                '//',
                ( (s.user, (':',s.password) ,'@'), s.hostname, (':',s.port)),
                '/', s.path, ('?',s.query), ('#',s.fragment)
            )
        )
    )





class OpenableURL(GenericPathURL):

    protocols.advise(
        instancesProvide = [ naming.IStreamAddress ]
    )

    def retrieve(self, refInfo, name, context, attrs=None):
        return URLStreamFactory(target = str(self))


class FileURL(OpenableURL):

    supportedSchemes = 'file',

    # Make syntax usable w/subclasses that redefine individual fields
    syntax = binding.classAttr(
        binding.Once(
            lambda s,d,a: URL.Sequence(
                URL.Alternatives(
                    URL.Sequence('//', s.hostname, s.path),
                    s.path,
                ), ('?', s.querySyntax), ('#', s.fragment),
            )
        )
    )

    querySyntax = GenericPathURL.query._syntax

    def getFilename(self):
        # We need to normalize ourself to match urllib's funky
        # conventions for file: conversion.  :(
        from urllib import url2pathname
        return url2pathname(pathFromURL(self))


    def retrieve(self, refInfo, name, context, attrs=None):
        return FileFactory( filename = self.getFilename() )




class PkgFileURL(URL.Base):

    protocols.advise(
        instancesProvide = [ naming.IStreamAddress ]
    )

    nameAttr = 'body'

    supportedSchemes = 'pkgfile',

    class body(URL.NameField):
        referencedType = naming.CompositeName
        canBeEmpty = True

    def getFilename(self):
        if len(self.body)<2 or not self.body[0]:
            raise exceptions.InvalidName(
                "Missing package name in %s" % self
            )
        from os.path import join, dirname
        from peak.util.imports import importString
        path = dirname(importString(self.body[0]).__file__)
        for p in self.body[1:]:
            path = join(path,p)
        return path

    def retrieve(self, refInfo, name, context, attrs=None):
        return FileFactory( filename = self.getFilename() )













class URLStreamFactory(binding.Component):

    """Stream factory for a 'urllib2.urlopen()'

    This is a pretty lame duck right now.  It's mainly here so we have a
    consistent interface across file-like URLs."""

    protocols.advise(
        instancesProvide=[naming.IStreamFactory]
    )

    target = binding.requireBinding("urllib2 URL or request", "target")


    def open(self,mode,seek=False,writable=False,autocommit=False):

        if writable:
            raise TypeError("URL not writable", self.target)

        if mode<>'b':
            raise TypeError("URL requires binary read mode", self.target)

        if seek:
            raise TypeError("URL not seekable", self.target)

        from urllib2 import urlopen
        return urlopen(str(self.target))


    def create(self,mode,seek=False,readable=False,autocommit=False):
        raise TypeError("Can't create URL", self.target)


    def update(self,mode,seek=False,readable=False,append=False,autocommit=False):
        raise TypeError("Can't update URL", self.target)

    def delete(self, autocommit=False):
        raise TypeError("Can't delete URL", self.target)



    def exists(self):

        from urllib2 import urlopen, HTTPError

        try:
            urlopen(self.target).close()
        except (HTTPError,IOError):
            return False
        else:
            return True































class FileFactory(binding.Component):

    """Stream factory for a local file object"""

    protocols.advise(
        instancesProvide=[naming.IStreamFactory]
    )

    filename = binding.requireBinding("Filename to open/modify", "filename")


    def open(self,mode,seek=False,writable=False,autocommit=False):
        return self._open(mode, 'r'+(writable and '+' or ''), autocommit)

    def create(self,mode,seek=False,readable=False,autocommit=False):
        return self._open(mode, 'w'+(readable and '+' or ''), autocommit)

    def update(self,mode,seek=False,readable=False,append=False,autocommit=False):
        return self._open(mode, 'a'+(readable and '+' or ''), autocommit)

    def exists(self):
        from os.path import exists
        return exists(self.filename)


    def _open(self, mode, flags, ac):

        if mode not in ('t','b','U'):
            raise TypeError("Invalid open mode:", mode)

        if not ac and flags<>'r':
            raise TypeError("Files require autocommit for write operations ")

        return open(self.filename, flags+mode)


    # XXX def delete(self,autocommit=False):
    # XXX def move(self, other, overwrite=True, autocommit=False):




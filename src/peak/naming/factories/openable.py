from peak.api import *
from peak.naming import URL

class GenericPathURL(URL.Base):

    nameAttr = 'path'
    supportedSchemes = 'http','https','ftp','file',

    class user(URL.Field): pass
    class password(URL.Field): pass

    class hostname(URL.Field):
        defaultValue = None
        syntax = URL.Conversion(
            URL.ExtractQuoted(URL.MatchString(pattern='[^/:]*')),
            defaultValue = None
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
    pass

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
        return url2pathname(str(self.path))


    def fromFilename(klass, aName):
        m = naming.URLMatch(aName)
        if m:
            return klass(m.group(1), aName[m.end():])
        else:
            from os.path import abspath
            from urllib import pathname2url
            return klass(None, pathname2url(abspath(aName)))

    fromFilename = classmethod(fromFilename)



class PkgFileURL(URL.Base):

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




















class URLStreamFactory(binding.Component):

    """Stream factory for a 'urllib2.urlopen()'

    This is a pretty lame duck right now.  It's mainly here so we have a
    consistent interface across file-like URLs."""

    protocols.advise(
        instancesProvide=[naming.IStreamFactory],
        asAdapterForTypes=[OpenableURL],
        factoryMethod = 'adaptFromURL',
    )

    target = binding.requireBinding("urllib2 URL or request")


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


    def adaptFromURL(klass, url, protocol):
        return klass(target = str(url))

    adaptFromURL = classmethod(adaptFromURL)

























class FileFactory(binding.Component):

    """Stream factory for a local file object"""

    protocols.advise(
        instancesProvide=[naming.IStreamFactory],
        asAdapterForTypes=[FileURL, PkgFileURL],
        factoryMethod = 'adaptFromURL',
    )

    filename = binding.requireBinding("Filename to open/modify")


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

    def adaptFromURL(klass, url, protocol):
        return klass(filename = url.getFilename())

    adaptFromURL = classmethod(adaptFromURL)






































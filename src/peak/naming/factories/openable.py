# XXX This is VERY rough...  :(

from peak.api import *


class OpenableURL(naming.URL.Base):

    def retrieve(self, refInfo, name, context, attrs=None):
        return URLStreamFactory(target = str(self))


class FileURL(naming.URL.Base):

    # XXX needs parser for //user:auth@host:port/path?query#frag
    # XXX could then be shared with URLs for http, ftp, https...
    # XXX Probably path portion needs to be manipulable as

    def retrieve(self, refInfo, name, context, attrs=None):
        return FileFactory(filename = urlToLocalFile(self))


def urlToLocalFile(url):

    path = url.body

    if path.startswith('//'):
        # XXX need to translate '/' into local 'os.sep'?
        return path[2:].split('/',1)[1]

    return path











class URLStreamFactory(binding.Component):

    """Stream factory for a 'urllib2.urlopen()'

    This is a pretty lame duck right now.  It's mainly here so we have a
    consistent interface across file-like URLs."""

    __implements__ = naming.IStreamFactory

    target = binding.requireBinding("urllib2 URL or request", "target")


    def open(self,mode,seek=False,writable=False,autocommit=False):

        if writable:
            raise TypeError("URL not writable", self.target)

        if mode<>'b':
            raise TypeError("URL requires binary read mode", self.target)

        if seek:
            raise TypeError("URL not seekable", self.target)

        from urllib2 import urlopen
        return urlopen(self.target)


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

    __implements__ = naming.IStreamFactory


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





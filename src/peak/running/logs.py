'''TODO:

    * Flesh out ILogSink (__call__), ILogEvent, and docs here and in peak.api

    * SysLog and LogTee objects/URLs (low priority; we don't seem to use
      these at the moment)
'''

from peak.binding.components import Component, Once, New, requireBinding
from peak.naming.names import ParsedURL
from peak.interface import implements, Interface
from peak.api import NOT_GIVEN

from interfaces import ILogger

from time import time, localtime, strftime
import sys, os, traceback

from socket import gethostname
_hostname = gethostname().split('.')[0]
del gethostname


__all__ = [
    'getLevelName', 'getLevelFor', 'addLevelName', 'Event', 'logfileURL',
    'AbstractLogger', 'LogFile', 'LogStream', 'loggerURL', 'peakLoggerURL',
]














def addLevelName(lvl,name):

    """Define 'name' for 'lvl'; fails if 'name' already in use"""

    if name in nameToLevel and nameToLevel[name]<>lvl:
        raise ValueError("Level already defined",name,nameToLevel[name])

    nameToLevel[name]=lvl

    if logging:
        logging.addLevelName(lvl,name)

    return levelToName.setdefault(lvl,name)


def getLevelName(lvl, default=NOT_GIVEN):

    """Get a name for 'lvl', or return 'default'

    If 'default' is not given, this returns '"Level %s" % lvl', for
    symmetry with the 'logging' package."""

    try:
        return levelToName[lvl]

    except KeyError:
        std = "Level %s" % lvl

        if logging:
            name = logging.getLevelName(lvl)
            if name <> std:
                addLevelName(lvl,name)
                return name

    if default is NOT_GIVEN:
        return std

    return default



def getLevelFor(ob, default=NOT_GIVEN):

    """Get a level integer for 'ob', or return 'default'

    If 'ob' is in fact a number (i.e. adding 0 to it works), it will be
    returned as-is.  If 'ob' is a string representation of an integer, its
    numeric value is returned.  This is so that functions which want to accept
    either numbers or level names can do so by calling this converter.

    If no conversion can be found, and no default is specified, LookupError
    is raised."""

    try:
        return ob+0     # If this works, it's a number, leave it alone
    except TypeError:
        pass

    try:
        return nameToLevel[ob]

    except KeyError:
        std = "Level %s" % ob

        if logging:
            lvl = logging.getLevelName(ob)
            if lvl <> std:
                addLevelName(lvl,ob)
                return lvl

    try:
        # See if we can convert it to a number
        return int(ob)
    except ValueError:
        pass

    if default is NOT_GIVEN:
        raise LookupError("No such log level", ob)

    return default


try:
    import logging
except ImportError:
    logging = None

if logging:
    # Add the other syslog levels
    logging.addLevelName(25, 'NOTICE')
    logging.addLevelName(60, 'ALERT')
    logging.addLevelName(70, 'EMERG')


nms  = 'TRACE ALL DEBUG INFO NOTICE WARNING ERROR CRITICAL ALERT EMERG'.split()
lvls =      0,  0,   10,  20,    25,     30,   40,      50,   60,   70

levelToName = dict(zip(lvls,nms))
nameToLevel = dict(zip(nms,lvls))

globals().update(nameToLevel)

__all__.extend(nms)




















class Event(Component):

    ident      = 'PEAK' # XXX use component names if avail?
    message    = ''
    priority   = TRACE
    timestamp  = Once(lambda *x: time())
    uuid       = New('peak.util.uuid:UUID')
    hostname   = _hostname
    process_id = Once(lambda *x: os.getpid())
    exc_info   = ()

    def traceback(self,d,a):
        if self.exc_info:
            return ''.join(traceback.format_exception(*self.exc_info))
        return ''

    traceback = Once(traceback)

    def __init__(self, message, parent=None, **info):

        super(Event,self).__init__(parent,**info)
        self.message = message

        if not isinstance(self.exc_info, tuple):
            self.exc_info = sys.exc_info()

    def keys(self):
        return [k for k in self.__dict__.keys() if not k.startswith('_')]

    def items(self):
        return [
            (k,v) for k,v in self.__dict__.items() if not k.startswith('_')
        ]

    def __contains__(self, key):
        return not key.startswith('_') and key in self.__dict__

    def __getitem__(self, key):
        return getattr(self,key)


    def linePrefix(self,d,a):
        return  "%s %s %s[%d]: " % (
            strftime('%b %d %H:%M:%S', localtime(self.timestamp)),
            _hostname, self.ident, self.process_id
        )

    linePrefix = Once(linePrefix)


    def asString(self, d, a):

        if self.exc_info:
            return '\n'.join(filter(None,[self.message,self.traceback]))
        else:
            return self.message

    asString = Once(asString)


    def prefixedString(self,d,a):
        return '%s%s\n' % (
            self.linePrefix,
            self.asString.rstrip().replace('\n', '\n'+self.linePrefix)
        )

    prefixedString = Once(prefixedString)


    def __unicode__(self):
        return self.prefixedString


    def __str__(self):
        return self.prefixedString.encode('utf8','replace')







class logfileURL(ParsedURL):

    supportedSchemes = ('logfile', )

    def __init__(self, scheme=None, body=None, filename=None, level=None):
        self.setup(locals())

    def parse(self, scheme, body):

        filename, _qs = body, {}

        if '?' in filename:
            filename, _qs = filename.split('?', 1)

            _qs = dict([x.split('=', 1) for x in _qs.split('&')])

        _lvl = _qs.get('level', 'ALL').upper()

        if _lvl.startswith('PRI_') or _lvl.startswith('LOG_'):
            _lvl = _lvl[4:]

        level = getLevelFor(_lvl, None)

        if level is None:
            raise InvalidNameError(
                "Unrecognized log level", body
            )

        return locals()


    def retrieve(self, refInfo, name, context, attrs=None):
        return LogFile(
            context.creationParent, context.creationName,
            filename=self.filename, level=self.level
        )





class peakLoggerURL(ParsedURL):
    """URL that only looks up PEAK loggers, even if 'logging' is installed"""

    def retrieve(self, refInfo, name, context, attrs=None):

        prop = 'peak.logs'

        if self.body:
            prop = '%s.%s' % prop, self.body

        return config.getProperty(
            context.creationParent, prop
        )


class loggerURL(peakLoggerURL):

    """URL that retrieves a PEP 282 logger, or a PEAK substitute"""

    supportedSchemes = ('logging.logger', )

    def retrieve(self, refInfo, name, context, attrs=None):

        if logging:
            return logging.getLogger(self.body)

        return super(loggerURL,self).retrieve(refInfo, name, context, attrs)


def _levelledMessage(lvl,exc_info=()):

    def msg(self, msg, *args, **kwargs):
        if self.level <= lvl:
            self.publish(
                self.EventClass(
                    (msg % args), self, priority=lvl, **kwargs
                )
            )
    return msg


class AbstractLogger(Component):

    implements(ILogger)

    level = requireBinding("Minimum priority for messages to be published")
    EventClass = Event


    def isEnabledFor(self,lvl):
        return self.level >= lvl

    def getEffectiveLevel(self,lvl):
        return self.level

    debug     = _levelledMessage(DEBUG)
    info      = _levelledMessage(INFO)
    warning   = _levelledMessage(WARNING)
    error     = _levelledMessage(ERROR)
    critical  = _levelledMessage(CRITICAL)

    def exception(self, msg, *args, **kwargs):
        if self.level <= ERROR:
            self.publish(
                self.EventClass(
                    (msg % args), self, priority=ERROR, exc_info=True, **kwargs
                )
            )

    def log(self, lvl, msg, *args, **kwargs):
        if self.level <= lvl:
            self.publish(
                self.EventClass(
                    (msg % args), self, priority=lvl, **kwargs
                )
            )

    def publish(self, event):
        pass



    def __call__(self, priority, msg, ident=None):

        if priority>=self.level:
            if isinstance(msg,tuple):
                e = Event('ERROR', exc_info = msg)
            else:
                e = Event(msg, priority=priority)

            if ident is not None:
                e.ident = ident

        self.sink(e)



class LogFile(AbstractLogger):

    filename = requireBinding("name of file to write logs to")

    def publish(self, event):
        if event.priority >= self.level:
            fp = open(self.filename, "a")
            try:
                fp.write(str(event))
            finally:
                fp.close()


class LogStream(AbstractLogger):

    stream = requireBinding("Writable stream to write messages to")

    def publish(self, event):
        if event.priority >= self.level:
            self.stream.write(str(event))







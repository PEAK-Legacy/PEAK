'''TODO:

    * Flesh out ILogSink (__call__), ILogEvent, and docs here and in peak.api

    * SysLog and LogTee objects/URLs (low priority; we don't seem to use
      these at the moment)
'''

from peak.binding.components import Component, Make, Require, Obtain, Delegate
from peak.naming import URL
from peak.api import NOT_GIVEN, protocols, naming, config, NOT_FOUND
from peak.naming.factories.openable import FileURL
from peak.naming.interfaces import IObjectFactory

from time import time, localtime, strftime
import sys, os, traceback

from socket import gethostname
_hostname = gethostname().split('.')[0]
del gethostname


__all__ = [
    'getLevelName', 'getLevelFor', 'addLevelName', 'Event', 'logfileURL',
    'AbstractLogger', 'LogFile', 'LogStream', 'peakLoggerURL',
    'peakLoggerContext',
    'IBasicLogger', 'ILogger', 'ILogEvent', 'ILoggingService',
]













class IBasicLogger(protocols.Interface):

    """A PEP 282 "logger" object, minus configuration methods

    All methods that take 'msg' and positional arguments 'args' will
     interpolate 'args' into 'msg', so the format is a little like a
    'printf' in C.  For example, in this code:

        aLogger.debug("color=%s; number=%d", "blue", 42)

    the log message will be rendered as '"color=blue; number=42"'.  Loggers
    should not interpolate the message until they have verified that the
    message will not be trivially suppressed.  (For example, if the logger
    is not accepting messages of the designated priority level.)  This avoids
    needless string processing in code that does a lot of logging calls that
    are mostly suppressed.  (E.g. debug logging.)

    Methods that take a '**kwargs' keywords argument only accept an 'exc_info'
    flag as a keyword argument.  If 'exc_info' is a true value, exception data
    from 'sys.exc_info()' is added to the log message.
    """

    def isEnabledFor(lvl):
        """Return true if logger will accept messages of level 'lvl'"""

    def getEffectiveLevel():
        """Get minimum priority level required for messages to be accepted"""

    def debug(msg, *args, **kwargs):
        """Log 'msg' w/level DEBUG"""

    def info(msg, *args, **kwargs):
        """Log 'msg' w/level INFO"""

    def warning(msg, *args, **kwargs):
        """Log 'msg' w/level WARNING"""

    def error(msg, *args, **kwargs):
        """Log 'msg' w/level ERROR"""


    def critical(msg, *args, **kwargs):
        """Log 'msg' w/level CRITICAL"""

    def exception(msg, *args):
        """Log 'msg' w/level ERROR, add exception info"""

    def log(lvl, msg, *args, **kwargs):
        """Log 'msg' w/level 'lvl'"""


class ILogger(IBasicLogger):

    """A PEAK logger, with additional (syslog-compatible) level methods"""

    def trace(msg, *args, **kwargs):
        """Log 'msg' w/level TRACE"""

    def notice(msg, *args, **kwargs):
        """Log 'msg' w/level NOTICE"""

    def alert(msg, *args, **kwargs):
        """Log 'msg' w/level ALERT"""

    def emergency(msg, *args, **kwargs):
        """Log 'msg' w/level EMERG"""


class ILogEvent(protocols.Interface):
    """Temporary marker to allow configurable event classes

    This interface will be fleshed out more later, as the log system
    syncs up more with the capabilities and interfaces of the Python
    2.3 logging package.
    """







class ILoggingService(protocols.Interface):

    """A service that supplies loggers"""

    def getLogger(name=''):
        """Get an ILogger for 'name'"""

    def getLevelName(lvl, default=NOT_GIVEN):

        """Get a name for 'lvl', or return 'default'

        If 'default' is not given, return '"Level %s" % lvl', for
        symmetry with the 'logging' package."""

    def getLevelFor(ob, default=NOT_GIVEN):

        """Get a level integer for 'ob', or return 'default'

        If 'ob' is in fact a number (i.e. adding 0 to it works), return as-is.
        If 'ob' is a string representation of an integer, return numeric value,
        so that functions which want to accept either numbers or level names
        can do so by calling this converter.

        If no conversion can be found, and no default is specified, raise
        LookupError."""
















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

    # And make it so PEP 282 loggers can be adapted to ILogger
    protocols.declareImplementation(
        logging.getLogger().__class__,
        instancesProvide = [IBasicLogger]
    )

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
    timestamp  = Make(lambda: time())
    uuid       = Make('peak.util.uuid:UUID')
    hostname   = _hostname
    process_id = Make(lambda: os.getpid())
    exc_info   = ()

    def traceback(self,d,a):
        if self.exc_info:
            return ''.join(traceback.format_exception(*self.exc_info))
        return ''

    traceback = Make(traceback)

    def __init__(self, parent, message, **info):

        super(Event,self).__init__(parent,message,**info)
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


    def linePrefix(self):
        return  "%s %s %s[%d]: " % (
            strftime('%b %d %H:%M:%S', localtime(self.timestamp)),
            _hostname, self.ident, self.process_id
        )

    linePrefix = Make(linePrefix)


    def asString(self):

        if self.exc_info:
            return '\n'.join(filter(None,[self.message,self.traceback]))
        else:
            return self.message

    asString = Make(asString)


    def prefixedString(self):
        return '%s%s\n' % (
            self.linePrefix,
            self.asString.rstrip().replace('\n', '\n'+self.linePrefix)
        )

    prefixedString = Make(prefixedString)


    def __unicode__(self):
        return self.prefixedString


    def __str__(self):
        return self.prefixedString.encode('utf8','replace')







class logfileURL(FileURL):

    supportedSchemes = ('logfile', )
    defaultFactory = 'peak.running.logs.LogFile'

    class level(URL.IntField):
        defaultValue = ALL
        syntax = URL.Conversion(
            converter = lambda x:
                getLevelFor(
                    x.upper()[
                        (x.upper()[:4] in ('PRI_','LOG_') and 4 or 0):
                    ]
                ),
            formatter = lambda x: getLevelName(x,str(x)),
        )

    querySyntax = URL.Sequence('level=', level)























class peakLoggerURL(URL.Base):

    """URL that only looks up PEAK loggers, even if 'logging' is installed"""

    supportedSchemes = ('logging.logger', 'logger')


class peakLoggerContext(naming.AddressContext):

    schemeParser = peakLoggerURL

    def _get(self, name, retrieve=1):

        prop = 'peak.logs'

        if name.body:
            prop = '%s.%s' % (prop, name.body)

        ob = config.getProperty(self.creationParent, prop, default=NOT_FOUND)
        if ob is NOT_FOUND:
            return NOT_FOUND

        return ob


















def _levelledMessage(lvl,exc_info=()):
    def msg(self, msg, *args, **kwargs):
        if self.level <= lvl:
            if args:
                msg = msg % args
            self.publish(self.EventClass(self, msg, priority=lvl, **kwargs))
    return msg


class AbstractLogger(Component):

    protocols.advise(
        instancesProvide=[ILogger]
    )

    level = Require("Minimum priority for messages to be published")
    EventClass = Obtain(config.FactoryFor(ILogEvent))

    def isEnabledFor(self,lvl):
        return self.level >= lvl

    def getEffectiveLevel(self):
        return self.level

    trace     = _levelledMessage(TRACE)
    debug     = _levelledMessage(DEBUG)
    info      = _levelledMessage(INFO)
    notice    = _levelledMessage(NOTICE)
    warning   = _levelledMessage(WARNING)
    error     = _levelledMessage(ERROR)
    critical  = _levelledMessage(CRITICAL)
    alert     = _levelledMessage(ALERT)
    emergency = _levelledMessage(EMERG)








    def exception(self, msg, *args, **kwargs):
        if self.level <= ERROR:
            self.publish(
                self.EventClass(
                    self, (msg % args), priority=ERROR, exc_info=True, **kwargs
                )
            )

    def log(self, lvl, msg, *args, **kwargs):
        if self.level <= lvl:
            if args:
                msg = msg % args
            self.publish(
                self.EventClass(self, msg, priority=lvl, **kwargs)
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










class BasicLoggerAsLogger(protocols.Adapter):

    """Augment a PEP 282-style "logger" to have full PEAK methods"""

    protocols.advise(
        instancesProvide=[ILogger],
        asAdapterForTypes=[IBasicLogger]
    )

    isEnabledFor = getEffectiveLevel = debug = info = warning = error \
        = critical = exception = log = \
            Delegate('subject')

    def trace(self, *args, **kwargs):
        self.log(TRACE, *args, **kwargs)

    def notice(self, *args, **kwargs):
        self.log(NOTICE, *args, **kwargs)

    def alert(self, *args, **kwargs):
        self.log(ALERT, *args, **kwargs)

    def emergency(self, *args, **kwargs):
        self.log(EMERG, *args, **kwargs)

















class LogFile(AbstractLogger):

    filename = Require("name of file to write logs to")
    protocols.advise(classProvides=[IObjectFactory])

    def publish(self, event):
        if event.priority >= self.level:
            fp = open(self.filename, "a")
            try:
                fp.write(str(event))
            finally:
                fp.close()

    def getObjectInstance(klass, context, refInfo, name, attrs=None):
        url, = refInfo.addresses
        return klass(filename=url.getFilename(), level=url.level)

    getObjectInstance = classmethod(getObjectInstance)


class LogStream(AbstractLogger):

    stream = Require("Writable stream to write messages to")

    def publish(self, event):
        if event.priority >= self.level:
            self.stream.write(str(event))















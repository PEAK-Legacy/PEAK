'''TODO:

    * Flesh out ILogSink (__call__), ILogEvent, and docs here and in peak.api
    
    * Dump formatted kwargs as part of the standard log format

      issues: currently, we don't know which items in our dict were kwargs.
      record a list of which were passed? Also, some we wouldn't want to
      include even if they were passed explicity (for example, priority,
      which is passed explicitly by the LOG_XXX functions. 
      
    * SysLog and LogTee objects/URLs (low priority; we don't seem to use
      these at the moment)
      
    * Syslog (and others) may want the second part of asString without the
      leading stuff -- maybe refactor into another routine that returns
      just the second part
'''

from peak.binding.components import Component, Once, New
from peak.api import binding, config, naming, NOT_GIVEN, PropertyName
from time import time, localtime, strftime
import sys, os, traceback
from socket import gethostname
_hostname = gethostname().split('.')[0]
del gethostname


__all__ = [
    'LOG_LEVEL', 'Event', 'PRI_SYSEMERG', 'PRI_SYSALERT', 'PRI_CRITICAL',
    'PRI_ERROR', 'PRI_WARNING', 'PRI_NOTICE', 'PRI_INFO', 'PRI_VERBOSE',
    'PRI_DEBUG', 'PRI_TRACE', 'ILogSink', 'ILogEvent',
]

LOG_LEVEL = PropertyName('peak.log_level')






                        # syslog        PEP 282         zLOG
                        # ---------     -------         ----
PRI_SYSEMERG = 500      # LOG_EMERG
PRI_SYSALERT = 400      # LOG_ALERT
PRI_CRITICAL = 300      # LOG_CRIT      CRITICAL(50)    PANIC
PRI_ERROR    = 200      # LOG_ERR       ERROR(40)       ERROR
PRI_WARNING  = 100      # LOG_WARNING   WARN(30)        WARNING, PROBLEM
PRI_NOTICE   = 50       # LOG_NOTICE
PRI_INFO     = 0        # LOG_INFO      INFO(20)        INFO
PRI_VERBOSE  = -100     #                               BLATHER
PRI_DEBUG    = -200     # LOG_DEBUG     DEBUG(10)       DEBUG
PRI_TRACE    = -300     #               ALL(0)          TRACE

syslog_scale = (
    (PRI_DEBUG,    7, 'LOG_DEBUG'),
    (PRI_INFO,     6, 'LOG_INFO'),
    (PRI_NOTICE,   5, 'LOG_NOTICE'),
    (PRI_WARNING,  4, 'LOG_WARNING'),
    (PRI_ERROR,    3, 'LOG_ERR'),
    (PRI_CRITICAL, 2, 'LOG_CRIT'),
    (PRI_SYSALERT, 1, 'LOG_ALERT'),
    (PRI_SYSEMERG, 0, 'LOG_EMERG'),
)


priorities = {}
for k, v in globals().items():
    if k.startswith('PRI_'):
        priorities[k] = v












from Interface import Interface

class ILogSink(Interface):
    def sink(event):
        """Attempt to handle the event.

        Returns true if the event was consumed, else false"""

        pass


class ILogEvent(Interface):
    pass




























class Event(Component):

    __implements__ = ILogEvent

    ident      = 'PEAK' # XXX use component names if avail?
    message    = ''
    priority   = PRI_TRACE
    timestamp  = Once(lambda *x: time())
    uuid       = New('peak.util.uuid:UUID')
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

    def publish(self, publishTo=NOT_GIVEN):

        if publishTo is NOT_GIVEN:
            publishTo=self.getParentComponent()

        if self.priority<config.getProperty(LOG_LEVEL, publishTo, PRI_WARNING):
            return
            
        for sink in config.findUtilities(ILogSink, publishTo):
            if sink.sink(self):
                return  # if absorbed, we're done

        # If no logger absorbed us, go to stderr
        print >>sys.stderr, self.asString.encode('utf8','replace'),


    def asString(self, d, a):

        if self.exc_info:
            text = '\n'.join(filter(None,[self.message,self.traceback]))
        else:
            text = self.message

        prefix = "%s %s %s[%d]: " % (
            strftime('%b %d %H:%M:%S', localtime(self.timestamp)),
            _hostname, self.ident, self.process_id
        )

        return '%s%s\n' % (prefix, text.rstrip().replace('\n', '\n'+prefix))

    asString = Once(asString)

    def __str__(self):
        return self.asString

    hostname = _hostname

        



class logfileURL(naming.ParsedURL):

    _supportedSchemes = ('logfile', )
    
    def __init__(self, scheme=None, body=None, filename=None, level=None):
        self.setup(locals())

    def parse(self, scheme, body):
        
        filename, _qs = body, {}
        
        if '?' in filename:
            filename, _qs = filename.split('?', 1)

            _qs = dict([x.split('=', 1) for x in _qs.split('&')])
            
        level = _qs.get('level', 'PRI_TRACE').upper()
        if not level.startswith('PRI_') and not level.startswith('LOG_'):
            level = 'PRI_' + level

        level = priorities[level] # XXX handle KeyError somehow?
        
        return locals()


    def retrieve(self, refInfo, name, context, attrs=None):
        return Logfile(self.filename, self.level)

        












class LogSink:

    __implements__ = ILogSink
    
    def sink(self, event):
        return True
        
    def __call__(self, priority, msg, ident=None):
        if type(msg) is type(()):
            e = Event('ERROR', exc_info = msg)
        else:
            e = Event(msg, priority=priority)

        if ident is not None:
            e.ident = ident
            
        self.sink(e)



class Logfile(LogSink):
    def __init__(self, filename, level):
        self.filename, self.level = filename, level
        
        return 

    def sink(self, event):
        if event.priority >= self.level:
            fp = open(self.filename, "a")
            fp.write(event.asString)
            fp.close()

        return True
        









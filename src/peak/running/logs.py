from peak.binding.components import Component, Once, New, findUtilities
from peak.api import binding, config, NOT_GIVEN, PropertyName
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

                        # syslog        PEP 282     zLOG
                        # ---------     -------     ----
PRI_SYSEMERG = 500      # LOG_EMERG
PRI_SYSALERT = 400      # LOG_ALERT
PRI_CRITICAL = 300      # LOG_CRIT      CRITICAL    PANIC
PRI_ERROR    = 200      # LOG_ERR       ERROR       ERROR
PRI_WARNING  = 100      # LOG_WARNING   WARN        WARNING, PROBLEM
PRI_NOTICE   = 50       # LOG_NOTICE
PRI_INFO     = 0        # LOG_INFO      INFO        INFO
PRI_VERBOSE  = -100     #                           BLATHER
PRI_DEBUG    = -200     # LOG_DEBUG     DEBUG       DEBUG
PRI_TRACE    = -300     #                           TRACE

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


from Interface import Interface

class ILogSink(Interface):
    pass

class ILogEvent(Interface):
    pass


































class Event(Component):

    __implements__ = ILogEvent

    ident      = 'PEAK' # XXX
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
            
        for sink in findUtilities(ILogSink, publishTo):  # XXX need interface
            if sink(self):
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

        



'''TODO:

    * Flesh out ILogSink, ILogEvent, and docs here and in peak.api
    
    * LogFile object and ParsedURL

    * Dump formatted kwargs as part of the standard log format

    * SysLog and LogTee objects/URLs (low priority; we don't seem to use
      these at the moment)
'''

from peak.binding.components import Component
from peak.api import binding, config, NOT_GIVEN
from peak.naming.names import PropertyName

LOG_LEVEL = PropertyName('peak.logs.level')

class LogEvent(Component):

    priority = 0

    def __new__(klass, message, parent=None, publishTo=NOT_GIVEN, **info):

        min_priority = config.getProperty(LOG_LEVEL, parent, 9999)   # XXX

        if min_priority <= info.get('priority', klass.priority):
            return super(LogEvent,klass).__new__(
                klass, parent, **info
            )


    def __init__(self, message, parent=None, publishTo=NOT_GIVEN, **info):
        super(LogEvent,self).__init__(parent,**info)
        self.message = message
        self.publish(publishTo)


    def publish(self, publishTo=NOT_GIVEN):

        if publishTo is NOT_GIVEN:
            publishTo=self.getParentComponent()

        for p in iterParents(publishTo):
            sink = p._getConfigData(ILogSink,self)  # XXX need interface
            if sink is not NOT_FOUND:
                absorbed = sink(self)   # XXX should this be a method call?
                if absorbed: break

    # properties: message, priority, uuid, timestamp, process_id, ...?
    # methods: keys, items, __contains__,__iter__, __getitem__, ...?


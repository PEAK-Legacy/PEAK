from peak.api import *
from interfaces import *
from model import *
from peak.util.signature import ISignature

__all__ = [
    'titleAsPropertyName', 'titleAsMethodName', 'DocumentProcessor',
    'AbstractProcessor', 'MethodProcessor', 'ModelProcessor',
    'ActionProcessor', 'Summary'
]


def titleAsPropertyName(text):
    """Convert a string like '"Test Widget"' to '"Test.Widget"'"""
    return PropertyName.fromString(
        '.'.join(
            text.strip().replace('.',' ').split()
        )
    )

def titleAsMethodName(text):
    """Convert a string like '"Spam the Sprocket"' to '"spamTheSprocket"'"""
    text = ''.join(text.strip().title().split())
    return text[:1].lower()+text[1:]

















class DocumentProcessor(binding.Component):

    """The default document processor, used to process a test document

    This processor just looks at each table and finds a processor for that
    table, using the 'peak.ddt.processors' property namespace.  It then invokes
    the processor on the corresponding table.

    If you have a project that requires special setup or configuration for the
    tests being run, you can subclass this to do that.  You'll just need to
    get the test "runner" to use your class instead of this one, which can be
    done in an .ini file with::

        [Component Factories]
        peak.ddt.interfaces.IDocumentProcessor = "my_package.MyProcessorClass"
    """

    protocols.advise(
        instancesProvide = [IDocumentProcessor, ITableProcessor]
    )

    processors = binding.Make(
        config.Namespace('peak.ddt.processors')
    )

    def processDocument(self,document):
        self.processTables( iter(document.tables) )

    def processTables(self,tables):
        for table in tables:
            self.processTable(table, tables)

    def processTable(self,table, tables):
        """Delegate to 'ITableProcessor' specified by table's first cell"""
        self.getProcessor(
            table.rows[0].cells[0].text
        ).processTable(table,tables)




    def getProcessor(self,text):
        """Return an 'ITableProcessor' for 'text' in a cell"""

        name = titleAsPropertyName(text)
        processor = adapt( self.processors[name], ITableProcessor )
        binding.suggestParentComponent(self,name,processor)
        return processor


































class AbstractProcessor(binding.Component):

    """Processor that just iterates over table contents, doing nothing

    This is just a skeleton for you to subclass and override."""

    protocols.advise(
        instancesProvide = [ITableProcessor,IRowProcessor,ICellProcessor]
    )

    def processTable(self,thisTable,remainingTables):
        """Process 'thisTable', and optionally consume some 'remainingTables'

        The default implementation calls 'self.processRows()' after skipping
        the first row (which ordinarily just names the test processor).

        If you intend to override this method, see the docs for
        'ITableProcessor.processTable()' for details on what it can/can't do.
        """
        rows = iter(thisTable.rows)
        rows.next()     # skip first row
        self.processRows(rows)


    def processRows(self,rows):
        """Process 'rows' (an iterator of remaining rows)

        The default implementation calls 'self.processRow(row,rows)' for each
        row in 'rows', so 'processRow' can consume multiple rows by using
        'rows.next()'."""

        for row in rows:
            self.processRow(row, rows)


    def processRow(self,row,rows):
        """Calls 'self.processCells(iter(row.cells))'"""
        self.processCells(iter(row.cells))



    def processCells(self,cells):
        """Calls 'self.processCell(cell,cells)' for 'cell' in 'cells'"""
        for cell in cells:
            self.processCell(cell,cells)


    def processCell(self,cell,cells):
        """Abstract method: default does nothing"""
        pass
































class MethodProcessor(AbstractProcessor):

    """Perform tests by mapping columns to processor methods

    If a table has columns named 'x', 'y', and 'z', this processor will call
    'self.x(cell)' for the first cell in each row, 'self.y(cell)' for the
    second, and so on across each row.  It's up to you to define those methods
    in a subclass to do whatever is appropriate for the given cell, such
    as using it for input, using it to validate output, mark the cell "right"
    or "wrong", etc.

    You can also override various methods of this class to use different ways
    of finding the methods to be called, parse column headings differently,
    etc.  See each method's documentation for details.
    """

    handlers = ()

    def processRows(self,rows):
        """Set up methods from the heading row, then process other rows

        This method invokes 'self.setupHandlers(row,rows)' on the "heading"
        row (the row after the title row naming the processor for this table).
        It then invokes 'self.processRow(row,rows)' on the remaining rows.
        """
        row = rows.next()
        self.setupHandlers(row,rows)
        for row in rows:
            self.processRow(row, rows)












    def processRow(self,row,rows):
        """Match each cell with a handler, and invoke it

        This method matches each cell in the row with the corresponding handler
        from 'self.handlers', and then calls 'handler(cell)'.  If a handler
        raises an exception, attempt to annotate the cell with the appropriate
        error information."""

        self.beforeRow()
        try:
            for cell,handler in zip(row.cells,self.handlers):
                try:
                    handler(cell)
                except:
                    cell.exception()
        finally:
            self.afterRow()


    def setupHandlers(self,row,rows):
        """Obtain a handler (method) corresponding to each column heading

        Obtain a handler using 'self.getHandler(cell.text)' for each cell in
        the heading row, and put them in 'self.handlers' in the same order as
        they appear in the table.  If an error occurs when looking up a handler,
        the corresponding cell is annotated with error information, and the
        table's contents are skipped, by consuming the 'rows' iterator.
        """

        self.handlers = handlers = []

        for cell in row.cells:
            try:
                handlers.append(self.getHandler(cell.text))
            except:
                cell.exception()
                list(rows)  # skip remaining rows
                break



    def getHandler(self,text):
        """Get a handler using 'text' from a cell

        The default implementation uses 'titleAsMethodName' to normalize the
        cell text to a "camel case" (e.g. 'camelCase') format, and then
        attempts to return 'getattr(self,methodName)'.

        You can override this routine to return any callable object that
        accepts a 'ddt.Cell' as its sole parameter.
        """
        return getattr(self,titleAsMethodName(text))


    def beforeRow(self):
        """Perform any pre-row setup

        This method is akin to 'setUp()' in a PyUnit test case.  It gives you
        an opportunity to create objects, reset values, open files, etc. before
        starting a row in the test table.  The default implementation does
        nothing."""


    def afterRow(self):
        """Perform any post-row tear down

        This method is akin to 'tearDown()' in a PyUnit test case.  It gives
        you an opportunity to get rid of objects, reset values, close files,
        etc. after finishing a row in the test table.  The default
        implementation does nothing."""












class ModelProcessor(MethodProcessor):

    """Test a domain object by getting/setting attributes or invoking methods

    Unlike 'ddt.ModelProcessor', this class can be used without subclassing.
    Just specify the 'targetClass' in the constructor, and optionally set
    'itemPerRow' to 'False' if you want one target instance to be used for
    all rows.  You can also supply 'methodTypes' to list the 'model.IType'
    types that should be used when invoking methods or checking their return
    values.  For example, you might use the following in an .ini file::

        [peak.ddt.processors]

        MyProcessor = ddt.ModelProcessor(
            targetClass = importString('my_model.MyElement'),
            methodTypes = Items(
                someMethodReturningInt = model.Integer,
                someMethodTakingFloat = model.Float,
                # etc.
            )
        )

    If 'someMethodReturningInt' or 'someMethodTakingFloat' are invoked by a
    test, the cell value will be converted to/from an integer or float as
    appropriate.

    By default, 'ModelProcessor' checks whether a column heading ends in ':'
    (indicating a "set" operation) or '?' (indicating a "get" operation).
    If you would like to override this, you can supply a 'columnSuffixes'
    argument to the constructor, or override it in a subclass.  See the
    'parseHeader()' method for more details.
    """

    itemPerRow = True

    methodTypes = ()

    columnSuffixes = ( (':','set'), ('?','get') )



    targetClass = binding.Require(
        """The 'peak.model.Element' subclass that is to be tested"""
    )

    targetInstance = binding.Require(
        """The specific instance currently being tested"""
    )

    _methodMap = binding.Make(
        lambda self: dict(self.methodTypes)
    )


    def getHandler(self,text):
        """Figure out whether handler should get or set, and how to do that

        The default implementation uses 'self.parseHeader()' to determine the
        kind of handler required, and then returns 'self.getGetter()' or
        'self.getSetter()' accordingly."""

        getOrSet, name = self.parseHeader(text)
        if getOrSet=='get':
            return self.getGetter(name)
        elif getOrSet=='set':
            return self.getSetter(name)
        raise ValueError("Invalid return value from parseHeader():", getOrSet)


    def beforeRow(self):
        """Create a new instance, if needed, before starting a row"""
        if self.itemPerRow or not self._hasBinding('targetInstance'):
            self.targetInstance = self.targetClass()    # note: suggests parent


    def afterRow(self):
        """Get rid of old instance, if needed, after finishing a row"""
        if self.itemPerRow:
            self._delBinding('targetInstance')



    def parseHeader(self,text):
        """Return a '(getOrSet,name)' tuple for header 'text'

        'getOrSet' should be the string '"get"' or '"set"', indicating how the
        column is to be interpreted.  'name' should be the name to be used for
        calling 'self.getSetter()' or 'self.getGetter()', respectively.

        The default implementation uses 'self.columnSuffixes' to determine the
        appropriate type.  The 'columnSuffixes' attribute must be an iterable
        of '(suffix,getOrSet)' pairs, where 'suffix' is a string to be checked
        for at the end of 'text', and 'getOrSet' is a string indicating whether
        the column should be get or set.  The suffices in 'columnSuffixes' are
        checked in the order they are provided, so longer suffixes should be
        listed before shorter ones to avoid ambiguity.  An empty string may
        be used as a suffix, to indicate the default behavior for a column, but
        should be placed last in the suffixes, if used.  If no default is
        given, and no suffixes match, an error is raised, causing the header
        to be marked in error and the table as a whole to be skipped.
        """

        text = text.strip()
        for suffix,kind in self.columnSuffixes:
            if text.endswith(suffix):
                return kind, text[:len(text)-len(suffix)]

        raise ValueError("Unable to determine column type:", text)















    def getGetter(self,name):
        """Get a "getting" handler for 'name'

        This is implemented by getting a 'ddt.ICellMapper' for the named
        feature from 'self.getMapper(name)', and returning a handler that
        performs a 'mapper.get()' operation on 'self.targetInstance' each
        time it's invoked.
        """
        get = self.getMapper(name).get
        return lambda cell: get(self.targetInstance, cell)


    def getSetter(self,name):
        """Get a "setting" handler for 'name'

        This is implemented by getting a 'ddt.ICellMapper' for the named
        feature from 'self.getMapper(name)', and returning a handler that
        performs a 'mapper.set()' operation on 'self.targetInstance' each
        time it's invoked.
        """
        set = self.getMapper(name).set
        return lambda cell: set(self.targetInstance, cell)


    def getMapper(self,name):
        """Get an 'ICellMapper' for the named feature in the target class

        This is done by retrieving the named attribute from the class (after
        applying 'titleAsMethodName()' to the name) and and adapting it to
        the 'ddt.ICellMapper' interface.  If there is an entry in
        'self.methodTypes' that indicates the datatype that should be used for
        the column, the mapper is informed of this via its 'suggestType()'
        method.
        """
        name = titleAsMethodName(name)
        mapper = adapt(getattr(self.targetClass,name), ICellMapper)
        binding.suggestParentComponent(self,name,mapper)
        if name in self._methodMap:
            mapper.suggestType(self._methodMap[name])
        return mapper

class ActionProcessor(ModelProcessor):

    """Test a domain object using a "script" of actions

    This 'ModelProcessor' subclass reads actions from a table with three or
    more columns.  The first cell in each row is a "command", such as "start",
    "enter", "press", or "check", that is used to look up a method on the
    action processor itself.  The invoked method can then use the remaining
    cells from the row to obtain its arguments.  See the docs for the 'start',
    'enter', 'press', and 'check' methods for more details.

    Note that tables used with 'ActionProcessor' must *not* include column
    headings, as 'ActionProcessor' does not parse them.  (As a result, it also
    has no need for a 'columnSuffix' attribute or 'parseHeader()' method.)

    Unlike 'ModelProcessor', 'ActionProcessor' should not be given a specific
    'targetClass' to use.  Instead, the 'start' command is used to create an
    instance of a specified class, which is then used until another 'start'
    command is executed.  Also, 'ActionProcessor' does not use the
    'columnSuffixes' attribute, because it does not parse column headings.
    """

    # XXX suggestType handling???

    # our class is the class of whatever our instance is, at any point in time
    targetClass = binding.Obtain('targetInstance/__class__', noCache=True)
    fixtures = binding.Make( config.Namespace('peak.ddt.models') )

    def processRows(self,rows):
        """Just process rows; no column headings are required or wanted."""
        for row in rows:
            self.processRow(row, rows)

    def processRow(self,row,rows):
        """Process a row using 'self.getCommand(firstCell.text)(otherCells)'"""
        try:
            self.getCommand(row.cells[0].text)(row.cells[1:])
        except:
            row.cells[0].exception()


    def getCommand(self,text):
        """Lookup 'text' as a method of this processor

        You can override this if you want to use a different strategy for
        obtaining commands.  The returned command must be a callable that
        takes one parameter: a list of cells.  The cells the command receives
        will be the remainder of the row that contained the command; typically
        this means 'row.cells[1:]'.
        """
        return getattr(self, titleAsMethodName(text))


    def mapCell(self,mapperCell,mappedCell,mapMethod):

        """Convenience method for two-argument mapping commands"""

        try:
            mapMethod = getattr(self.getMapper(mapperCell.text),mapMethod)
        except:
            mapperCell.exception()
        try:
            mapMethod(self.targetInstance, mappedCell)
        except:
            mappedCell.exception()

















    # Basic commands

    def start(self,cells):
        """Obtain an instance of the specified type and use it from here on
        """
        try:
            name = titleAsPropertyName(cells[0].text)
            self.targetInstance = self.fixtures[name]
            # XXX if processor, pass extra cells?
        except:
            cells[0].exception()


    def enter(self,cells):
        """Look up a field name, and then set it to value
        """
        self.mapCell(cells[0],cells[1],'set')


    def press(self,cells):
        """Invoke specified method/button/whatever
        """
        self.mapCell(cells[0],cells[0],'invoke')


    def check(self,cells):
        """Look up a field name, and check if value matches
        """
        self.mapCell(cells[0],cells[1],'get')












class Summary(AbstractProcessor):

    """Add rows to a table summarizing the test results so far"""

    key = "Counts"

    def processTable(self,table,tables):

        document = table.document
        summary = document.summary
        summary[self.key] = table.document.score
        items = summary.items(); items.sort()

        for k,v in items:
            row = table.newRow(
                cells=[table.newCell(text=k),table.newCell(text=str(v))]
            )
            table.addRow(row)

            if k==self.key:
                self.reportCounts(row.cells[1])

    def reportCounts(self,cell):

        before = cell.document.score

        if before.wrong or before.exceptions:
            cell.wrong()
        else:
            cell.right()

        # Put the score back to what it was
        cell.document.score = before








class FeatureAsCellMapper(protocols.Adapter):

    """Cell mapping support for 'property' and other data descriptors"""

    protocols.advise(
        instancesProvide=[ICellMapper],
        asAdapterForProtocols=[model.IFeature]
    )

    def suggestType(self,dataType):
        pass    # we know our datatype, so we don't care about this

    def get(self,instance,cell):
        value = self.subject.__get__(instance)
        if self.subject.parse(cell.text) == value:
            cell.right()
        else:
            cell.wrong(self.subject.format(value))

    def set(self,instance,cell):
        self.subject.__set__(instance, self.subject.parse(cell.text))

    def invoke(self,instance,cell):
        try:
            raise TypeError("Attributes can't be invoked", self.subject)
        except:
            cell.exception()














class PropertyAsCellMapper(protocols.Adapter):

    """Cell mapping support for 'property' and other data descriptors"""

    protocols.advise(
        instancesProvide=[ICellMapper],
        asAdapterForTypes=[property]
    )

    dataType = model.String

    def suggestType(self,dataType):
        self.dataType = dataType

    def get(self,instance,cell):
        value = self.subject.__get__(instance)
        cell.assertEqual(value, self.dataType)

    def set(self,instance,cell):
        value = self.dataType.mdl_fromString(cell.text)
        self.subject.__set__(instance, value)

    def invoke(self,instance,cell):
        try:
            raise TypeError("Descriptors can't be invoked", self.subject)
        except:
            cell.exception()


def descriptorAsCellMapper(ob,proto):
    if hasattr(ob,'__set__') and hasattr(ob,'__get__'):
        return PropertyAsCellMapper(ob,proto)


protocols.declareAdapter(
    descriptorAsCellMapper, provides=[ICellMapper], forTypes=[object]
)




class CallableAsCellMapper(protocols.Adapter):

    """Cell mapping support for methods"""

    protocols.advise(
        instancesProvide=[ICellMapper],
        asAdapterForProtocols=[ISignature]
    )

    dataType = model.String

    def suggestType(self,dataType):
        self.dataType = dataType

    def get(self,instance,cell):
        value = self.subject.getCallable()(instance)
        cell.assertEqual(value, self.dataType)

    def set(self,instance,cell):
        value = self.dataType.mdl_fromString(cell.text)
        self.subject.getCallable()(instance, value)

    def invoke(self,instance,cell):
        try:
            self.subject.getCallable()(instance)
        except:
            cell.exception()















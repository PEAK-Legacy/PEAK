from peak.api import *
from interfaces import *
from model import *

__all__ = [
    'DocumentProcessor', 'AbstractProcessor', 'ColumnProcessor',
    'SummaryProcessor'
]

    
class DocumentProcessor(binding.Component):

    protocols.advise(
        instancesProvide = [IDocumentProcessor, ITableProcessor]
    )

    factories = binding.Make(config.Namespace('peak.ddt.processors'))

    def processDocument(self,document):
        self.processTables( iter(document.tables) )

    def processTables(self,tables):
        for table in tables:
            self.processTable(table, tables)

    def processTable(self,table, tables):
        name = table.rows[0].cells[0].text
        adapt(
            self.factories[name](self), ITableProcessor
        ).processTable(table, tables)











class AbstractProcessor(binding.Component):

    protocols.advise(
        instancesProvide = [ITableProcessor,IRowProcessor,ICellProcessor]
    )

    def processTable(self,table,tables):
        rows = iter(table.rows)
        rows.next()     # skip first row
        self.processRows(rows)

    def processRows(self,rows):
        for row in rows:
            self.processRow(row, rows)

    def processRow(self,row,rows):
        self.processCells(iter(row.cells))

    def processCells(self,cells):
        for cell in cells:
            self.processCell(cell,cells)

    def processCell(self,cell,cells):
        pass

















class ColumnProcessor(AbstractProcessor):

    handlers = ()

    def processRows(self,rows):
        row = rows.next()
        self.setupHandlers(row,rows)
        super(ColumnProcessor,self).processRows(rows)


    def processRow(self,row,rows):
        for cell,handler in zip(row.cells,self.handlers):
            try:
                handler(cell)
            except:
                cell.exception()


    def setupHandlers(self,row,rows):
        self.handlers = handlers = []; failed = False

        for cell in row.cells:
            try:
                handlers.append(self.getHandler(cell.text))
            except:
                cell.exception(); failed = True

        if failed:
            list(rows)  # skip remaining rows


    def getHandler(self,text):
        return getattr(self,text)








class SummaryProcessor(AbstractProcessor):

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









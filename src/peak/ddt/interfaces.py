from peak.api import *

__all__ = [
    'ICellProcessor', 'IDocumentProcessor', 'IRowProcessor', 'ITableProcessor',
]


class IDocumentProcessor(protocols.Interface):

    def processDocument(document):
        """Process a document, updating it with test results

        Note that this method (and anything it calls) should not interact with
        the document's DM or transaction context.  Typically this method would
        simply iterate over the document's tables, invoking an appropriate
        'ITableProcessor' for each one."""


class ITableProcessor(protocols.Interface):

    def processTable(thisTable,remainingTables):
        """Process 'thisTable', and optionally consume some 'remainingTables'

        'remainingTables' is an iterator over the remaining tables in the same
        document, if any.  Any tables consumed from this iterator will be
        skipped by the calling document processor.  This allows a table
        processor to take control of processing for subsequent tables in a
        document, e.g. when multiple tables are needed to process a single
        test."""












class IRowProcessor(protocols.Interface):

    def processRow(thisRow,remainingRows):
        """Process 'thisRow', and optionally consume some 'remainingRows'

        'remainingRows' is an iterator over the remaining rows in the same
        table, if any.  Any rows consumed from this iterator will be
        skipped by the calling table processor.  This allows a row
        processor to take control of processing for subsequent rows in a
        table, e.g. when multiple rows need to be processed by the same
        processor."""


class ICellProcessor(protocols.Interface):

    def processCell(cell):
        """Process 'cell', using it for input or output as needed"""

























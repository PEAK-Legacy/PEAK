from peak.api import *
from model import Document, Table, Row, Cell
from bisect import insort

GREEN  = ' bgcolor="#CFFFCF"'
RED    = ' bgcolor="#FFCFCF"'
GREY   = ' bgcolor="#EFEFEF"'
YELLOW = ' bgcolor="#FFFFCF"'

def label(text):
    return ' <font size="-1" color="#C08080"><i>%s</i></font>' % text

def diminish(text):
    return ' <font color="#808080">%s</font>' % text

def escape(text):
    return text.replace(
        '&','&amp;'
    ).replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')






















def parseTags(text,tag,startAt,startBy,contentProcessor):

    pos = startAt
    items = []

    while pos < startBy:
        tagStart = text.find("<"+tag,pos)

        if tagStart<0 or tagStart>=startBy:
            break

        contentStart = text.find(">", tagStart)
        if contentStart<0:
            break

        firstClose = text.find("</"+tag, contentStart)
        if firstClose<0:
            break

        pos, item = contentProcessor(
            tag=tagStart, content=contentStart+1, close=firstClose
        )
        items.append(item)

    return pos,items
















class HTMLDocument(storage.EntityDM):

    text = binding.Require("Text of the HTML document to be processed")

    lctext = binding.Make(lambda self: self.text.lower())

    output = binding.Require(
        "Output stream, as a stream factory", adaptTo=naming.IStreamFactory
    )

    stream = binding.Make(
        lambda self: self.output.create('t')
    )

    document = binding.Make(lambda self: self[Document])

    edits = binding.Make(list)

    def _ghost(self, oid, state=None):

        if oid is Document:
            return Document()

        kind,tag,content,close = oid
        return kind()


    def _load(self, oid, ob):

        if oid is Document:
            pos, items = parseTags(
                self.lctext, "table", 0, len(self.text), self.makeTable
            )
            return {'tables':items}

        raise AssertionError("Can't load state for anything but Document")





    def insertText(self,pos,text):
        insort(self.edits, (pos,pos,text))


    def _save(self,ob):
        if ob._p_oid is Document:
            return  # nothing to save

        kind,tag,content,close = ob._p_oid

        if kind is not Cell:
            return  # still nothing to save

        if ob.score.right:
            self.insertText(content-1,GREEN)

        elif ob.score.wrong:
            self.insertText(content-1,RED)
            if hasattr(ob,'actual'):
                pass    # XXX

        elif ob.score.ignored:
            self.insertText(content-1,GREY)

        elif ob.score.exceptions:
            self.insertText(content-1,YELLOW)


    def flush(self,ob=None):
        self._delBinding('edits')
        super(HTMLDocument,self).flush()
        lastPos = 0
        for (s,e,t) in self.edits:
            self.stream.write(self.text[lastPos:s])
            self.stream.write(t)
            lastPos=e
        self.stream.write(self.text[lastPos:])




    def makeTable(self,tag,content,close):
        pos, rows = parseTags(
            self.lctext, "tr", content, close, self.makeRow
        )
        return pos, self.preloadState(
            (Table,tag,content,close),
            {'rows':rows, 'document':self.document}
        )

    def makeRow(self,tag,content,close):
        pos, cells = parseTags(
            self.lctext, "td", content, close, self.makeCell
        )
        return pos, self.preloadState(
            (Row,tag,content,close),
            {'cells':cells, 'document':self.document}
        )

    def makeCell(self,tag,content,close):
        pos, subTables = parseTags(
            self.lctext, "table", content, close, self.makeTable
        )
        return pos, self.preloadState(
            (Cell,tag,content,close),
            {'document':self.document, 'text':self.text[content:close]}
        )

























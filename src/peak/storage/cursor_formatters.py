"""A variety of ways to render the data from a cursor to a file object"""

from peak.api import *

class AbstractCursorFormatter(binding.Component):
    cursor = binding.Obtain('..')
    header = binding.Make(lambda: True)
    footer = binding.Make(lambda: True)
    delim  = binding.Make(lambda: '|')
    

    def __call__(self, stdout):
        c = self.cursor
        
        if c._cursor.description:
            self.formatSet(c, stdout)

        while c.nextset():
            if not c._cursor.description:
                continue

            self.betweenSets(stdout)
            self.formatSet(c, stdout)


    def betweenSets(self, stdout):
        print >>stdout


    def printFooter(self, c, stdout, nr):
        print >>stdout, "(%d rows)" % nr


    def formatSet(self, c, stdout):
        nrows = self.formatRows(c, stdout)

        if self.footer:
            self.printFooter(c, stdout, nrows)


    def toStr(self, val, width=None):
        if val is None:
            if width is None:
                return "NULL"
            return "NULL".ljust(width)[:width]
        elif width is None:
            return str(val)
        elif type(val) in (int, long):
            return "%*d" % (width, val)
        elif type(val) is float:
            return "%*g" % (width, val)
        else:
            if type(val) is unicode:
                val = val.encode('utf8')
    
            return str(val).ljust(width)[:width]
        

class cursorToHoriz(AbstractCursorFormatter):
    def formatRows(self, c, stdout):
        out = stdout.write
        t, d, l = [], [], []
        first = 1
        nr = 0

        for r in c._cursor.description:
            w = r[2]
            if not w or w <= 0: w = r[3]
            if not w or w <= 0: w = 20 # XXX
            if w<len(r[0]): w = len(r[0])

            t.append(self.toStr(r[0], w)); d.append('-' * w); l.append(w)

        if self.header:
            out(' '.join(t)); out('\n')
            out(' '.join(d)); out('\n')
        
        for r in c:
            nr += 1
            i = 0
            o = []
            for v in r:
                o.append(self.toStr(v, l[i]))
                i += 1

            out(' '.join(o))
            out('\n')

        return nr


class cursorToVert(AbstractCursorFormatter):
    def formatRows(self, c, stdout):
        h = [x[0] for x in c._cursor.description]
        w = max([len(x) for x in h])
        nr = 0

        for r in c:
            i = 0
            nr += 1
            for v in r:
                print >>stdout, "%s %s" % (h[i].rjust(w), self.toStr(v))
                i += 1
            print >>stdout

        return nr


class cursorToPlain(AbstractCursorFormatter):
    def formatRows(self, c, stdout):
        d = self.delim
        nr = 0

        if self.header:
            print >>stdout, d.join([x[0] for x in c._cursor.description])

        for r in c:
            nr += 1
            print >>stdout, d.join([self.toStr(v) for v in r])

        return nr



class cursorToRepr(AbstractCursorFormatter):
    def formatRows(self, c, stdout):
        nr = 0

        if self.header:
            print >>stdout, `c._cursor.description`
        for r in c:
            nr += 1
            print >>stdout, `r`

        return nr



class cursorToLDIF(AbstractCursorFormatter):
    header = binding.Make(lambda: False)
    footer = binding.Make(lambda: False)

    def formatRows(self, c, stdout):
        nr = 0
        
        for r in c:
            nr += 1
            cols = r.keys()

            # dn must come first, according to RFC2849...
            try:
                dnix = cols.index('dn')
                del cols[dnix]
                cols.insert(0, 'dn')
            except ValueError:
                # ...though we can't be fully compliant if there is no dn!
                pass
                 
            for col in cols:
                vals = r[col]
                if type(vals) is not list:
                    vals = [vals]
                
                for val in vals:
                    if val is None:
                        continue
                        
                    val = self.toStr(val)
                    colname = "%s: " % col

                    ascii = True
                    for ch in val:
                        o = ord(ch)
                        if o < 32 or o > 126:
                            ascii = False
                            break

                    if not ascii:
                        colname = "%s:: " % col
                        val = ''.join(val.encode('base64').split())
                    
                    fl = 77 - len(colname)
                    stdout.write(colname + val[:fl] + '\n')
                    
                    val = val[fl:]
                    while val:
                        stdout.write(' ' + val[:76] + '\n')
                        val = val[76:]
                
            print >>stdout

        return nr

"""
        R   W   A   T   C
r   ->  y   n   n   n   n
r+  ->  y   y   n   n   n
w   ->  n   y   n   y   y
w+  ->  y   y   n   y   y
a   ->  n   y   y   n   y
a+  ->  y   y   y   n   y
+   ->  y   y   -   -   -

b                           n
"""


class OpenMode(object):
    """Open Mode"""

    __slots__ = ('read', 'write', 'append', 'truncate', 'create', 'text')
    
    def __init__(self, s):
        self.text = True
        self.create = -1

        for c in s:
            if c in 'rwa':
                if self.create != -1:
                    raise IOError, "invalid mode: more than one of r, w, or a, or specified multiple times"
                elif c == 'r':
                    self.read = True
                    self.write= self.append= self.truncate= self.create= False
                elif c == 'w':
                    self.read = self.append = False
                    self.write = self.truncate = self.create = True
                else:
                    self.read = self.truncate = False
                    self.write = self.append = self.create = True
            elif c == '+':
                if self.create == -1:
                    raise IOError, "invalid mode: must specify r, w, or a before +"
                self.read = self.write = True
            elif c == 'b':
                self.text = False                
            else:
                raise IOError, 'invalid mode: character %s unknown' % `c`

        if self.create == -1:
            raise IOError, 'invalid mode: one of r, w, or a must be specified'


    def __str__(self):
        if self.create:
            if (self.append and self.truncate) \
            or (not self.append and not self.truncate):
                raise IOError, 'mode cannot be represented as a string'
            if self.append:
                mode = 'a'
            else:
                mode = 'w'
            if self.read and self.write:
                mode += '+'
        else:
            mode = 'r'
            if self.append or self.truncate:
                raise IOError, 'mode cannot be represented as a string'
            if self.write:
                mode += '+'


        if not self.text:
            mode += 'b'

        return mode


    def __repr__(self):
        return '<open mode ' + \
        (self.read      and 'R' or 'r') + \
        (self.write     and 'W' or 'w') + \
        (self.append    and 'A' or 'a') + \
        (self.truncate  and 'T' or 't') + \
        (self.create    and 'C' or 'c') + \
        (self.text      and 'X' or 'x') + \
        '>'


if __name__ == "__main__":
    # XXX move to unit tests, and test that invalid modes error
    
    for m in ("r", "w", "a", "r+", "w+", "a+"):
        assert str(OpenMode(m)) == m
        assert str(OpenMode(m + 'b')) == m + 'b'


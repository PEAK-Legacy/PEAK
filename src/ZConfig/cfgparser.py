##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Configuration parser."""

import ZConfig
import ZConfig.url

from ZConfig.substitution import isname, substitute

try:
    True
except NameError:
    True = 1
    False = 0


class ZConfigParser:
    __metaclass__ = type
    __slots__ = ('resource', 'context', 'lineno',
                 'stack', 'defs', 'file', 'url')

    def __init__(self, resource, context, defines=None):
        self.resource = resource
        self.context = context
        self.file = resource.file
        self.url = resource.url
        self.lineno = 0
        self.stack = []   # [(type, name, delegatename, prevmatcher), ...]
        if defines is None:
            defines = {}
        self.defs = defines

    def nextline(self):
        line = self.file.readline()
        if line:
            self.lineno += 1
            return False, line.strip()
        else:
            return True, None

    def parse(self, section):
        done, line = self.nextline()
        while not done:
            if line[:1] in ("", "#"):
                # blank line or comment
                pass

            elif line[:2] == "</":
                # section end
                if line[-1] != ">":
                    self.error("malformed section end")
                section = self.end_section(section, line[2:-1])

            elif line[0] == "<":
                # section start
                if line[-1] != ">":
                    self.error("malformed section start")
                section = self.start_section(section, line[1:-1])

            elif line[0] == "%":
                self.handle_directive(section, line[1:])

            else:
                self.handle_key_value(section, line)

            done, line = self.nextline()

        if self.stack:
            self.error("unclosed sections not allowed")

    def start_section(self, section, rest):
        isempty = rest[-1:] == "/"
        if isempty:
            text = rest[:-1].rstrip()
        else:
            text = rest.rstrip()
        # parse section start stuff here
        m = _section_start_rx.match(text)
        if not m:
            self.error("malformed section header")
        type, name, delegatename = m.group('type', 'name', 'delegatename')
        type = type.lower()
        if name:
            name = name.lower()
        try:
            newsect = self.context.startSection(section, type, name,
                                                delegatename)
        except ZConfig.ConfigurationError, e:
            self.error(e[0])

        if isempty:
            self.context.endSection(section, type, name, delegatename, newsect)
            return section
        else:
            self.stack.append((type, name, delegatename, section))
            return newsect

    def end_section(self, section, rest):
        if not self.stack:
            self.error("unexpected section end")
        type = rest.rstrip().lower()
        opentype, name, delegatename, prevsection = self.stack.pop()
        if type != opentype:
            self.error("unbalanced section end")
        try:
            self.context.endSection(
                prevsection, type, name, delegatename, section)
        except ZConfig.ConfigurationError, e:
            self.error(e[0])
        return prevsection

    def handle_key_value(self, section, rest):
        m = _keyvalue_rx.match(rest)
        if not m:
            self.error("malformed configuration data")
        key, value = m.group('key', 'value')
        if not value:
            value = ''
        else:
            value = substitute(value, self.defs)
        try:
            section.addValue(key, value, (self.lineno, None, self.url))
        except ZConfig.ConfigurationError, e:
            self.error(e[0])

    def handle_directive(self, section, rest):
        m = _keyvalue_rx.match(rest)
        if not m:
            self.error("missing or unrecognized directive")
        name, arg = m.group('key', 'value')
        if name not in ("define", "include"):
            self.error("unknown directive: " + `name`)
        if not arg:
            self.error("missing argument to %%%s directive" % name)
        if name == "include":
            self.handle_include(section, arg)
        elif name == "define":
            self.handle_define(section, arg)
        else:
            assert 0, "unexpected directive for " + `"%" + rest`

    def handle_include(self, section, rest):
        newurl = ZConfig.url.urljoin(self.url, rest)
        self.context.includeConfiguration(section, newurl, self.defs)

    def handle_define(self, section, rest):
        parts = rest.split(None, 1)
        defname = parts[0].lower()
        defvalue = ''
        if len(parts) == 2:
            defvalue = parts[1]
        if self.defs.has_key(defname):
            self.error("cannot redefine " + `defname`)
        if not isname(defname):
            self.error("not a substitution legal name: " + `defname`)
        self.defs[defname] = substitute(defvalue, self.defs)

    def error(self, message):
        raise ZConfig.ConfigurationSyntaxError(message, self.url, self.lineno)


import re
# _name_re cannot allow "(" or ")" since we need to be able to tell if
# a section has a name or not: <section (name)> would be ambiguous if
# parentheses were allowed in names.
_name_re = r"[^\s()]+"
_keyvalue_rx = re.compile(r"(?P<key>%s)\s*(?P<value>[^\s].*)?$"
                          % _name_re)
_section_start_rx = re.compile(r"(?P<type>%s)"
                               r"(?:\s+(?P<name>%s))?"
                               r"(?:\s*[(](?P<delegatename>%s)[)])?"
                               r"$"
                               % (_name_re, _name_re, _name_re))
del re

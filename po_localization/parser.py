# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import io
import re
from po_localization.po_file import PoFile
from .strings import unescape, UnescapeError

MATCHER = re.compile(r'^\s*(#.*)?\s*(?:([^"\[\s]+)(?:\[(\d+)\])?)?(?:\s*"(.*)")?\s*$')


def parse_po_filename(filename):
    po_file = PoFile()
    Parser(po_file).parse_po_filename(filename)
    return po_file.get_catalog()


def parse_po_file(fp, filename=None):
    po_file = PoFile()
    Parser(po_file).parse_po_file(fp)
    return po_file.get_catalog()


class Parser(object):
    def __init__(self, po_file):
        self.state = 'start'
        self.po_file = po_file
        self.context = None
        self.message = None
        self.plural_message = None
        self.translated_message = None
        self.current_plural_index = 0
        self.plural_translated_messages = {}

    def _store_pending_data(self):
        if self.message is not None:
            if self.message == '':
                for line in self.translated_message.split('\n'):
                    if len(line):
                        parts = line.partition(':')
                        self.po_file.add_header_field(parts[0], parts[2].strip())
            else:
                entry = self.po_file.add_entry(self.message, self.plural_message, self.context)
                if self.state == 'after msgstr':
                    entry.add_translation(self.translated_message)
                elif self.state == 'after msgstr[N]':
                    for index, text in self.plural_translated_messages.items():
                        entry.add_plural_translation(index, text)
        self._reset_pending_data()

    def _reset_pending_data(self):
        self.context = None
        self.message = None
        self.plural_message = None
        self.translated_message = None
        self.current_plural_index = 0
        self.plural_translated_messages.clear()

    def parse_po_filename(self, filename):
        # XXX: Actually, encoding may be different and specified in the .po file comment
        with io.open(filename, encoding='utf-8') as po_file:
            return self.parse_po_file(po_file, filename)

    def parse_po_file(self, fp, filename=None):
        for line_number, line in enumerate(fp):
            try:
                match = MATCHER.match(line)
                if match is None:
                    raise ParseError(filename, line_number, "Invalid syntax")
                if match.group(1):
                    # comment
                    continue
                if match.group(2) == 'msgctxt' and self.state not in ('after msgctxt', 'after msgid', 'after msgid_plural'):
                    self._store_pending_data()
                    if match.group(3) is not None:
                        raise ParseError(filename, line_number, "Unexpected index afted keyword")
                    if match.group(4) is None:
                        raise ParseError(filename, line_number, "Missing context string")
                    self.context = unescape(match.group(4))
                    self.state = 'after msgctxt'
                elif match.group(2) == 'msgid' and self.state not in ('after msgid', 'after msgid_plural'):
                    if self.state != 'after msgctxt':
                        self._store_pending_data()
                    if match.group(3) is not None:
                        raise ParseError(filename, line_number, "Unexpected index afted keyword")
                    if match.group(4) is None:
                        raise ParseError(filename, line_number, "Missing message identifier string")
                    self.message = unescape(match.group(4))
                    self.state = 'after msgid'
                elif match.group(2) == 'msgid_plural' and self.state == 'after msgid':
                    if match.group(3) is not None:
                        raise ParseError(filename, line_number, "Unexpected index after keyword")
                    if match.group(4) is None:
                        raise ParseError(filename, line_number, "Missing plural message identifier string")
                    self.plural_message = unescape(match.group(4))
                    self.state = 'after msgid_plural'
                elif match.group(2) == 'msgstr' and self.state in ('after msgid', 'after msgid_plural', 'after msgstr[N]'):
                    if match.group(4) is None:
                        raise ParseError(filename, line_number, "Missing translated message string")
                    if self.state == 'after msgid':
                        if match.group(3) is not None:
                            raise ParseError(filename, line_number, "Unexpected plural message index after keyword")
                        self.translated_message = unescape(match.group(4))
                        self.state = 'after msgstr'
                    elif self.state == 'after msgid_plural' or self.state == 'after msgstr[N]':
                        if match.group(3) is None:
                            raise ParseError(filename, line_number, "Missing plural message index after keyword")
                        self.current_plural_index = int(match.group(3))
                        if self.current_plural_index in self.plural_translated_messages:
                            raise ParseError(filename, line_number,
                                "Duplicate plural message index: {}".format(self.current_plural_index))
                        self.plural_translated_messages[self.current_plural_index] = unescape(match.group(4))
                        self.state = 'after msgstr[N]'
                elif match.group(2) is None:
                    if match.group(4) is None:
                        # empty-line
                        continue
                    if self.state == 'after msgid':
                        self.message += unescape(match.group(4))
                    elif self.state == 'after msgstr':
                        self.translated_message += unescape(match.group(4))
                    elif self.state == 'after msgid_plural':
                        self.plural_message += unescape(match.group(4))
                    elif self.state == 'after msgstr[N]':
                        self.plural_translated_messages[self.current_plural_index] += unescape(match.group(4))
                    else:
                        raise ParseError(filename, line_number,
                            "Unexpected string continuation after '{}'".format(self.state))
                else:
                    raise ParseError(filename, line_number, "Unexpected keyword: {}".format(match.group(2)))
            except UnescapeError as e:
                raise ParseError(filename, line_number, e)
        self._store_pending_data()
        if self.state in ('after msgctxt', 'after msgid', 'after msgid_plural'):
            raise ParseError(filename, None, "Unexpected end of file")


class ParseError(Exception):
    def __init__(self, filename, line_number, message, *args):
        self.filename = filename
        self.line_number = line_number
        self.parse_error_message = message
        super(ParseError, self).__init__(filename, line_number, message)

    def __str__(self):
        return "{}:{}: {}".format(self.filename, self.line_number, self.parse_error_message)

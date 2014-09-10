# coding=utf-8

from __future__ import absolute_import
from __future__ import unicode_literals

import re
from django.utils.six import text_type

MATCHER = re.compile(r'^\s*(#.*)?\s*(?:([^"\[\s]+)(?:\[(\d+)\])?)?(?:\s*"(.*)")?\s*$')


def parse_po_filename(filename):
    with open(filename) as po_file:
        return parse_po_file(po_file, filename)


def parse_po_file(po_file, filename=None):
    catalog = {}
    state = 'start'
    context = None
    message = ''
    translated_message = ''
    plural_message = ''
    current_plural_index = 0
    plural_translated_messages = {}

    def decode_string(encoded_string):
        # XXX: Actually, encoding may be different and specified in the .po file comment
        return text_type(encoded_string.decode('string_escape'), encoding='utf-8')

    def store_pending_data():
        if len(message):
            if state == 'after msgstr':
                catalog[decode_string(message)] = decode_string(translated_message)
            elif state == 'after msgstr[N]':
                for number, text in plural_translated_messages.items():
                    catalog_key = (decode_string(message), number)
                    catalog[catalog_key] = decode_string(text)
                plural_translated_messages.clear()

    for line_number, line in enumerate(po_file):
        match = MATCHER.match(line)
        if match is None:
            raise ParseError(filename, line_number, "Invalid syntax")
        if match.group(1):
            # comment
            continue
        if match.group(2) == 'msgctxt' and state not in ('after msgctxt', 'after msgid', 'after msgid_plural'):
            if match.group(3) is not None:
                raise ParseError(filename, line_number, "Unexpected index afted keyword")
            if match.group(4) is None:
                raise ParseError(filename, line_number, "Missing context string")
            context = match.group(4)
            state = 'after msgctxt'
        elif match.group(2) == 'msgid' and state not in ('after msgid', 'after msgid_plural'):
            store_pending_data()
            if match.group(3) is not None:
                raise ParseError(filename, line_number, "Unexpected index afted keyword")
            if match.group(4) is None:
                raise ParseError(filename, line_number, "Missing message identifier string")
            message = match.group(4)
            # prefixing message with context using '\x04' as namespace separator
            if context:
                message = '\x04'.join([context, match.group(4)])
                context = None
            state = 'after msgid'
        elif match.group(2) == 'msgid_plural' and state == 'after msgid':
            if match.group(3) is not None:
                raise ParseError(filename, line_number, "Unexpected index after keyword")
            if match.group(4) is None:
                raise ParseError(filename, line_number, "Missing plural message identifier string")
            plural_message = match.group(4)
            state = 'after msgid_plural'
        elif match.group(2) == 'msgstr' and state in ('after msgid', 'after msgid_plural', 'after msgstr[N]'):
            if match.group(4) is None:
                raise ParseError(filename, line_number, "Missing translated message string")
            if state == 'after msgid':
                if match.group(3) is not None:
                    raise ParseError(filename, line_number, "Unexpected plural message index after keyword")
                translated_message = match.group(4)
                state = 'after msgstr'
            elif state == 'after msgid_plural' or state == 'after msgstr[N]':
                if match.group(3) is None:
                    raise ParseError(filename, line_number, "Missing plural message index after keyword")
                current_plural_index = int(match.group(3))
                if current_plural_index in plural_translated_messages:
                    raise ParseError(filename, line_number, "Duplicate plural message index: {}", current_plural_index)
                plural_translated_messages[current_plural_index] = match.group(4)
                state = 'after msgstr[N]'
        elif match.group(2) is None:
            if match.group(4) is None:
                # empty-line
                continue
            if state == 'after msgid':
                message += match.group(4)
            elif state == 'after msgstr':
                translated_message += match.group(4)
            elif state == 'after msgid_plural':
                plural_message += match.group(4)
            elif state == 'after msgstr[N]':
                plural_translated_messages[current_plural_index] += match.group(4)
            else:
                raise ParseError(
                    filename, line_number, "Expected message continuation or valid keyword after '{}'", state)
        else:
            raise ParseError(filename, line_number, "Unexpected keyword: {}", match.group(2))
    store_pending_data()
    if state in ('after msgctxt', 'after msgid', 'after msgid_plural'):
        raise ParseError(filename, None, "Unexpected end of file")
    return catalog


class ParseError(Exception):
    def __init__(self, filename, line_number, message, *args):
        self.line_number = line_number
        formatted_message = message.format(*args)
        if filename is None:
            if line_number is not None:
                formatted_message = "At line {}: {}".format(line_number, formatted_message)
        else:
            if line_number is None:
                formatted_message = "In {}: {}".format(filename, formatted_message)
            else:
                formatted_message = "At {}:{}: {}".format(filename, line_number, formatted_message)
        super(ParseError, self).__init__(formatted_message)

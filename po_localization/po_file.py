# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re
from io import StringIO
from .strings import escape

EMBEDDED_NEWLINE_MATCHER = re.compile(r'[^\n]\n+[^\n]')


class PoFile(object):
    def __init__(self):
        self.header_fields = []
        self._header_index = {}
        self.entries = {}

    def clone(self):
        po_file = PoFile()
        po_file.header_fields.extend(self.header_fields)
        for msgid, entry in self.entries.items():
            po_file.entries[msgid] = entry.clone()
        return po_file

    def add_header_field(self, field, value):
        if field in self._header_index:
            self.header_fields[self._header_index[field]] = (field, value)
        else:
            self._header_index[field] = len(self.header_fields)
            self.header_fields.append((field, value))

    def add_entry(self, message, plural=None, context=None):
        msgid = get_msgid(message, context)
        if msgid in self.entries:
            entry = self.entries[msgid]
            # Allow merging a non-plural entry with a plural entry
            # If more than one plural entry only keep the first
            if entry.plural is None:
                entry.plural = plural
        else:
            entry = TranslationEntry(message, plural, context)
            self.entries[msgid] = entry
        return entry

    def dump(self, fp, include_locations=True, prune_obsoletes=False):
        needs_blank_line = False
        if len(self.header_fields):
            print('msgid ""', file=fp)
            print('msgstr ""', file=fp)
            for field, value in self.header_fields:
                print(r'"{}: {}\n"'.format(field, value), file=fp)
            needs_blank_line = True
        nplurals = self.get_nplurals()
        for entry in sorted(self.entries.values(), key=get_entry_sort_key):
            if needs_blank_line:
                print('', file=fp)
            needs_blank_line = entry.dump(
                fp, nplurals, include_locations=include_locations, prune_obsolete=prune_obsoletes)

    def dumps(self, include_locations=True, prune_obsoletes=False):
        string_file = StringIO()
        self.dump(string_file, include_locations, prune_obsoletes)
        return string_file.getvalue()

    def get_catalog(self):
        catalog = {}
        for entry in self.entries.values():
            entry.fill_catalog(catalog)
        return catalog

    def get_nplurals(self):
        plural_field_index = self._header_index.get('Plural-Forms', -1)
        if plural_field_index != -1:
            field, value = self.header_fields[plural_field_index]
            if field == 'Plural-Forms':
                for pair in value.split(';'):
                    parts = pair.partition('=')
                    if parts[0].strip() == 'nplurals':
                        return int(parts[2].strip())
        return None


class TranslationEntry(object):
    MIN_NPLURALS = 2

    def __init__(self, message, plural=None, context=None):
        self.message = message
        self.plural = plural
        self.context = context
        self.locations = []
        self.translations = {}

    def clone(self):
        entry = TranslationEntry(self.message, self.plural, self.context)
        entry.locations.extend(self.locations)
        entry.translations = self.translations.copy()
        return entry

    def add_location(self, filename, lineno):
        self.locations.append((filename, lineno))

    def add_translation(self, translation):
        self.add_plural_translation(0, translation)

    def add_plural_translation(self, index, translation):
        self.translations[index] = translation

    def fill_catalog(self, catalog):
        msgid = get_msgid(self.message, self.context)
        if self.plural is not None:
            for index, translation in self.translations.items():
                if translation:
                    catalog[(msgid, index)] = translation
        else:
            translation = self.translations.get(0, '')
            if translation:
                catalog[msgid] = translation

    def dump(self, fp, nplurals=None, include_locations=True, prune_obsolete=False):
        """
        If plural, shows exactly 'nplurals' plurals if 'nplurals' is not None, else shows at least min_nplurals.
        All plural index are ordered and consecutive, missing entries are displayed with an empty string.
        """
        if not len(self.locations):
            if prune_obsolete or all(translation == '' for index, translation in self.translations.items()):
                return False
            else:
                print('#. obsolete entry', file=fp)
        if include_locations and len(self.locations):
            print('#: {}'.format(' '.join('{}:{}'.format(*location) for location in self.locations)), file=fp)
        if self.context is not None:
            print('msgctxt {}'.format(multiline_escape(self.context)), file=fp)
        print('msgid {}'.format(multiline_escape(self.message)), file=fp)
        if self.plural is not None:
            print('msgid_plural {}'.format(multiline_escape(self.plural)), file=fp)
            if nplurals is None:
                nplurals = self.get_suggested_nplurals()
            for index in range(nplurals):
                print('msgstr[{}] {}'.format(index, multiline_escape(self.translations.get(index, ''))), file=fp)
        else:
            print('msgstr {}'.format(multiline_escape(self.translations.get(0, ''))), file=fp)
        return True

    def get_suggested_nplurals(self):
        if len(self.translations) > 0:
            return max(max(self.translations.keys()) + 1, self.MIN_NPLURALS)
        else:
            return self.MIN_NPLURALS


def multiline_escape(string):
    if EMBEDDED_NEWLINE_MATCHER.search(string):
        lines = string.split('\n')
        return (
            '""\n'
            + '\n'.join('"{}\\n"'.format(escape(line)) for line in lines[:-1])
            + ('\n"{}"'.format(escape(lines[-1])) if len(lines[-1]) else ""))
    else:
        return '"{}"'.format(escape(string))


def get_msgid(message, context=None):
    if context is not None:
        return '{}\x04{}'.format(context, message)
    else:
        return message

def get_entry_sort_key(entry):
    return entry.locations, entry.context if entry.context else '', entry.message

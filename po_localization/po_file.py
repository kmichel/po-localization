# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .strings import escape


class PoFile(object):
    def __init__(self):
        self.header_fields = []
        self.header_index = {}
        self.entries = {}

    def clone(self):
        po_file = PoFile()
        po_file.header_fields.extend(self.header_fields)
        for msgid, entry in self.entries.items():
            po_file.entries[msgid] = entry.clone()
        return po_file

    def add_header_field(self, field, value):
        if field in self.header_index:
            self.header_fields[self.header_index] = (field, value)
        else:
            self.header_index[field] = len(self.header_fields)
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
        nplurals = self._get_nplurals()
        for entry in sorted(self.entries.values(), key=lambda e: e.locations):
            if needs_blank_line:
                print('', file=fp)
            needs_blank_line = entry.dump(
                fp, nplurals, include_locations=include_locations, prune_obsolete=prune_obsoletes)

    def get_catalog(self):
        catalog = {}
        for entry in self.entries.values():
            entry.fill_catalog(catalog)
        return catalog

    def _get_nplurals(self):
        for field, value in self.header_fields:
            if field == 'Plural-forms':
                for pair in value.split(';'):
                    parts = pair.partition('=')
                    if parts[0].strip() == 'nplurals':
                        return int(parts[2].strip())
        return None


class TranslationEntry(object):
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

    def dump(self, fp, nplurals=None, min_nplurals=2, include_locations=True, prune_obsolete=False):
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
            print('msgctxt "{}"'.format(escape(self.context)), file=fp)
        print('msgid "{}"'.format(escape(self.message)), file=fp)
        if self.plural is not None:
            print('msgid_plural "{}"'.format(escape(self.plural)), file=fp)
            if nplurals is None:
                if len(self.translations) > 0:
                    nplurals = max(max(self.translations.keys()) + 1, min_nplurals)
                else:
                    nplurals = min_nplurals
            for index in range(nplurals):
                print('msgstr[{}] "{}"'.format(index, self.translations.get(index, '')), file=fp)
        else:
            print('msgstr "{}"'.format(self.translations.get(0, '')), file=fp)
        return True

def get_msgid(message, context=None):
    if context is not None:
        return '{}\x04{}'.format(context, message)
    else:
        return message

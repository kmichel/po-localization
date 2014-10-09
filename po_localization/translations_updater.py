# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
from . import python_extractor, template_extractor
from .parser import Parser
from .po_file import PoFile

extractors = {
    '.html': template_extractor.extract_messages,
    '.txt': template_extractor.extract_messages,
    '.py': python_extractor.extract_messages
}
""":type extractors: dict[str, (str, str, str) -> None]"""


class TranslationsUpdater(object):
    def __init__(self, root_paths=(), locales=(), include_locations=True, prune_obsoletes=False):
        super(TranslationsUpdater, self).__init__()
        self.root_paths = root_paths
        self.locales = locales
        self.include_locations = include_locations
        self.prune_obsoletes = prune_obsoletes

    def execute(self):
        for root_path in self.root_paths:
            update_translations(
                root_path=root_path,
                locales=self.locales,
                include_locations=self.include_locations,
                prune_obsoletes=self.prune_obsoletes)

    def list_files(self):
        for root_path in self.root_paths:
            for dirpath, dirnames, filenames in os.walk(root_path):
                for filename in filenames:
                    extension = os.path.splitext(filename)[1]
                    if extension in extractors:
                        yield os.path.join(dirpath, filename)


def update_translations(
        root_path, domain='django', locales=(), locales_path='locale',
        update_all=True, include_locations=True, prune_obsoletes=False):
    locales_path = os.path.join(root_path, locales_path)
    base_po_file = create_base_po_file(root_path)
    create_locales_paths(locales_path, locales)
    if os.path.isdir(locales_path):
        for locale in os.listdir(locales_path):
            locale_path = os.path.join(locales_path, locale)
            if os.path.isdir(locale_path) and (update_all or locale in locales):
                update_locale_translations(base_po_file, locale_path, domain, include_locations, prune_obsoletes)


def create_base_po_file(root_path):
    base_po_file = PoFile()
    root_path_length = len(root_path) + (0 if root_path.endswith('/') else 1)
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            extension = os.path.splitext(filename)[1]
            extractor = extractors.get(extension, None)
            if extractor is not None:
                full_filename = os.path.join(dirpath, filename)
                printable_filename = full_filename[root_path_length:]
                extractor(full_filename, base_po_file, printable_filename=printable_filename)
    return base_po_file


def create_locales_paths(locales_path, locales):
    for locale in locales:
        locale_path = os.path.join(locales_path, locale)
        if not os.path.exists(locale_path):
            os.makedirs(locale_path)


def update_locale_translations(
        po_file, locale_path, domain='django', include_locations=True, prune_obsoletes=False):
    po_file = po_file.clone()
    translation_filename = os.path.join(locale_path, 'LC_MESSAGES/{}.po'.format(domain))
    if os.path.exists(translation_filename):
        Parser(po_file).parse_po_filename(translation_filename)
    if not os.path.exists(os.path.dirname(translation_filename)):
        os.makedirs(os.path.dirname(translation_filename))
    # We do this dance to avoid overwriting the locale file with a broken one
    # if the dump function ever fails. A real atomic write may be better but
    # requires fiddling with file attributes and alters the inode (which is used
    # by osx aliases).
    memory_file = io.StringIO()
    po_file.dump(memory_file, include_locations=include_locations, prune_obsoletes=prune_obsoletes)
    memory_file.seek(0)
    with io.open(translation_filename, 'w', encoding='utf-8') as locale_file:
        locale_file.write(memory_file.read())

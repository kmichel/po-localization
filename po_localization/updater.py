#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
from django.utils.importlib import import_module
from .extractor import extract_messages
from .po_file import PoFile
from .parser import Parser


def update_modules_translations(
        modules_import_paths, domain='django', locales=(), locales_path='locale',
        update_all=True, include_locations=True, prune_obsoletes=False):
    for module_import_path in modules_import_paths:
        module = import_module(module_import_path)
        app_path = os.path.dirname(module.__file__)
        update_translations(
            app_path, domain, locales, locales_path, update_all, include_locations, prune_obsoletes)


def update_translations(
        root_path, domain='django', locales=(), locales_path='locale',
        update_all=True, include_locations=True, prune_obsoletes=False):
    base_po_file = PoFile()
    root_path_length = len(root_path) + (0 if root_path.endswith('/') else 1)
    locales_path = os.path.join(root_path, locales_path)
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith('.py'):
                full_filename = os.path.join(dirpath, filename)
                printable_filename = full_filename[root_path_length:]
                extract_messages(full_filename, base_po_file, printable_filename=printable_filename)
    for locale in locales:
        locale_path = os.path.join(locales_path, locale)
        if not os.path.exists(locale_path):
            os.makedirs(locale_path)
    if os.path.isdir(locales_path):
        for locale in os.listdir(locales_path):
            locale_path = os.path.join(locales_path, locale)
            if os.path.isdir(locale_path) and (update_all or locale in locales):
                locale_po_file = base_po_file.clone()
                translation_filename = os.path.join(locale_path, 'LC_MESSAGES/{}.po'.format(domain))
                if os.path.exists(translation_filename):
                    Parser(locale_po_file).parse_po_filename(translation_filename)
                # We do this dance to avoid overwriting the locale file with a broken one
                # if the dump function ever fails. A real atomic write may be better but
                # requires fiddling with file attributes and alters the inode (which is used
                # by osx aliases).
                memory_file = io.StringIO()
                locale_po_file.dump(memory_file, include_locations=include_locations, prune_obsoletes=prune_obsoletes)
                memory_file.seek(0)
                if not os.path.exists(os.path.dirname(translation_filename)):
                    os.makedirs(os.path.dirname(translation_filename))
                with io.open(translation_filename, 'w', encoding='utf-8') as locale_file:
                    locale_file.write(memory_file.read())

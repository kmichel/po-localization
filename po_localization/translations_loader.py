# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import django.utils.translation.trans_real
from . import parser


class TranslationsLoader(object):
    def __init__(self, locale_paths=(), locales=()):
        self.locale_paths = locale_paths
        self.locales = locales
        super(TranslationsLoader, self).__init__()

    def execute(self):
        for locale in self.locales:
            language = django.utils.translation.trans_real.to_language(locale)
            # XXX: this will trigger useless loading of translations from django code
            catalog = django.utils.translation.trans_real.translation(language)._catalog
            catalog.clear()
            for file_path in self._get_translation_files(locale):
                catalog.update(parser.parse_po_filename(file_path))

    def list_files(self):
        for locale in self.locales:
            for file_path in self._get_translation_files(locale):
                yield file_path

    def _get_translation_files(self, locale):
        for locale_path in self.locale_paths:
            translation_path = os.path.join(locale_path, locale, 'LC_MESSAGES/django.po')
            if os.path.isfile(translation_path):
                yield translation_path

# coding=utf-8

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
import sys
import threading
from django.utils._os import upath
from django.utils.importlib import import_module
import django.utils.translation.trans_real
from . import parser

logger = logging.getLogger(__name__)


class TranslationLoader(object):
    def __init__(self, locales, locale_paths):
        self.locales = locales
        self.locale_paths = locale_paths
        self.file_mtimes = {}
        self.is_dirty = True
        self.lock = threading.Lock()

    def update(self, force=False):
        with self.lock:
            if force:
                self.is_dirty = True
            self._check_for_changes()
            if self.is_dirty:
                self._load()

    def _load(self):
        for locale in self.locales:
            language = django.utils.translation.trans_real.to_language(locale)
            # XXX: this will trigger useless loading of translations from django code
            catalog = django.utils.translation.trans_real.translation(language)._catalog
            catalog.clear()
            for file_path in self._get_translation_files(locale):
                catalog.update(parser.parse_po_filename(file_path))
        self.is_dirty = False

    def _check_for_changes(self):
        for locale in self.locales:
            for file_path in self._get_translation_files(locale, include_missing=True):
                if os.path.isfile(file_path):
                    file_mtime = get_file_mtime(file_path)
                    if file_path not in self.file_mtimes or self.file_mtimes[file_path] != file_mtime:
                        self.file_mtimes[file_path] = file_mtime
                        self.is_dirty = True
                elif file_path in self.file_mtimes:
                    self.is_dirty = True
                    del self.file_mtimes[file_path]

    def _get_translation_files(self, locale, include_missing=False):
        for locale_path in self.locale_paths:
            translation_path = os.path.join(locale_path, locale, 'LC_MESSAGES/django.po')
            if include_missing or os.path.isfile(translation_path):
                yield translation_path


def get_enabled_locales(settings):
    ret = []
    for language_code, language_name in settings.LANGUAGES:
        ret.append(django.utils.translation.trans_real.to_locale(language_code))
    return ret


def get_localization_paths(settings):
    ret = []
    django_locale_path = os.path.join(os.path.dirname(upath(sys.modules[settings.__module__].__file__)), 'locale')
    ret.append(django_locale_path)
    for app_name in reversed(settings.INSTALLED_APPS):
        app = import_module(app_name)
        app_locale_path = os.path.join(os.path.dirname(upath(app.__file__)), 'locale')
        if os.path.isdir(app_locale_path):
            ret.append(app_locale_path)
    for locale_path in reversed(settings.LOCALE_PATHS):
        if os.path.isdir(locale_path):
            ret.append(locale_path)
    return ret


def get_file_mtime(filename):
    stat = os.stat(filename)
    mtime = stat.st_mtime
    if sys.platform == 'win32':
        mtime -= stat.st_ctime
    return mtime

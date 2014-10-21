# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import django
from django.conf import settings
from django.utils._os import upath
from django.utils.importlib import import_module
from django.test.signals import setting_changed
import django.utils.translation.trans_real
from po_localization.file_watcher import FileWatcher
from po_localization.translations_loader import TranslationsLoader
from po_localization.translations_updater import TranslationsUpdater


class PoLocalizationMiddleware(object):
    def __init__(self):
        self.translations_updater = TranslationsUpdater()
        self.translations_loader = TranslationsLoader()
        self.translations_updater_watcher = FileWatcher(self.translations_updater)
        self.translations_loader_watcher = FileWatcher(self.translations_loader)
        self.reconfigure()
        setting_changed.connect(self._reconfigure)
        self.waiting_for_first_request = True

    def _reconfigure(self, sender, **kwargs):
        self.reconfigure()

    def reconfigure(self):
        self.translations_updater.root_paths = get_translations_update_roots()
        self.translations_updater.locales = get_enabled_locales(
            excluded_locales=getattr(settings, 'UPDATE_TRANSLATIONS_EXCLUDED_LOCALES', ()))
        self.translations_updater.include_locations = getattr(settings, 'UPDATE_TRANSLATIONS_WITH_LOCATIONS', True)
        self.translations_updater.prune_obsoletes = getattr(settings, 'UPDATE_TRANSLATIONS_PRUNE_OBSOLETES', False)
        # Force update in case any setting has changed (which changes the output)
        self.translations_updater_watcher.set_dirty()

        self.translations_loader.locales = get_enabled_locales()
        self.translations_loader.locale_paths = get_translations_reload_roots()

    def process_request(self, request):
        if getattr(settings, 'AUTO_UPDATE_TRANSLATIONS', False):
            self.translations_updater_watcher.check()
        if self.waiting_for_first_request or getattr(settings, 'AUTO_RELOAD_TRANSLATIONS', settings.DEBUG):
            self.translations_loader_watcher.check()
        self.waiting_for_first_request = False


def get_enabled_locales(excluded_locales=()):
    ret = []
    for language_code, language_name in settings.LANGUAGES:
        locale = django.utils.translation.trans_real.to_locale(language_code)
        if locale not in excluded_locales:
            ret.append(locale)
    return ret


def get_translations_reload_roots():
    ret = get_packages_paths(['django.conf'], 'locale')
    if django.VERSION[:2] < (1, 7):
        ret.extend(get_packages_paths(reversed(settings.INSTALLED_APPS), 'locale'))
    else:
        from django.apps import apps

        for app_config in apps.get_app_configs():
            module_path = os.path.dirname(upath(app_config.module.__file__))
            ret.append(os.path.join(module_path, 'locale'))
    for locale_path in reversed(settings.LOCALE_PATHS):
        if os.path.isdir(locale_path):
            ret.append(locale_path)
    return ret


def get_translations_update_roots():
    return get_packages_paths(getattr(settings, 'UPDATE_TRANSLATIONS_PACKAGES', ()))


def get_packages_paths(packages_import_paths, relative_path=''):
    ret = []
    for package_import_path in packages_import_paths:
        module = import_module(package_import_path)
        module_path = os.path.dirname(upath(module.__file__))
        ret.append(os.path.join(module_path, relative_path))
    return ret

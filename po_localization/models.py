# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from django import VERSION as django_version
from django.conf import settings
from django.core.signals import request_started
from django.dispatch import receiver
from django.utils._os import upath
from django.utils.importlib import import_module
import django.utils.translation.trans_real
from .translations_loader import TranslationsLoader
from .translations_updater import TranslationsUpdater


translations_updater = None
translations_loader = None


def handle_settings_change():
    global translations_updater
    global translations_loader
    translations_updater = TranslationsUpdater(
        root_paths=get_translations_update_roots(settings),
        locales=get_enabled_locales(settings),
        include_locations=getattr(settings, 'UPDATE_TRANSLATIONS_WITH_LOCATIONS', True),
        prune_obsoletes=getattr(settings, 'UPDATE_TRANSLATIONS_PRUNE_OBSOLETES', False))

    # This is responsible for updating translations after server reload (after python file modification)
    if getattr(settings, 'AUTO_UPDATE_TRANSLATIONS', False):
        translations_updater.reload()

    translations_loader = TranslationsLoader(
        get_enabled_locales(settings),
        get_translations_reload_roots(settings))

    # Only load translations if not waiting for the first request
    if not getattr(settings, 'AUTO_RELOAD_TRANSLATIONS', settings.DEBUG):
        translations_loader.reload()


def get_enabled_locales(settings):
    ret = []
    for language_code, language_name in settings.LANGUAGES:
        ret.append(django.utils.translation.trans_real.to_locale(language_code))
    return ret


def get_translations_reload_roots(settings):
    ret = []
    localization_packages = ['django.conf']
    # TODO: use app registry in django >= 1.7
    localization_packages.extend(reversed(settings.INSTALLED_APPS))
    ret.extend(get_packages_paths(localization_packages, 'locale'))
    for locale_path in reversed(settings.LOCALE_PATHS):
        if os.path.isdir(locale_path):
            ret.append(locale_path)
    return ret


def get_translations_update_roots(settings):
    return get_packages_paths(getattr(settings, 'UPDATE_TRANSLATIONS_PACKAGES', ()))


def get_packages_paths(packages_import_paths, relative_path=''):
    ret = []
    for package_import_path in packages_import_paths:
        module = import_module(package_import_path)
        module_path = os.path.dirname(upath(module.__file__))
        ret.append(os.path.join(module_path, relative_path))
    return ret


@receiver(request_started)
def reload_before_request(sender, **kwargs):
    if getattr(settings, 'AUTO_UPDATE_TRANSLATIONS', False):
        translations_updater.reload()
    if getattr(settings, 'AUTO_RELOAD_TRANSLATIONS', settings.DEBUG):
        translations_loader.reload()


# Only auto-initialize now if Django is older than 1.7
if django_version[0] == 1 and django_version[1] < 7:
    handle_settings_change()

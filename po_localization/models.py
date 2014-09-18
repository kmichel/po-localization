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
from . import loader
from .updater import update_modules_translations


def update_apps_translations():
    update_modules_translations(
        modules_import_paths=getattr(settings, 'UPDATE_TRANSLATIONS_APPS', ()),
        locales=get_enabled_locales(settings),
        include_locations=getattr(settings, 'UPDATE_TRANSLATIONS_WITH_LOCATIONS', True),
        prune_obsoletes=getattr(settings, 'UPDATE_TRANSLATIONS_PRUNE_OBSOLETES', False))


def handle_settings_change():
    if getattr(settings, 'AUTO_UPDATE_TRANSLATIONS', False):
        update_apps_translations()

    global translation_loader
    translation_loader = loader.TranslationLoader(
        get_enabled_locales(settings),
        get_localization_paths(settings))


def get_enabled_locales(settings):
    ret = []
    for language_code, language_name in settings.LANGUAGES:
        ret.append(django.utils.translation.trans_real.to_locale(language_code))
    return ret


def get_localization_paths(settings):
    ret = []
    localization_modules = ['django.conf']
    # TODO: use app registry in django >= 1.7
    localization_modules.extend(reversed(settings.INSTALLED_APPS))
    ret.extend(get_modules_localization_paths(localization_modules))
    for locale_path in reversed(settings.LOCALE_PATHS):
        if os.path.isdir(locale_path):
            ret.append(locale_path)
    return ret


def get_modules_localization_paths(module_paths):
    ret = []
    for module_path in reversed(module_paths):
        module = import_module(module_path)
        module_locale_path = os.path.join(os.path.dirname(upath(module.__file__)), 'locale')
        ret.append(module_locale_path)
    return ret


@receiver(request_started)
def reload_before_request(sender, **kwargs):
    if getattr(settings, 'AUTO_RELOAD_TRANSLATIONS', settings.DEBUG):
        translation_loader.reload()


def load_initial_translations():
    # Only load them if not waiting
    if not getattr(settings, 'AUTO_RELOAD_TRANSLATIONS', settings.DEBUG):
        translation_loader.reload()


# Only load translations now if django is older than 1.7
if django_version[0] == 1 and django_version[1] < 7:
    handle_settings_change()
    load_initial_translations()

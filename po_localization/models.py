# coding=utf-8

from __future__ import absolute_import
from __future__ import unicode_literals

from django.conf import settings
from django.core.signals import request_started
from . import loader

translation_loader = loader.TranslationLoader(
    loader.get_enabled_locales(settings),
    loader.get_localization_paths(settings))


def update_translations(sender, **kwargs):
    translation_loader.update()


if getattr(settings, 'AUTORELOAD_TRANSLATIONS', settings.DEBUG):
    request_started.connect(update_translations)
else:
    translation_loader.update()

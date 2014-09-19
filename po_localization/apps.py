# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .models import handle_settings_change

try:
    from django.apps import AppConfig
except ImportError:
    class AppConfig(object):
        pass


class PoLocalizationConfig(AppConfig):
    name = 'po_localization'
    verbose_name = 'po localization'

    def ready(self):
        handle_settings_change()

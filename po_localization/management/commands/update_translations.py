# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Update translation files'

    def handle(self, *args, **options):
        from ...middleware import PoLocalizationMiddleware
        po_localization_middleware = PoLocalizationMiddleware()
        po_localization_middleware.translations_updater.execute()

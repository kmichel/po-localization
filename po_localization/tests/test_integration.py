# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import django
from django.conf import settings
from django.core import management

if not settings.configured:
    settings.configure()
    django_setup = getattr(django, 'setup', lambda: None)
    django_setup()

import io
import os
import shutil
import sys
import tempfile
import time
import unittest
from django.test import SimpleTestCase
from django.utils import translation
from po_localization.tests.subtest import SubprocessTestCase


class IntegrationTestCase(SubprocessTestCase, SimpleTestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'test_app'), os.path.join(self.temp_dir, 'test_app'))
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'test_project'), os.path.join(self.temp_dir, 'test_project'))
        sys.path.insert(0, self.temp_dir)
        self.locale_path = os.path.join(self.temp_dir, 'test_app/locale')

    def tearDown(self):
        sys.path.remove(self.temp_dir)
        shutil.rmtree(self.temp_dir)

    def test_simple(self):
        local_settings = {
            'ALLOWED_HOSTS': ['*'],
            'AUTO_RELOAD_TRANSLATIONS': True,
            'AUTO_UPDATE_TRANSLATIONS': True,
            'UPDATE_TRANSLATIONS_PACKAGES': (
                'test_app',
            ),
            'UPDATE_TRANSLATIONS_EXCLUDED_LOCALES': (
                'en',
            ),
            'MIDDLEWARE_CLASSES': (
                'po_localization.middleware.PoLocalizationMiddleware',
            ),
            'INSTALLED_APPS': (
                'po_localization',
                'test_app',
            ),
            'LANGUAGE_CODE': 'fr',
            'LANGUAGES': (
                ('fr', 'French'),
                ('en', 'English'),
            ),
            'ROOT_URLCONF': 'test_app.urls',
        }
        with self.settings(**local_settings):
            self.client.get('')
            self.assertTrue(os.path.exists(self.locale_path))
            french_translation_filename = os.path.join(self.locale_path, 'fr/LC_MESSAGES/django.po')
            self.assertTrue(os.path.isfile(french_translation_filename))
            english_translation_filename = os.path.join(self.locale_path, 'en/LC_MESSAGES/django.po')
            self.assertFalse(os.path.exists(english_translation_filename))

            with io.open(french_translation_filename, 'r', encoding='utf-8') as translation_file:
                self.assertEqual(
                    translation_file.read(),
"""#: models.py:12
msgid "test field"
msgstr ""

#: templates/index.html:8
msgid "test template"
msgstr ""

#: templates/index.html:10
msgid "%(counter)s item"
msgid_plural "%(counter)s items"
msgstr[0] ""
msgstr[1] ""

#: views.py:12
msgctxt "view context"
msgid "test view string"
msgstr ""
""")
            self.assertEqual("test field", translation.ugettext("test field"))
            # This sleep is required because mtimes do not have a high enough resolution
            time.sleep(1)
            with io.open(french_translation_filename, 'w', encoding='utf-8') as translation_file:
                translation_file.write(
"""
msgid "test field"
msgstr "champ de test"

msgid "test template"
msgstr "template de test"

msgid "%(counter)s item"
msgid_plural "%(counter)s items"
msgstr[0] "%(counter)s élément"
msgstr[1] "%(counter)s éléments"

msgctxt "view context"
msgid "test view string"
msgstr "chaîne de vue de test"
""")
            # No request triggered, still not translated
            self.assertEqual("test field", translation.ugettext("test field"))
            self.assertEqual("test template", translation.ugettext("test template"))
            self.assertEqual("test view string", translation.pgettext("view context", "test view string"))
            self.assertEqual("%(counter)s items", translation.ungettext("%(counter)s item", "%(counter)s items", 2))
            # Trigger a request, should reload translations
            self.assertEqual("chaîne de vue de test", self.client.get('').content.decode('utf-8'))
            self.assertEqual("champ de test", translation.ugettext("test field"))
            self.assertEqual("template de test", translation.ugettext("test template"))
            self.assertEqual("chaîne de vue de test", translation.pgettext("view context", "test view string"))
            self.assertEqual("%(counter)s éléments", translation.ungettext("%(counter)s item", "%(counter)s items", 2))

            # Test file update
            with io.open(os.path.join(self.temp_dir, 'test_app/models.py'), 'a', encoding='utf-8') as models_file:
                models_file.write('    second_field=models.TextField(verbose_name=_(\'second field\'))')
            self.client.get('')
            with io.open(french_translation_filename, 'r', encoding='utf-8') as translation_file:
                self.assertEqual(
                    translation_file.read(),
"""#: models.py:12
msgid "test field"
msgstr "champ de test"

#: models.py:13
msgid "second field"
msgstr ""

#: templates/index.html:8
msgid "test template"
msgstr "template de test"

#: templates/index.html:10
msgid "%(counter)s item"
msgid_plural "%(counter)s items"
msgstr[0] "%(counter)s élément"
msgstr[1] "%(counter)s éléments"

#: views.py:12
msgctxt "view context"
msgid "test view string"
msgstr "chaîne de vue de test"
""")
            # Test file removal
            os.unlink(os.path.join(self.temp_dir, 'test_app/views.py'))
            self.client.get('')
            with io.open(french_translation_filename, 'r', encoding='utf-8') as translation_file:
                self.assertEqual(
                    translation_file.read(),
"""#. obsolete entry
msgctxt "view context"
msgid "test view string"
msgstr "cha\xeene de vue de test"

#: models.py:12
msgid "test field"
msgstr "champ de test"

#: models.py:13
msgid "second field"
msgstr ""

#: templates/index.html:8
msgid "test template"
msgstr "template de test"

#: templates/index.html:10
msgid "%(counter)s item"
msgid_plural "%(counter)s items"
msgstr[0] "%(counter)s élément"
msgstr[1] "%(counter)s éléments"
""")
            with self.settings(UPDATE_TRANSLATIONS_PRUNE_OBSOLETES=True):
                self.client.get('')
                with io.open(french_translation_filename, 'r', encoding='utf-8') as translation_file:
                    self.assertEqual(
                        translation_file.read(),
"""#: models.py:12
msgid "test field"
msgstr "champ de test"

#: models.py:13
msgid "second field"
msgstr ""

#: templates/index.html:8
msgid "test template"
msgstr "template de test"

#: templates/index.html:10
msgid "%(counter)s item"
msgid_plural "%(counter)s items"
msgstr[0] "%(counter)s élément"
msgstr[1] "%(counter)s éléments"
""")

    def test_management_command(self):
        local_settings = {
            'AUTO_UPDATE_TRANSLATIONS': False,
            'INSTALLED_APPS': (
                'po_localization',
                'test_app',
            ),
            'MIDDLEWARE_CLASSES': (
                'po_localization.middleware.PoLocalizationMiddleware',
            ),
            'UPDATE_TRANSLATIONS_PACKAGES': (
                'test_app',
            ),
        }
        with self.settings(**local_settings):
            self.assertFalse(os.path.exists(self.locale_path))
            management.call_command('update_translations')
            self.assertTrue(os.path.exists(self.locale_path))

    def test_custom_locale_paths(self):
        local_settings = {
            'AUTO_RELOAD_TRANSLATIONS': True,
            'INSTALLED_APPS': (
                'po_localization',
            ),
            'MIDDLEWARE_CLASSES': (
                'po_localization.middleware.PoLocalizationMiddleware',
            ),
            'LOCALE_PATHS': (
                os.path.join(self.temp_dir, 'test_project/locale'),
            ),
            'LANGUAGE_CODE': 'fr',
            'LANGUAGES': (
                ('fr', 'French'),
                ('en', 'English'),
            ),
            'ROOT_URLCONF': 'test_project.urls'
        }
        with self.settings(**local_settings):
            response = self.client.get('')
            self.assertEqual("chaîne de test de projet", response.content.decode('utf-8'))

    @unittest.skipIf(django.VERSION[:2] < (1, 7), "app registry not available in django<1.7")
    def test_app_registry(self):
        local_settings = {
            'ALLOWED_HOSTS': ['*'],
            'AUTO_RELOAD_TRANSLATIONS': True,
            'AUTO_UPDATE_TRANSLATIONS': False,
            'MIDDLEWARE_CLASSES': (
                'po_localization.middleware.PoLocalizationMiddleware',
            ),
            'INSTALLED_APPS': (
                'po_localization',
                'test_app.apps.TestAppConfig',
            ),
            'LANGUAGE_CODE': 'fr',
            'LANGUAGES': (
                ('fr', 'French'),
                ('en', 'English'),
            ),
            'ROOT_URLCONF': 'test_app.urls',
        }
        with self.settings(**local_settings):
            french_translation_filename = os.path.join(self.locale_path, 'fr/LC_MESSAGES/django.po')
            os.makedirs(os.path.dirname(french_translation_filename))
            with io.open(french_translation_filename, 'w', encoding='utf-8') as translation_file:
                translation_file.write(
"""
msgid "test field"
msgstr "champ de test"

msgid "test template"
msgstr "template de test"

msgid "%(counter)s item"
msgid_plural "%(counter)s items"
msgstr[0] "%(counter)s élément"
msgstr[1] "%(counter)s éléments"

msgctxt "view context"
msgid "test view string"
msgstr "chaîne de vue de test"
""")
            self.assertEqual("chaîne de vue de test", self.client.get('').content.decode('utf-8'))

    def test_auto_reload_disabled(self):
        local_settings = {
            'AUTO_RELOAD_TRANSLATIONS': False,
            'INSTALLED_APPS': (
                'po_localization',
            ),
            'MIDDLEWARE_CLASSES': (
                'po_localization.middleware.PoLocalizationMiddleware',
            ),
            'LOCALE_PATHS': (
                os.path.join(self.temp_dir, 'test_project/locale'),
            ),
            'LANGUAGE_CODE': 'fr',
            'LANGUAGES': (
                ('fr', 'French'),
                ('en', 'English'),
            ),
            'ROOT_URLCONF': 'test_project.urls'
        }
        with self.settings(**local_settings):
            self.client.get('')
            self.assertEqual("chaîne de test de projet", translation.ugettext("test project string"))
            translation_filename = os.path.join(self.temp_dir, 'test_project/locale/fr/LC_MESSAGES/django.po')
            with io.open(translation_filename, 'a', encoding='utf-8') as translation_file:
                translation_file.write(
"""
msgid "extra translation"
msgstr "translation supplémentaire"
""")
            self.client.get('')
            self.assertEqual("extra translation", translation.ugettext("extra translation"))

# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import django
from django.conf import settings

if not settings.configured:
    settings.configure()
    django_setup = getattr(django, 'setup', lambda: None)
    django_setup()

import io
import os
import shutil
import sys
import tempfile
from django.test import SimpleTestCase
from django.utils.importlib import import_module
from django.utils import translation
from po_localization.models import handle_settings_change

SETTINGS = {
    'ALLOWED_HOSTS': ['*'],
    'AUTO_RELOAD_TRANSLATIONS': True,
    'AUTO_UPDATE_TRANSLATIONS': True,
    'UPDATE_TRANSLATIONS_PACKAGES': (
        'test_app',
    ),
    'UPDATE_TRANSLATIONS_EXCLUDED_LOCALES': (
        'en',
    ),
    'INSTALLED_APPS': (
        'test_app',
    ),
    'LANGUAGE_CODE': 'fr',
    'LANGUAGES': (
        ('fr', 'French'),
        ('en', 'English'),
    ),
    'ROOT_URLCONF': 'test_app.urls',
}


class IntegrationTestCase(SimpleTestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'test_app'), os.path.join(self.temp_dir, 'test_app'))
        sys.path.insert(0, self.temp_dir)
        self.locale_path = self.get_test_app_locale_path()

    def tearDown(self):
        sys.path.remove(self.temp_dir)
        shutil.rmtree(self.temp_dir)

    def test_simple(self):
        try:
            with self.settings(**SETTINGS):
                handle_settings_change()

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

#: views.py:12
msgid "test view string"
msgstr ""
""")
                self.assertEqual("test field", translation.ugettext("test field"))
                with io.open(french_translation_filename, 'w', encoding='utf-8') as translation_file:
                    translation_file.write(
"""
msgid "test field"
msgstr "champ de test"

msgid "test template"
msgstr "template de test"

msgid "test view string"
msgstr "chaîne de vue de test"
""")
                # No request triggered, still not translated
                self.assertEqual("test field", translation.ugettext("test field"))
                self.assertEqual("test template", translation.ugettext("test template"))
                self.assertEqual("test view string", translation.ugettext("test view string"))
                # Trigger a request, should reload translations
                self.assertEqual("chaîne de vue de test", self.client.get('').content.decode('utf-8'))
                self.assertEqual("champ de test", translation.ugettext("test field"))
                self.assertEqual("template de test", translation.ugettext("test template"))

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

#: views.py:12
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
""")
                with self.settings(UPDATE_TRANSLATIONS_PRUNE_OBSOLETES=True):
                    handle_settings_change()
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
""")
        finally:
            if os.path.exists(self.locale_path):
                shutil.rmtree(self.locale_path)

    def get_test_app_locale_path(self):
        test_app = import_module('test_app')
        test_app_path = os.path.dirname(test_app.__file__)
        return os.path.join(test_app_path, 'locale')

# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from unittest import TestCase
from po_localization.po_file import PoFile
from po_localization.template_extractor import extract_messages


class TemplateExtractorTestCase(TestCase):
    def setUp(self):
        po_file = PoFile()
        extract_messages(os.path.join(os.path.dirname(__file__), 'sample.html'), po_file)
        self.po_keys = po_file.entries.keys()

    def test_simple(self):
        self.assertIn("simple translation", self.po_keys)
        self.assertIn("translation to variable", self.po_keys)

    def test_context(self):
        self.assertIn("context\x04translation with context", self.po_keys)

    def test_block(self):
        self.assertIn("simple block translation", self.po_keys)
        self.assertIn("context\x04block translation with context", self.po_keys)

    def test_plural(self):
        self.assertIn("%(counter)s block translation", self.po_keys)
        self.assertIn("context\x04%(counter)s block translation with context", self.po_keys)

    def test_requires_i18n(self):
        self.assertNotIn("ignored translation before loading i18n", self.po_keys)

    def test_ignore_variable_translations(self):
        self.assertNotIn("ignored_variable_translation", self.po_keys)
        self.assertNotIn("ignored translation with variable context", self.po_keys)
        self.assertNotIn("variable_context\x04,ignored translation with variable context", self.po_keys)
        self.assertNotIn("ignored block translation with variable context", self.po_keys)
        self.assertNotIn("variable_context\x04,ignored block translation with variable context", self.po_keys)
        self.assertNotIn("ignored %(counter)s block translation with variable context", self.po_keys)
        self.assertNotIn("variable_context\x04ignored %(counter)s block translation with variable context", self.po_keys)

    def test_ignore_filtered_constants(self):
        self.assertNotIn("ignored translation with filter", self.po_keys)
        self.assertNotIn("ignored translation with filtered context", self.po_keys)
        self.assertNotIn("context\x04ignored translation with filtered context", self.po_keys)




# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from unittest import TestCase
from po_localization.po_file import PoFile
from po_localization.python_extractor import extract_messages


class PythonExtractorTestCase(TestCase):
    def test_full_module(self):
        po_file = PoFile()
        extract_messages(os.path.join(os.path.dirname(__file__), 'sample.py'), po_file, 'sample.py')
        po_keys = po_file.entries.keys()
        self.assertIn('test', po_keys)
        self.assertIn('test_lazy', po_keys)
        self.assertIn('test_noop', po_keys)
        self.assertIn('utest', po_keys)
        self.assertIn('utest_lazy', po_keys)
        self.assertIn('utest_noop', po_keys)
        self.assertIn('context\x04ptest', po_keys)
        self.assertIn('context\x04ptest_lazy', po_keys)
        self.assertIn('context\x04ptest', po_keys)
        self.assertIn('ntest', po_keys)
        self.assertIn('ntest_lazy', po_keys)
        self.assertIn('untest', po_keys)
        self.assertIn('untest_lazy', po_keys)
        self.assertIn('context\x04nptest', po_keys)
        self.assertIn('context\x04nptest_lazy', po_keys)

    def test_module_alias(self):
        po_file = PoFile()
        extract_messages(os.path.join(os.path.dirname(__file__), 'sample.py'), po_file, 'sample.py')
        po_keys = po_file.entries.keys()
        self.assertIn('test', po_keys)
        self.assertIn('test_lazy', po_keys)
        self.assertIn('test_noop', po_keys)
        self.assertIn('utest', po_keys)
        self.assertIn('utest_lazy', po_keys)
        self.assertIn('utest_noop', po_keys)
        self.assertIn('context\x04ptest', po_keys)
        self.assertIn('context\x04ptest_lazy', po_keys)
        self.assertIn('context\x04ptest', po_keys)
        self.assertIn('ntest', po_keys)
        self.assertIn('ntest_lazy', po_keys)
        self.assertIn('untest', po_keys)
        self.assertIn('untest_lazy', po_keys)
        self.assertIn('context\x04nptest', po_keys)
        self.assertIn('context\x04nptest_lazy', po_keys)

    def test_module_alias_2(self):
        po_file = PoFile()
        extract_messages(os.path.join(os.path.dirname(__file__), 'sample.py'), po_file, 'sample.py')
        po_keys = po_file.entries.keys()
        self.assertIn('tm2_test', po_keys)
        self.assertIn('tm2_test_lazy', po_keys)
        self.assertIn('tm2_test_noop', po_keys)
        self.assertIn('tm2_utest', po_keys)
        self.assertIn('tm2_utest_lazy', po_keys)
        self.assertIn('tm2_utest_noop', po_keys)
        self.assertIn('context\x04tm2_ptest', po_keys)
        self.assertIn('context\x04tm2_ptest_lazy', po_keys)
        self.assertIn('context\x04tm2_ptest', po_keys)
        self.assertIn('tm2_ntest', po_keys)
        self.assertIn('tm2_ntest_lazy', po_keys)
        self.assertIn('tm2_untest', po_keys)
        self.assertIn('tm2_untest_lazy', po_keys)
        self.assertIn('context\x04tm2_nptest', po_keys)
        self.assertIn('context\x04tm2_nptest_lazy', po_keys)

    def test_function_aliases(self):
        po_file = PoFile()
        extract_messages(os.path.join(os.path.dirname(__file__), 'sample.py'), po_file, 'sample.py')
        po_keys = po_file.entries.keys()
        self.assertIn('alias_test', po_keys)
        self.assertIn('alias_test_lazy', po_keys)
        self.assertIn('alias_test_noop', po_keys)
        self.assertIn('alias_utest', po_keys)
        self.assertIn('alias_utest_lazy', po_keys)
        self.assertIn('alias_utest_noop', po_keys)
        self.assertIn('context\x04alias_ptest', po_keys)
        self.assertIn('context\x04alias_ptest_lazy', po_keys)
        self.assertIn('context\x04alias_ptest', po_keys)
        self.assertIn('alias_ntest', po_keys)
        self.assertIn('alias_ntest_lazy', po_keys)
        self.assertIn('alias_untest', po_keys)
        self.assertIn('alias_untest_lazy', po_keys)
        self.assertIn('context\x04alias_nptest', po_keys)
        self.assertIn('context\x04alias_nptest_lazy', po_keys)

    def test_scoping(self):
        po_file = PoFile()
        extract_messages(os.path.join(os.path.dirname(__file__), 'sample.py'), po_file, 'sample.py')
        po_keys = po_file.entries.keys()
        self.assertNotIn('not a translation', po_keys)
        self.assertIn('a translation', po_keys)
        self.assertNotIn('still not a translation', po_keys)

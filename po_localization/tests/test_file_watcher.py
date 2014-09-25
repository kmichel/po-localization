# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile
import time
from unittest import TestCase
from po_localization.file_watcher import FileWatcher


class FileWatcherTestCase(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_empty(self):
        operator = TestOperator()
        file_watcher = FileWatcher(operator)
        file_watcher.check()
        self.assertEqual(1, operator.list_files_calls)
        self.assertEqual(1, operator.execute_calls)
        file_watcher.check()
        self.assertEqual(2, operator.list_files_calls)
        self.assertEqual(1, operator.execute_calls)
        file_watcher.set_dirty()
        self.assertEqual(2, operator.list_files_calls)
        self.assertEqual(1, operator.execute_calls)
        file_watcher.check()
        self.assertEqual(3, operator.list_files_calls)
        self.assertEqual(2, operator.execute_calls)
        file_watcher.check()
        self.assertEqual(4, operator.list_files_calls)
        self.assertEqual(2, operator.execute_calls)

    def test_add_file_to_list(self):
        file_path = os.path.join(self.temp_dir, 'file.ext')
        with open(file_path, 'w'):
            pass
        operator = TestOperator()
        file_watcher = FileWatcher(operator)
        file_watcher.check()
        self.assertEqual(1, operator.list_files_calls)
        self.assertEqual(1, operator.execute_calls)
        operator.files_list = (__file__,)
        file_watcher.check()
        self.assertEqual(2, operator.list_files_calls)
        self.assertEqual(2, operator.execute_calls)

    def test_touch_file(self):
        file_path = os.path.join(self.temp_dir, 'file.ext')
        with open(file_path, 'w'):
            pass
        start_time = time.time()
        operator = TestOperator((file_path,))
        os.utime(file_path, (0, start_time))
        file_watcher = FileWatcher(operator)
        file_watcher.check()
        self.assertEqual(1, operator.list_files_calls)
        self.assertEqual(1, operator.execute_calls)
        file_watcher.check()
        self.assertEqual(2, operator.list_files_calls)
        self.assertEqual(1, operator.execute_calls)
        os.utime(file_path, (0, start_time + 1))
        file_watcher.check()
        self.assertEqual(3, operator.list_files_calls)
        self.assertEqual(2, operator.execute_calls)

    def test_remove_file(self):
        file_path = os.path.join(self.temp_dir, 'file.ext')
        with open(file_path, 'w'):
            pass
        operator = TestOperator((file_path,))
        file_watcher = FileWatcher(operator)
        file_watcher.check()
        self.assertEqual(1, operator.list_files_calls)
        self.assertEqual(1, operator.execute_calls)
        os.unlink(file_path)
        file_watcher.check()
        self.assertEqual(2, operator.list_files_calls)
        self.assertEqual(2, operator.execute_calls)

    def test_remove_file_from_list(self):
        file_path = os.path.join(self.temp_dir, 'file.ext')
        with open(file_path, 'w'):
            pass
        operator = TestOperator((file_path,))
        file_watcher = FileWatcher(operator)
        file_watcher.check()
        self.assertEqual(1, operator.list_files_calls)
        self.assertEqual(1, operator.execute_calls)
        operator.files_list = ()
        file_watcher.check()
        self.assertEqual(2, operator.list_files_calls)
        self.assertEqual(2, operator.execute_calls)


class TestOperator(object):
    def __init__(self, files_list=()):
        self.files_list = files_list
        self.execute_calls = 0
        self.list_files_calls = 0

    def execute(self):
        self.execute_calls += 1

    def list_files(self):
        self.list_files_calls += 1
        return self.files_list

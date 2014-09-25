# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import threading


class FileWatcher(object):
    def __init__(self, operator):
        self.operator = operator
        self.file_mtimes = {}
        self.is_dirty = True
        self.lock = threading.Lock()

    def set_dirty(self):
        self.is_dirty = True

    def check(self):
        with self.lock:
            self._check_for_changes()
            if self.is_dirty:
                self.operator.execute()
                self.is_dirty = False

    def _check_for_changes(self):
        files_list = set(self.operator.list_files())
        for file_path in list(self.file_mtimes.keys()):
            if file_path not in files_list:
                self.is_dirty = True
                del self.file_mtimes[file_path]
        for file_path in files_list:
            if os.path.isfile(file_path):
                file_mtime = get_file_mtime(file_path)
                if file_path not in self.file_mtimes or self.file_mtimes[file_path] != file_mtime:
                    self.file_mtimes[file_path] = file_mtime
                    self.is_dirty = True
            elif file_path in self.file_mtimes:
                self.is_dirty = True
                del self.file_mtimes[file_path]


def get_file_mtime(filename):
    stat = os.stat(filename)
    mtime = stat.st_mtime
    if sys.platform == 'win32':
        mtime -= stat.st_ctime
    return mtime

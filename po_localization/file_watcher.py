# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import threading


class FileWatcher(object):
    def __init__(self):
        self.file_mtimes = {}
        self.is_dirty = True
        self.lock = threading.Lock()

    def reload(self):
        with self.lock:
            if not self.is_dirty:
                self._check_for_changes()
            if self.is_dirty:
                self.do_load()
                self.is_dirty = False

    def do_load(self):
        pass

    def list_files(self):
        return ()

    def _check_for_changes(self):
        files_list = set(self.list_files())
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

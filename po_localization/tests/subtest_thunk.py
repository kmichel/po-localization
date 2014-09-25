# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import base64
from importlib import import_module
import os
import pickle
import sys
from po_localization.tests.subtest import PicklableTestResult, print_bytes

if __name__ == '__main__':
    if 'COVERAGE_PROCESS_START' in os.environ:
        import coverage
        coverage.process_startup()
    module_name, class_name, method_name = sys.argv[1:]
    module = import_module(module_name)
    test_case_class = getattr(module, class_name)
    test_case = test_case_class(method_name)
    result = PicklableTestResult()
    test_case(result)
    pickled_result = pickle.dumps(result.storage, protocol=pickle.HIGHEST_PROTOCOL)
    encoded_result = base64.encodestring(pickled_result)
    print_bytes(b'-')
    print_bytes(encoded_result)

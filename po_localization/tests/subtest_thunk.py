# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from importlib import import_module
import pickle
import sys
from po_localization.tests.subtest import PicklableTestResult

if __name__ == '__main__':
    module_name, class_name, method_name = sys.argv[1:]
    module = import_module(module_name)
    test_case_class = getattr(module, class_name)
    test_case = test_case_class(method_name)
    result = PicklableTestResult()
    test_case(result)
    output = sys.stdout.buffer if hasattr(sys.stdout, 'buffer') else sys.stdout
    pickle.dump(result.storage, output, protocol=pickle.HIGHEST_PROTOCOL)

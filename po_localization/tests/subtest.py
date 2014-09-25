# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import base64
import os
import pickle
import subprocess
import sys
from unittest import TestCase, TestResult


class SubprocessTestCase(TestCase):
    def __call__(self, result=None):
        if result is not None and isinstance(result, PicklableTestResult):
            super(SubprocessTestCase, self).__call__(result)
        else:
            orig_result = result
            if result is None:
                result = self.defaultTestResult()
                start_test_run = getattr(result, 'startTestRun', None)
                if start_test_run is not None and callable(start_test_run):
                    start_test_run()

            self._resultForDoCleanups = result
            result.startTest(self)
            try:
                test_module_name = self.__class__.__module__
                test_class_name = self.__class__.__name__
                test_method_name = self._testMethodName
                subtest_thunk = os.path.join(os.path.dirname(__file__), 'subtest_thunk.py')
                args = [sys.executable, subtest_thunk, test_module_name, test_class_name, test_method_name]
                environment = os.environ
                if 'coverage' in sys.modules:
                    environment = environment.copy()
                    environment['COVERAGE_PROCESS_START'] = '.coveragerc'
                proc = subprocess.Popen(args, stdout=subprocess.PIPE, env=environment)
                stdout_content, nothing = proc.communicate()
                if proc.returncode != 0:
                    print_bytes(stdout_content)
                    raise subprocess.CalledProcessError(proc.returncode, args)
                else:
                    user_stdout_content, separator, encoded_data = stdout_content.rpartition(b'-')
                    print_bytes(user_stdout_content)
                    decoded_data = base64.decodestring(encoded_data)
                    result_actions = pickle.loads(decoded_data)
                    for action, arguments in result_actions:
                        getattr(result, action)(*arguments)
            finally:
                result.stopTest(self)
                if orig_result is None:
                    stop_test_run = getattr(result, 'stopTestRun', None)
                    if stop_test_run is not None and callable(stop_test_run):
                        stop_test_run()


def print_bytes(content):
    output = sys.stdout.buffer if hasattr(sys.stdout, 'buffer') else sys.stdout
    sys.stdout.flush()
    output.write(content)
    output.flush()


class PicklableTestResult(TestResult):
    def __init__(self, *args, **kwargs):
        super(PicklableTestResult, self).__init__(*args, **kwargs)
        self.storage = []

    def addError(self, test, err):
        self.storage.append(('addError', (PicklableTest(test), get_picklable_exc_info(err))))

    def addExpectedFailure(self, test, err):
        self.storage.append(('addExpectedFailure', (PicklableTest(test), get_picklable_exc_info(err))))

    def addFailure(self, test, err):
        self.storage.append(('addFailure', (PicklableTest(test), get_picklable_exc_info(err))))

    def addSkip(self, test, reason):
        self.storage.append(('addSkip', (PicklableTest(test), reason)))

    def addSuccess(self, test):
        self.storage.append(('addSuccess', (PicklableTest(test),)))

    def addUnexpectedSuccess(self, test):
        self.storage.append(('addUnexpectedSuccess', (PicklableTest(test),)))


class PicklableTest(object):
    def __init__(self, test):
        self.failureException = test.failureException
        self._testMethodName = getattr(test, '_testMethodName', None)
        self._shortDescription = test.shortDescription()
        self._str = test.__str__()
        self._repr = test.__repr__()

    def shortDescription(self):
        return self._shortDescription

    def __str__(self):
        return self._str

    def __repr__(self):
        return self._repr


def get_picklable_exc_info(exc_info):
    exception_type, exception_value, traceback = exc_info
    return exception_type, exception_value, PicklableTraceback(traceback)


class PicklableTraceback(object):
    def __init__(self, traceback):
        self.tb_frame = PicklableTracebackFrame(traceback.tb_frame)
        self.tb_lineno = traceback.tb_lineno
        self.tb_next = None if traceback.tb_next is None else PicklableTraceback(traceback.tb_next)


class PicklableTracebackFrame(object):
    def __init__(self, traceback_frame):
        self.f_code = PicklableCode(traceback_frame.f_code)
        self.f_globals = dict((key, None) for key in traceback_frame.f_globals.keys())


class PicklableCode(object):
    def __init__(self, code):
        self.co_filename = code.co_filename
        self.co_name = code.co_name

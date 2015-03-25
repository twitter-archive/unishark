# Copyright 2015 Twitter, Inc and other contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import traceback
import unittest
import time
from unishark.util import (get_long_class_name, get_long_method_name, get_module_name)
import threading
from collections import deque
from inspect import ismodule


_str_io = None
if sys.version_info[0] < 3:  # python 2.7
    _str_io = __import__('StringIO')
else:
    _str_io = __import__('io')

if _str_io is None or not ismodule(_str_io):
    raise ImportError


def _make_buffer():
    return _str_io.StringIO()


class _PooledIOBuffer():
    _lock = threading.RLock()

    def __init__(self):
        self.buff_queue = deque()
        self.buff_queue.append(_make_buffer())
        self.buff_dict = dict()

    def _get_buff(self):
        with _PooledIOBuffer._lock:
            if not self.buff_queue:
                return _make_buffer()
            else:
                return self.buff_queue.popleft()

    def write(self, *args, **kwargs):
        i = threading.current_thread().ident
        if i not in self.buff_dict:
            buff = self._get_buff()
            self.buff_dict[i] = buff
        self.buff_dict[i].write(*args, **kwargs)

    def getvalue(self, *args, **kwargs):
        i = threading.current_thread().ident
        return self.buff_dict[i].getvalue(*args, **kwargs) if i in self.buff_dict else None

    def flush(self, *args, **kwargs):
        i = threading.current_thread().ident
        if i in self.buff_dict:
            self.buff_dict[i].flush(*args, **kwargs)

    def seek(self, *args, **kwargs):
        i = threading.current_thread().ident
        if i in self.buff_dict:
            self.buff_dict[i].seek(*args, **kwargs)

    def truncate(self, *args, **kwargs):
        i = threading.current_thread().ident
        if i in self.buff_dict:
            self.buff_dict[i].truncate(*args, **kwargs)

    def free(self):
        i = threading.current_thread().ident
        if i in self.buff_dict:
            buff = self.buff_dict.pop(threading.current_thread().ident)
            buff.seek(0)
            buff.truncate()
            self.buff_queue.append(buff)


_io_buffer = _PooledIOBuffer()
out = _io_buffer

PASS = 0
SKIPPED = 1
ERROR = 2
FAIL = 3
EXPECTED_FAIL = 4
UNEXPECTED_PASS = 5


class BufferedTestResult(unittest.TextTestResult):
    # TODO make this class thread-safe
    def __init__(self, stream, descriptions, verbosity):
        super(BufferedTestResult, self).__init__(stream, descriptions, verbosity)
        self.buffer = False
        # key = test class name, value = a list of results.
        # One result is a tuple like (test method name, method doc, duration, status, output, traceback)
        self.results = dict()
        self.start_time = 0.0
        self.sum_duration = 0.0
        self.successes = 0

    def _add_result(self, test, duration, status, output, trace_back):
        mod_name = get_module_name(test)
        cls_name = get_long_class_name(test)
        if mod_name not in self.results:
            self.results[mod_name] = dict()
        if cls_name not in self.results[mod_name]:
            self.results[mod_name][cls_name] = []
        test_name, test_doc = self.__class__._get_test_info(test)
        output = output or 'No Log\n'
        trace_back = trace_back or 'No Exception\n'
        self.results[mod_name][cls_name].append((test_name, test_doc, duration, status, output, trace_back))

    @staticmethod
    def _get_test_info(test):
        test_name = get_long_method_name(test)
        test_doc = getattr(test, '_testMethodDoc')
        return test_name, test_doc or 'No Method Doc\n'

    def _exc_info_to_string(self, error, test):
        """Almost the same as its base class implementation, except eliminating the mirror output"""
        exctype, value, tb = error
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            msg_lines = traceback.format_exception(exctype, value, tb, length)
        else:
            msg_lines = traceback.format_exception(exctype, value, tb)
        return ''.join(msg_lines)

    def startTest(self, test):
        super(BufferedTestResult, self).startTest(test)
        self.start_time = time.time()

    def stopTest(self, test):
        self._mirrorOutput = False
        _io_buffer.free()

    def addSuccess(self, test):
        duration = time.time() - self.start_time
        super(BufferedTestResult, self).addSuccess(test)
        self.successes += 1
        self._add_result(test, duration, PASS, _io_buffer.getvalue(), '')

    def addError(self, test, error):
        duration = time.time() - self.start_time
        super(BufferedTestResult, self).addError(test, error)
        test_obj, exception_str = self.errors[-1]
        self._add_result(test, duration, ERROR, _io_buffer.getvalue(), exception_str)

    def addFailure(self, test, error):
        duration = time.time() - self.start_time
        super(BufferedTestResult, self).addFailure(test, error)
        test_obj, exception_str = self.failures[-1]
        self._add_result(test, duration, FAIL, _io_buffer.getvalue(), exception_str)

    def addSkip(self, test, reason):
        duration = time.time() - self.start_time
        super(BufferedTestResult, self).addSkip(test, reason)
        test_obj, reason = self.skipped[-1]
        self._add_result(test, duration, SKIPPED, _io_buffer.getvalue(), 'Skipped: {0!r}'.format(reason))

    def addExpectedFailure(self, test, error):
        duration = time.time() - self.start_time
        super(BufferedTestResult, self).addExpectedFailure(test, error)
        test_obj, exception_str = self.expectedFailures[-1]
        self._add_result(test, duration, EXPECTED_FAIL, _io_buffer.getvalue(), exception_str)

    def addUnexpectedSuccess(self, test):
        duration = time.time() - self.start_time
        super(BufferedTestResult, self).addUnexpectedSuccess(test)
        self._add_result(test, duration, UNEXPECTED_PASS, _io_buffer.getvalue(), '')

    def wasSuccessful(self):
        return len(self.failures) == len(self.errors) == len(self.unexpectedSuccesses) == 0


class BufferedTestRunner(unittest.TextTestRunner):
    def __init__(self, reporters, verbosity=1, descriptions=False):
        super(BufferedTestRunner, self).__init__(buffer=False,
                                                 verbosity=verbosity,
                                                 descriptions=descriptions,
                                                 resultclass=BufferedTestResult)
        self.reporters = reporters

    def run(self, test):
        start_time = time.time()
        result = super(BufferedTestRunner, self).run(test)
        result.sum_duration = time.time() - start_time
        from unishark.reporter import Reporter
        for reporter in self.reporters:
            if not isinstance(reporter, Reporter):
                raise TypeError
        for reporter in self.reporters:
            reporter.report(result)
        return result
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

from unittest import TextTestRunner
from unishark.suite import TestSuite, convert
from unishark.result import BufferedTestResult, out, WritelnDecorator
from unishark.reporter import Reporter
from unittest.signals import registerResult
import time
import warnings
import logging
from sys import stderr

log = logging.getLogger(__name__)

_concurrency_level_to_int = {
    'none': TestSuite.ROOT_LEVEL,
    'module': TestSuite.MODULE_LEVEL,
    'class': TestSuite.CLASS_LEVEL,
    'method': TestSuite.METHOD_LEVEL
}


class BufferedTestRunner(TextTestRunner):
    def __init__(self, reporters=None, verbosity=1, descriptions=False):
        super(BufferedTestRunner, self).__init__(buffer=False,
                                                 verbosity=verbosity,
                                                 descriptions=descriptions,
                                                 resultclass=BufferedTestResult)
        if reporters:
            self.reporters = reporters
        else:
            self.reporters = []
        for reporter in self.reporters:
            if not isinstance(reporter, Reporter):
                raise TypeError

    def __getstate__(self):
        # called before pickling
        state = self.__dict__.copy()
        if 'stream' in state:
            del state['stream']
        return state

    def __setstate__(self, state):
        # called while unpickling
        self.__dict__.update(state)
        self.__dict__['stream'] = WritelnDecorator(stderr)

    def make_result(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

    def make_results_tree(self, test, result):
        if self.__class__._is_suite(test):
            result.children = [self.make_result() for _ in test]
            for t, r in zip(test, result.children):
                self.make_results_tree(t, r)

    def _before_run(self):
        # Keep the same as lines 145-162 in unittest.TextTextRunner.run
        result = self.make_result()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        with warnings.catch_warnings():
            warn = getattr(self, 'warnings', None)
            if warn:
                warnings.simplefilter(warn)
                if warn in ['default', 'always']:
                    warnings.filterwarnings('module',
                                            category=DeprecationWarning,
                                            message='Please use assert\w+ instead.')
        return result

    def _after_run(self, result):
        # Almost the same as lines 175-213 in unittest.TextTextRunner.run,
        # with small fix of counting unexpectedSuccesses into a FAILED run.
        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", result.sum_duration))
        self.stream.writeln()

        expected = unexpected = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expected, unexpected, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
            if unexpected:
                infos.append("unexpected successes=%d" % unexpected)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expected:
            infos.append("expected failures=%d" % expected)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")

    @staticmethod
    def _is_suite(test):
        try:
            iter(test)
        except TypeError:
            return False
        return True

    def run(self, test, name='test', description='', max_workers=1, concurrency_level='class', timeout=None):
        result = self._before_run()
        result.name = name
        result.description = description
        start_time = time.time()
        start_test_run = getattr(result, 'startTestRun', None)
        if start_test_run is not None:
            start_test_run()
        try:
            if not self.__class__._is_suite(test):
                test(result)
            else:
                test = convert(test)
                self.make_results_tree(test, result)
                test.run(result, concurrency_level=_concurrency_level_to_int[concurrency_level],
                         max_workers=max_workers, timeout=timeout)
        finally:
            stop_test_run = getattr(result, 'stopTestRun', None)
            if stop_test_run is not None:
                stop_test_run()
        result.sum_duration = time.time() - start_time
        self._after_run(result)

        log.debug('%d free IO buffer(s) in the pool, %d in use.' %
                  (len(out.buff_queue), len(out.buff_dict)))
        if out.buff_dict:
            log.debug('IO buffers in use: %r' % out.buff_dict)

        for reporter in self.reporters:
            reporter.report(result)
        return result
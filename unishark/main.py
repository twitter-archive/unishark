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

import abc
import unishark
import sys
import logging
import concurrent.futures
import time


log = logging.getLogger(__name__)


class TestProgram(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self):
        pass


class DefaultTestProgram(TestProgram):
    def __init__(self, test_dict_conf, verbosity=1, descriptions=False):
        self.test_dict_conf = test_dict_conf
        self.name_pattern = None
        if 'name_pattern' in self.test_dict_conf['test']:
            self.name_pattern = self.test_dict_conf['test']['name_pattern']
        self.verbosity = verbosity
        self.descriptions = descriptions
        self.reporters = self._make_reporters()

    def run(self):
        test = self.test_dict_conf['test']
        max_workers_on_suites = int(test['max_workers']) if 'max_workers' in test else 1
        if max_workers_on_suites <= 1:
            return self._run_suites_sequentially()
        else:
            return self._run_suites_concurrently(max_workers_on_suites)

    @staticmethod
    def _get_class_from_name(long_cls_name):
        parts = long_cls_name.split('.')
        mod = __import__('.'.join(parts[:-1]))
        cls = getattr(mod, parts[-1], None)
        if cls is None:
            raise AttributeError('Class not found.')
        if not issubclass(cls, unishark.Reporter):
            raise TypeError('Class is not a subclass of Reporter.')
        return cls

    def _make_reporters(self):
        created_reporters = []
        test = self.test_dict_conf['test']
        reporters = self.test_dict_conf['reporters'] if 'reporters' in self.test_dict_conf else dict()
        if 'reporters' in test:
            for name in test['reporters']:
                reporter = reporters[name]
                reporter_class = self.__class__._get_class_from_name(reporter['class'])
                kwargs = reporter['kwargs'] if 'kwargs' in reporter else None
                if kwargs and type(kwargs) is dict:
                    created_reporters.append(reporter_class(**kwargs))
                else:
                    created_reporters.append(reporter_class())
        return created_reporters

    def _run_suites_sequentially(self):
        exit_code = 0
        suites = unishark.DefaultTestLoader(name_pattern=self.name_pattern).load_tests_from_dict(self.test_dict_conf)
        runner = unishark.BufferedTestRunner(reporters=self.reporters,
                                             verbosity=self.verbosity,
                                             descriptions=self.descriptions)
        for suite_name, suite_content in suites.items():
            package_name = suite_content['package']
            suite = suite_content['suite']
            max_workers = suite_content['max_workers']
            concurrency_level = suite_content['concurrency_level']
            result = runner.run(suite, name=suite_name, description='Package: ' + package_name,
                                max_workers=max_workers, concurrency_level=concurrency_level)
            exit_code += 0 if result.wasSuccessful() else 1
        for reporter in self.reporters:
            reporter.collect()
        return exit_code

    def _run_suites_concurrently(self, max_workers_on_suites):
        exit_code = 0
        suites = unishark.DefaultTestLoader(name_pattern=self.name_pattern).load_tests_from_dict(self.test_dict_conf)
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers_on_suites) as executor:
            futures = []
            for suite_name, suite_content in suites.items():
                package_name = suite_content['package']
                suite = suite_content['suite']
                max_workers = suite_content['max_workers']
                concurrency_level = suite_content['concurrency_level']
                runner = unishark.BufferedTestRunner(reporters=self.reporters,
                                                     verbosity=self.verbosity,
                                                     descriptions=self.descriptions)
                future = executor.submit(runner.run, suite,
                                         name=suite_name,
                                         description='Package: ' + package_name,
                                         max_workers=max_workers,
                                         concurrency_level=concurrency_level)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                exit_code += 0 if result.wasSuccessful() else 1
        actual_duration = time.time() - start_time
        log.info('Actual total time taken: %.3fs' % actual_duration)
        for reporter in self.reporters:
            reporter.set_actual_duration(actual_duration)
            reporter.collect()
        return exit_code


def main(test_program):
    if not isinstance(test_program, TestProgram):
        raise TypeError
    exit_code = test_program.run()
    log.info('Exit Code: %d' % exit_code)
    sys.exit(exit_code)
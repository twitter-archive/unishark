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


from unittest.suite import TestSuite as UnitTestSuite
from unittest.case import SkipTest
import sys
from unishark.util import get_module_name
from unishark.result import combine_results
import concurrent.futures
import logging

_ErrorHolder = getattr(getattr(__import__('unittest'), 'suite'), '_ErrorHolder')

log = logging.getLogger(__name__)


def _is_suite(test):
    try:
        iter(test)
    except TypeError:
        return False
    return True


def _get_level(test):
    if not _is_suite(test):
        return TestSuite.METHOD_LEVEL
    else:
        for t in test:
            return _get_level(t) - 1
        return TestSuite.ROOT_LEVEL


def _get_current_module(test):
    # test is a module level suite
    current_module = None
    for tt in test:  # tt is a class level suite
        for t in tt:  # t is a test case instance
            current_module = t.__class__.__module__
            break
        break
    return current_module


def _get_current_class(test):
    # test is a class level suite
    current_class = None
    for t in test:  # t is a test case instance
        current_class = t.__class__
        break
    return current_class


def _call_if_exists(parent, attr):
    func = getattr(parent, attr, lambda: None)
    func()


def _group_test_cases(test, dic):
    if not _is_suite(test):
        mod = get_module_name(test)
        if mod not in dic:
            dic[mod] = dict()
        cls = test.__class__
        if cls not in dic[mod]:
            dic[mod][cls] = []
        dic[mod][cls].append(test)
    else:
        for t in test:
            _group_test_cases(t, dic)


def convert(test):
    suite = TestSuite()
    dic = dict()
    _group_test_cases(test, dic)
    for mod_dic in dic.values():
        mod_suite = TestSuite()
        for cases in mod_dic.values():
            cls_suite = TestSuite()
            cls_suite.addTests(cases)
            mod_suite.addTest(cls_suite)
        suite.addTest(mod_suite)
    log.debug('Converted tests: %r' % suite)
    return suite


class TestSuite(UnitTestSuite):
    ROOT_LEVEL = 0
    MODULE_LEVEL = 1
    CLASS_LEVEL = 2
    METHOD_LEVEL = 3

    def __init__(self, tests=()):
        super(TestSuite, self).__init__(tests)
        self._successful_fixtures = set()
        self._failed_fixtures = set()

    def __len__(self):
        return len(self._tests)

    def validate(self):
        assert len(self) > 0
        for mod_suite in self:
            assert _is_suite(mod_suite)
            assert isinstance(mod_suite, TestSuite)
            assert len(mod_suite) > 0
            for cls_suite in mod_suite:
                assert _is_suite(cls_suite)
                assert isinstance(cls_suite, TestSuite)
                assert len(cls_suite) > 0
                for case in cls_suite:
                    assert not _is_suite(case)

    def validate_result(self, result):
        assert len(self) == len(result)
        for mod_suite, mod_result in zip(self, result):
            assert len(mod_suite) == len(mod_result)
            assert type(mod_result) is type(result)
            for cls_suite, cls_result in zip(mod_suite, mod_result):
                assert len(cls_suite) == len(cls_result)
                assert type(cls_result) is type(result)
                for case_result in cls_result:
                    assert type(case_result) is type(result)

    def run(self, result, debug=False, concurrency_level=ROOT_LEVEL, max_workers=1, timeout=None):
        if concurrency_level < TestSuite.ROOT_LEVEL or concurrency_level > TestSuite.METHOD_LEVEL:
            raise ValueError('concurrency_level must be between %d and %d.'
                             % (TestSuite.ROOT_LEVEL, TestSuite.METHOD_LEVEL))
        if debug or self.countTestCases() <= 0 or max_workers <= 1:
            return super(TestSuite, self).run(result, debug=debug)
        self.validate()
        self.validate_result(result)
        with concurrent.futures.ThreadPoolExecutor(max_workers) as main_executor:
            self._run(self, result, TestSuite.ROOT_LEVEL, concurrency_level, main_executor, timeout)
        return result

    def _run(self, test, result, current_level, concurrency_level, main_executor, timeout):
        # test is a test suite instance which must be well-formed.
        # A well-formed test suite has a 4-level self-embedded structure:
        #                                    suite obj(root)
        #                                     /           \
        #                             suite obj(mod1)    suite obj(mod2)
        #                                /      \                    \
        #               suite obj(mod1.cls1)  suite obj(mod1.cls2)  ...
        #                 /            \                       \
        # case obj(mod1.cls1.mth1)  case obj(mod1.cls1.mth2)  ...
        if current_level == concurrency_level:
            self._seq_run(test, result)
        elif current_level < concurrency_level:
            results = result.children  # Divide: for each sub-suite(or test case) in the suite, there is a child result
            if current_level == TestSuite.ROOT_LEVEL:
                if concurrency_level == TestSuite.MODULE_LEVEL:
                    self._handle_fixtures(main_executor, self._setup_module, self._teardown_module,
                                          test, results, current_level, concurrency_level, main_executor, timeout)
                else:
                    with concurrent.futures.ThreadPoolExecutor(len(test)) as executor:
                        self._handle_fixtures(executor, self._setup_module, self._teardown_module,
                                              test, results, current_level, concurrency_level, main_executor, timeout)
            elif current_level == TestSuite.MODULE_LEVEL:
                if concurrency_level == TestSuite.CLASS_LEVEL:
                    self._handle_fixtures(main_executor, self._setup_class, self._teardown_class,
                                          test, results, current_level, concurrency_level, main_executor, timeout)
                else:
                    with concurrent.futures.ThreadPoolExecutor(len(test)) as executor:
                        self._handle_fixtures(executor, self._setup_class, self._teardown_class,
                                              test, results, current_level, concurrency_level, main_executor, timeout)
            elif current_level == TestSuite.CLASS_LEVEL:
                futures = [
                    main_executor.submit(self._run, t, r, current_level+1, concurrency_level, main_executor, timeout)
                    for t, r in zip(test, results)
                ]
                concurrent.futures.wait(futures, timeout=timeout)
            combine_results(result, results)  # Conquer: collect child results into parent result
        return test, result

    def _seq_run(self, test, result):
        level = _get_level(test)
        if level == TestSuite.ROOT_LEVEL:
            for t in test:
                self._seq_run(t, result)
        elif level == TestSuite.MODULE_LEVEL:
            self._setup_module(test, result)
            for t in test:
                self._seq_run(t, result)
            self._teardown_module(test, result)
        elif level == TestSuite.CLASS_LEVEL:
            self._setup_class(test, result)
            for t in test:
                self._seq_run(t, result)
            self._teardown_class(test, result)
        elif level == TestSuite.METHOD_LEVEL:
            current_class = test.__class__
            current_module = current_class.__module__
            if current_module + '.setUpModule' in self._failed_fixtures:
                return
            if '.'.join((current_module, current_class.__name__, 'setUpClass')) in self._failed_fixtures:
                return
            test(result)
        else:
            raise NotImplementedError

    def _handle_fixtures(self, executor, setup_fn, teardown_fn,
                         test, results, current_level, concurrency_level, main_executor, timeout):
        futures_of_setup = [executor.submit(setup_fn, t, r) for t, r in zip(test, results)]
        futures = []
        for done in concurrent.futures.as_completed(futures_of_setup, timeout=timeout):
            t, r = done.result()
            futures.append(
                executor.submit(self._run, t, r, current_level+1, concurrency_level, main_executor, timeout)
            )
        futures_of_teardown = []
        for done in concurrent.futures.as_completed(futures, timeout=timeout):
            t, r = done.result()
            futures_of_teardown.append(executor.submit(teardown_fn, t, r))
        concurrent.futures.wait(futures_of_teardown, timeout=timeout)

    def _addClassOrModuleLevelException(self, result, exception, error_name):
        error = FixtureErrors(error_name)
        addSkip = getattr(result, 'addSkip', None)
        if addSkip is not None and isinstance(exception, SkipTest):
            addSkip(error, str(exception))
        else:
            result.addError(error, sys.exc_info())

    def _setup_module(self, test, result):
        # test must be a module level suite
        current_module = _get_current_module(test)
        fixture_name = current_module + '.setUpModule'
        if fixture_name in self._successful_fixtures or fixture_name in self._failed_fixtures:
            return test, result

        try:
            module = sys.modules[current_module]
        except KeyError:
            return test, result
        setUpModule = getattr(module, 'setUpModule', None)
        if setUpModule is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                setUpModule()
                self._successful_fixtures.add(fixture_name)
            except Exception as e:
                self._failed_fixtures.add(fixture_name)
                error_name = '%s:setUpModule' % current_module
                self._addClassOrModuleLevelException(result, e, error_name)
            finally:
                _call_if_exists(result, '_restoreStdout')
        return test, result

    def _teardown_module(self, test, result):
        # test must be a module level suite
        current_module = _get_current_module(test)
        fixture_name = current_module + '.tearDownModule'
        if fixture_name in self._successful_fixtures or fixture_name in self._failed_fixtures:
            return
        if current_module + '.setUpModule' in self._failed_fixtures:
            return

        try:
            module = sys.modules[current_module]
        except KeyError:
            return
        tearDownModule = getattr(module, 'tearDownModule', None)
        if tearDownModule is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                tearDownModule()
                self._successful_fixtures.add(fixture_name)
            except Exception as e:
                self._failed_fixtures.add(fixture_name)
                error_name = '%s:tearDownModule' % current_module
                self._addClassOrModuleLevelException(result, e, error_name)
            finally:
                _call_if_exists(result, '_restoreStdout')

    def _setup_class(self, test, result):
        # test must be a class level suite
        current_class = _get_current_class(test)
        current_module = current_class.__module__
        class_name = '.'.join((current_module, current_class.__name__))
        fixture_name = class_name + '.setUpClass'
        if fixture_name in self._successful_fixtures or fixture_name in self._failed_fixtures:
            return test, result
        if current_module + '.setUpModule' in self._failed_fixtures:
            return test, result
        if getattr(current_class, '__unittest_skip__', False):
            return test, result

        setUpClass = getattr(current_class, 'setUpClass', None)
        if setUpClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                setUpClass()
                self._successful_fixtures.add(fixture_name)
            except Exception as e:
                self._failed_fixtures.add(fixture_name)
                current_class._classSetupFailed = True
                error_name = '%s:%s:setUpClass' % (current_module, current_class.__name__)
                self._addClassOrModuleLevelException(result, e, error_name)
            finally:
                _call_if_exists(result, '_restoreStdout')
        return test, result

    def _teardown_class(self, test, result):
        # test must be a class level suite
        current_class = _get_current_class(test)
        current_module = current_class.__module__
        class_name = '.'.join((current_module, current_class.__name__))
        fixture_name = class_name + '.tearDownClass'
        if fixture_name in self._successful_fixtures or fixture_name in self._failed_fixtures:
            return
        if class_name + '.setUpClass' in self._failed_fixtures:
            return
        if current_module + '.setUpModule' in self._failed_fixtures:
            return
        if getattr(current_class, "__unittest_skip__", False):
            return

        tearDownClass = getattr(current_class, 'tearDownClass', None)
        if tearDownClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                tearDownClass()
                self._successful_fixtures.add(fixture_name)
            except Exception as e:
                self._failed_fixtures.add(fixture_name)
                error_name = '%s:%s:tearDownClass' % (current_module, current_class.__name__)
                self._addClassOrModuleLevelException(result, e, error_name)
            finally:
                _call_if_exists(result, '_restoreStdout')


class FixtureErrors(_ErrorHolder):
    def __init__(self, description):
        super(FixtureErrors, self).__init__(description)
        self.description = self.description.replace('.', ':')

    def id(self):
        return "%s.%s" % (self.__class__.__name__, self.description)
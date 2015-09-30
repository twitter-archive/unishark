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


import unittest
import pyclbr
import logging
import types
import re

log = logging.getLogger(__name__)


class DefaultTestLoader:
    def __init__(self, name_pattern=None):
        self._name_tree = None
        self._case_class = unittest.TestCase
        self._suite_class = unittest.TestSuite
        self._name_trees_by_pkg = dict()
        self.name_pattern = name_pattern or r'^test\w*'
        self.one_dot_name_pattern = r'\w+\.test\w*'
        self.two_dots_name_pattern = r'(\w+\.){2}test\w*'

    def load_tests_from_dict(self, dict_conf):
        suites_dict = dict()
        for suite_name, content in self._parse_tests_from_dict(dict_conf).items():
            package = content['package']
            test_case_names = content['test_case_names']
            suite = self.load_tests_from_full_names(test_case_names)
            if suite.countTestCases() <= 0:
                log.warning('Test suite %r is empty.' % suite_name)
            suites_dict[suite_name] = {
                'package': package,
                'suite': suite,
                'max_workers': content['max_workers'],
                'concurrency_level': content['concurrency_level']
            }
            log.info('Created test suite %r successfully from package %r.' % (suite_name, package))
        return suites_dict

    def load_tests_from_full_names(self, full_names):
        """
        Returns a unittest.TestSuite instance containing the tests
        whose full name is given and short method name filtered by name_pattern.
        A full name is a dotted name like (package.)module.class.method
        """
        full_names = self._filter_tests_by_name_pattern(full_names)
        return self._make_suite_from_full_names(full_names)

    def load_tests_from_package(self, pkg_name, regex=None):
        """
        Returns a unittest.TestSuite instance containing the tests
        whose dotted long name module.class.method matches the given regular expression
        and short method name matches name_pattern.
        A dotted package name must be provided. regex is default to '(\w+\.){2}test\w*'
        """
        self._build_pkg_name_tree(pkg_name)
        full_names = self._get_full_method_names_from_tree(pkg_name)
        full_names = self._filter_tests_by_two_dots_name_pattern(full_names, regex=regex)
        full_names = self._filter_tests_by_name_pattern(full_names)
        return self._make_suite_from_full_names(full_names)

    def load_tests_from_modules(self, mod_names, regex=None):
        """
        Returns a unittest.TestSuite instance containing the tests
        whose dotted long name class.method matches the given regular expression
        and short method name matches name_pattern.
        A list of dotted module names must be provided. regex is default to '\w+\.test\w*'
        """
        self._build_name_tree(None, set(mod_names))
        full_names = self._get_full_method_names_from_tree(None)
        full_names = self._filter_tests_by_one_dot_name_pattern(full_names, regex=regex)
        full_names = self._filter_tests_by_name_pattern(full_names)
        return self._make_suite_from_full_names(full_names)

    def _filter_tests_by_name_pattern(self, full_names):
        return list(filter(lambda n: re.match(self.name_pattern, n.split('.')[-1]), full_names))

    def _filter_tests_by_one_dot_name_pattern(self, full_names, regex=None):
        regex = regex or self.one_dot_name_pattern
        return list(filter(lambda n: re.match(regex, '.'.join(n.split('.')[-2:])), full_names))

    def _filter_tests_by_two_dots_name_pattern(self, full_names, regex=None):
        regex = regex or self.two_dots_name_pattern
        return list(filter(lambda n: re.match(regex, '.'.join(n.split('.')[-3:])), full_names))

    def _make_suite_from_full_names(self, full_names):
        cases = list(filter(lambda c: c is not None, [self._make_case_from_full_name(name) for name in full_names]))
        suite = self._suite_class(cases)
        log.info('Loaded %d test(s).' % suite.countTestCases())
        log.debug('Loaded test(s): %r' % suite)
        return suite

    def _make_case_from_full_name(self, full_name):
        name_parts = full_name.split('.')
        mod = None
        importable_parts = name_parts[:]
        while importable_parts:
            try:
                mod = __import__('.'.join(importable_parts))
                break
            except ImportError:
                del importable_parts[-1]
                if not importable_parts:
                    raise
        obj = mod
        parent = None
        for part in name_parts[1:]:
            parent, obj = obj, getattr(obj, part)
        if not isinstance(obj, types.FunctionType) and not isinstance(obj, types.MethodType):
            raise TypeError('%r is neither %r nor %r' % (obj, types.FunctionType, types.MethodType))
        # filter out class if it is not unittest.TestCase subclass
        elif isinstance(parent, type) and issubclass(parent, self._case_class):
            name = name_parts[-1]
            test_obj = parent(name)
            # filter out static methods
            if not isinstance(getattr(test_obj, name), types.FunctionType):
                return test_obj
        else:
            return None

    def _parse_tests_from_dict(self, dict_conf):
        res_suites = dict()
        test = dict_conf['test']
        suites = dict_conf['suites']
        for suite_name in test['suites']:
            suite = suites[suite_name]
            pkg_name = None
            if 'package' in suite and suite['package']:
                pkg_name = suite['package']
            groups_dict = suite['groups']
            test_cases_names = []
            for group_key, group in groups_dict.items():
                group = groups_dict[group_key]
                if 'disable' in group and group['disable']:
                    continue
                gran = group['granularity']
                if gran == 'package':
                    full_mth_names = self._get_full_method_names_from_package(pkg_name, group)
                    test_cases_names.extend(full_mth_names)
                elif gran == 'module':
                    full_mth_names = self._get_full_method_names_from_modules(pkg_name, group)
                    test_cases_names.extend(full_mth_names)
                elif gran == 'class':
                    full_mth_names = self._get_full_method_names_from_classes(pkg_name, group)
                    test_cases_names.extend(full_mth_names)
                elif gran == 'method':
                    full_mth_names = self._get_full_method_names_from_methods(pkg_name, group)
                    test_cases_names.extend(full_mth_names)
                else:
                    raise ValueError('Granularity must be one of %r.' % ['package', 'module', 'class', 'method'])
            max_workers = int(suite['max_workers']) if 'max_workers' in suite else 1
            concurrency_level = suite['concurrency_level'] if 'concurrency_level' in suite else 'class'
            concur_levels = ['module', 'class', 'method']
            if concurrency_level not in concur_levels:
                raise ValueError('Concurrency level (%r) is not one of %r.' % (concurrency_level, concur_levels))
            res_suites[suite_name] = {
                'package': pkg_name or 'None',
                'test_case_names': set(test_cases_names),
                'max_workers': max_workers,
                'concurrency_level': concurrency_level
            }
        log.debug('Parsed test config: %r' % res_suites)
        log.info('Parsed test config successfully.')
        return res_suites

    def _build_pkg_name_tree(self, pkg_name):
        import pkgutil
        import copy
        if not pkg_name:
            raise ValueError('A dotted package name must be provided.')
        if pkg_name in self._name_trees_by_pkg:
            self._name_tree = copy.deepcopy(self._name_trees_by_pkg[pkg_name])
        else:
            pkg = __import__(pkg_name)
            name_parts = pkg_name.split('.')
            if len(name_parts) > 1:
                for part in name_parts[1:]:
                    pkg = getattr(pkg, part)
            members = pkgutil.iter_modules(pkg.__path__)
            mod_names = []
            for _, mod_name, is_pkg in members:
                if not is_pkg:
                    mod_names.append(mod_name)
            self._build_name_tree(pkg_name, mod_names)
            self._name_trees_by_pkg[pkg_name] = copy.deepcopy(self._name_tree)

    def _get_full_method_names_from_package(self, pkg_name, group):
        self._build_pkg_name_tree(pkg_name)
        if 'except_modules' in group:
            self._del_except_modules_in_name_tree(group['except_modules'])
        if 'except_classes' in group:
            self._del_except_classes_in_name_tree(group['except_classes'])
        if 'except_methods' in group:
            self._del_except_methods_in_name_tree(group['except_methods'])
        full_names = self._get_full_method_names_from_tree(pkg_name)
        pattern = group.get('pattern', None)
        return self._filter_tests_by_two_dots_name_pattern(full_names, regex=pattern)

    def _get_full_method_names_from_modules(self, pkg_name, group):
        mod_names = group['modules']
        mod_names = set(mod_names)
        self._build_name_tree(pkg_name, mod_names)
        if 'except_classes' in group:
            self._del_except_classes_in_name_tree(group['except_classes'])
        if 'except_methods' in group:
            self._del_except_methods_in_name_tree(group['except_methods'])
        return self._get_full_method_names_from_tree(pkg_name)

    def _get_full_method_names_from_classes(self, pkg_name, group):
        long_cls_names = group['classes']
        long_cls_names = set(long_cls_names)
        mod_names = set()
        for long_cls_name in long_cls_names:
            mod_name, _ = self.__class__._get_cls_name_parts(long_cls_name)
            mod_names.add(mod_name)
        self._build_name_tree(pkg_name, mod_names, filter_cls_names=long_cls_names)
        if 'except_methods' in group:
            self._del_except_methods_in_name_tree(group['except_methods'])
        return self._get_full_method_names_from_tree(pkg_name)

    def _get_full_method_names_from_methods(self, pkg_name, group):
        long_mth_names = group['methods']
        long_mth_names = set(long_mth_names)
        for long_mth_name in long_mth_names:
            self.__class__._get_mth_name_parts(long_mth_name)
        full_mth_names = list(map(lambda n: '.'.join((pkg_name, n)), long_mth_names)) \
            if pkg_name else long_mth_names
        return full_mth_names

    @staticmethod
    def _get_cls_name_parts(long_name):
        parts = long_name.split('.')
        if len(parts) != 2:
            raise ValueError('%r does not comply with: "module.class".' % long_name)
        return parts[0], parts[1]

    @staticmethod
    def _get_mth_name_parts(long_name):
        parts = long_name.split('.')
        if len(parts) != 3:
            raise ValueError('%r does not comply with: "module.class.method".' % long_name)
        return parts[0], parts[1], parts[2]

    def _del_except_modules_in_name_tree(self, except_mod_names):
        for mod_name in set(except_mod_names):
            self._del_mod_in_name_tree(mod_name)

    def _del_except_classes_in_name_tree(self, except_cls_names):
        for except_cls_name in set(except_cls_names):
            mod_name, cls_name = self.__class__._get_cls_name_parts(except_cls_name)
            self._del_cls_in_name_tree(mod_name, cls_name)

    def _del_except_methods_in_name_tree(self, except_mth_names):
        for except_mth_name in set(except_mth_names):
            mod_name, cls_name, mth_name = self.__class__._get_mth_name_parts(except_mth_name)
            self._del_mth_in_name_tree(mod_name, cls_name, mth_name)

    @staticmethod
    def _inspect_module(pkg_name, mod_name):
        full_mod_name = mod_name if not pkg_name else '.'.join((pkg_name, mod_name))
        return pyclbr.readmodule_ex(full_mod_name)  # return module_content

    @staticmethod
    def _get_classes_of_module(module_content):
        classes = dict()  # a dict of 'class_name': pyclbr.Class obj
        for name, obj in module_content.items():
            if isinstance(obj, pyclbr.Class):
                classes[name] = obj
        return classes

    @staticmethod
    def _get_method_names_by_class(cls):
        # cls.methods is a dict of 'method_name': method_line_no
        return sorted(cls.methods.keys(), key=lambda k: cls.methods[k])

    # A name tree is like:
    # tree = {
    #     'mod1': {
    #         'cls1': {
    #             'mth1', 'mth2', ...
    #         },
    #         'cls2': {
    #             ...
    #         },
    #         ...
    #     },
    #     'mod2': {
    #         ...
    #     },
    #     ...
    # }
    def _build_name_tree(self, pkg_name, mod_names, filter_cls_names=None):
        tree = self._name_tree = dict()
        for mod_name in mod_names:
            full_mod_name = '.'.join((pkg_name, mod_name)) if pkg_name else mod_name
            __import__(full_mod_name)
        for mod_name in mod_names:
            mod_content = self.__class__._inspect_module(pkg_name, mod_name)
            classes = self.__class__._get_classes_of_module(mod_content)
            if not classes:
                continue
            for cls_name, cls in classes.items():
                long_cls_name = '.'.join((mod_name, cls_name))
                if filter_cls_names and long_cls_name not in filter_cls_names:
                    continue
                mth_names = self.__class__._get_method_names_by_class(cls)
                if not mth_names:
                    continue
                if mod_name not in tree:
                    tree[mod_name] = dict()
                if cls_name not in tree[mod_name]:
                    tree[mod_name][cls_name] = set()
                for mth_name in mth_names:
                    tree[mod_name][cls_name].add(mth_name)

    def _del_mod_in_name_tree(self, mod_name):
        if mod_name not in self._name_tree:
            raise ValueError('Cannot exclude %r because it is not included.' % mod_name)
        del self._name_tree[mod_name]

    def _del_cls_in_name_tree(self, mod_name, cls_name):
        long_cls_name = '.'.join((mod_name, cls_name))
        if mod_name not in self._name_tree or cls_name not in self._name_tree[mod_name]:
            raise ValueError('Cannot exclude %r because it is not included.' % long_cls_name)
        del self._name_tree[mod_name][cls_name]
        if not self._name_tree[mod_name]:
            del self._name_tree[mod_name]

    def _del_mth_in_name_tree(self, mod_name, cls_name, mth_name):
        long_mth_name = '.'.join((mod_name, cls_name, mth_name))
        if mod_name not in self._name_tree \
                or cls_name not in self._name_tree[mod_name] \
                or mth_name not in self._name_tree[mod_name][cls_name]:
            raise ValueError('Cannot exclude %r because it is not included.' % long_mth_name)
        self._name_tree[mod_name][cls_name].remove(mth_name)
        if not self._name_tree[mod_name][cls_name]:
            del self._name_tree[mod_name][cls_name]
        if not self._name_tree[mod_name]:
            del self._name_tree[mod_name]

    def _get_full_method_names_from_tree(self, pkg_name):
        full_method_names = []
        self._get_dotted_names_dfs(self._name_tree, pkg_name, full_method_names)
        return full_method_names

    def _get_dotted_names_dfs(self, tree, prefix, dotted_names):
        for name in tree:
            dotted_name = '.'.join((prefix, name)) if prefix else name
            if type(tree) is set:  # leaf
                dotted_names.append(dotted_name)
            else:  # tree is dict
                self._get_dotted_names_dfs(tree[name], dotted_name, dotted_names)
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

log = logging.getLogger(__name__)


class DefaultTestLoader:
    def __init__(self, method_prefix='test'):
        self._name_tree = None
        self._test_loader = unittest.TestLoader()
        self.method_prefix = method_prefix

    def load_test_from_dict(self, dict_conf):
        suites_dict = dict()
        for suite_name, content in self._parse_tests_from_dict(dict_conf).items():
            package = content['package']
            test_case_names = content['test_case_names']
            if not test_case_names:
                log.warning('Test suite %r is empty.' % suite_name)
            suites_dict[suite_name] = {
                'package': package,
                'suite': self._test_loader.loadTestsFromNames(test_case_names)
            }
            log.info('Created test suite %r successfully: loaded %d test(s) from package %r.'
                     % (suite_name, len(test_case_names), package))
        return suites_dict

    def _parse_tests_from_dict(self, dict_conf):
        res_suites = dict()
        suites_dict = dict_conf['suites']
        for suite_name, suite in suites_dict.items():
            if 'disable' in suite and suite['disable']:
                continue
            pkg_name = suite['package'] if 'package' in suite else None
            groups_dict = suite['groups']
            test_cases_names = []
            for group_key, group in groups_dict.items():
                group = groups_dict[group_key]
                if 'disable' in group and group['disable']:
                    continue
                gran = group['granularity']
                if gran == 'module':
                    mod_names = group['modules']
                    mod_names = set(mod_names)
                    self._build_name_tree(pkg_name, mod_names)
                    if 'except_classes' in group:
                        self._del_except_classes_in_name_tree(group['except_classes'])
                    if 'except_methods' in group:
                        self._del_except_methods_in_name_tree(group['except_methods'])
                    test_cases_names.extend(self._get_full_method_names_from_tree(pkg_name))
                elif gran == 'class':
                    long_cls_names = group['classes']
                    long_cls_names = set(long_cls_names)
                    mod_names = set()
                    for long_cls_name in long_cls_names:
                        mod_name, _ = self.__class__._get_cls_name_parts(long_cls_name)
                        mod_names.add(mod_name)
                    self._build_name_tree(pkg_name, mod_names, filter_cls_names=long_cls_names)
                    if 'except_methods' in group:
                        self._del_except_methods_in_name_tree(group['except_methods'])
                    test_cases_names.extend(self._get_full_method_names_from_tree(pkg_name))
                elif gran == 'method':
                    long_mth_names = group['methods']
                    long_mth_names = set(long_mth_names)
                    for long_mth_name in long_mth_names:
                        self.__class__._get_mth_name_parts(long_mth_name)
                    full_mth_names = list(map(lambda x: '.'.join((pkg_name, x)), long_mth_names)) \
                        if pkg_name else long_mth_names
                    test_cases_names.extend(full_mth_names)
                else:
                    raise ValueError('Granularity must be in %r.' % ['module', 'class', 'method'])
            res_suites[suite_name] = {'package': pkg_name, 'test_case_names': set(test_cases_names)}
        log.info('Parsed test config successfully.')
        return res_suites

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

    def _del_except_classes_in_name_tree(self, except_cls_names):
        for except_cls_name in set(except_cls_names):
            mod_name, cls_name = self.__class__._get_cls_name_parts(except_cls_name)
            self._del_cls_in_name_tree(mod_name, cls_name)

    def _del_except_methods_in_name_tree(self, except_mth_names):
        for except_mth_name in set(except_mth_names):
            mod_name, cls_name, mth_name = self.__class__._get_mth_name_parts(except_mth_name)
            self._del_mth_in_name_tree(mod_name, cls_name, mth_name)

    def _get_method_names_by_class(self, cls):
        # cls.methods is a dict of 'method_name': method_line_no
        method_names = sorted(cls.methods.keys(), key=lambda k: cls.methods[k])
        return filter(lambda n: n.startswith(self.method_prefix), method_names)

    @staticmethod
    def _get_classes_by_module_name(pkg_name, mod_name):
        full_mod_name = mod_name
        if pkg_name:
            full_mod_name = '.'.join((pkg_name, mod_name))
        classes = pyclbr.readmodule(full_mod_name)  # a dict of 'class_name': pyclbr.Class obj
        # TODO filter classes to get only subclasses of unittest.TestCase
        return classes

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
            classes = self._get_classes_by_module_name(pkg_name, mod_name)
            if not classes:
                continue
            if mod_name not in tree:
                tree[mod_name] = dict()
            for cls_name, cls in classes.items():
                long_cls_name = '.'.join((mod_name, cls_name))
                if filter_cls_names and long_cls_name not in filter_cls_names:
                    continue
                mth_names = self._get_method_names_by_class(cls)
                if not mth_names:
                    continue
                if cls_name not in tree[mod_name]:
                    tree[mod_name][cls_name] = set()
                for mth_name in mth_names:
                    tree[mod_name][cls_name].add(mth_name)

    def _del_cls_in_name_tree(self, mod_name, cls_name):
        long_cls_name = '.'.join((mod_name, cls_name))
        if mod_name not in self._name_tree:
            raise ValueError('Cannot exclude %r: %r not found in modules list.' % (long_cls_name, mod_name))

        if cls_name not in self._name_tree[mod_name]:
            raise ValueError('Cannot exclude %r: %r not found in %r.' % (long_cls_name, cls_name, mod_name))

        del self._name_tree[mod_name][cls_name]
        if not self._name_tree[mod_name]:
            del self._name_tree[mod_name]

    def _del_mth_in_name_tree(self, mod_name, cls_name, mth_name):
        long_mth_name = '.'.join((mod_name, cls_name, mth_name))
        if mod_name not in self._name_tree:
            raise ValueError('Cannot exclude %r: %r not found in modules list.' % (long_mth_name, mod_name))

        if cls_name not in self._name_tree[mod_name]:
            raise ValueError('Cannot exclude %r: %r not found in %r.' % (long_mth_name, cls_name, mod_name))

        if mth_name not in self._name_tree[mod_name][cls_name]:
            raise ValueError('Cannot exclude %r: %r not found in %r.' % (long_mth_name, mth_name, cls_name))

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
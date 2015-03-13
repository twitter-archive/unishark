__author__ = 'Ying Ni <yni@twitter.com>'


import unittest
import pyclbr
import logging

log = logging.getLogger(__name__)


class DefaultTestLoader:
    def __init__(self):
        self._name_tree = None
        self._test_loader = unittest.TestLoader()
        self.method_prefix = 'test'

    def load_test_from_dict(self, dict_conf):
        suites_dict = dict()
        for suite_name, content in self._parse_tests_from_dict(dict_conf).items():
            package = content['package']
            test_case_names = content['test_case_names']
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
                    mod_names = list(set(mod_names))
                    self._build_name_tree(pkg_name, mod_names)
                    if 'except_classes' in group:
                        self._del_except_classes_in_name_tree(group['except_classes'])
                    if 'except_methods' in group:
                        self._del_except_methods_in_name_tree(group['except_methods'])
                    test_cases_names.extend(self._get_full_method_names_from_name_tree(mod_names))
                elif gran == 'class':
                    cls_names = group['classes']
                    cls_names = list(set(cls_names))
                    mod_names = map(lambda n: '.'.join(n.split('.')[:-1]), cls_names)
                    mod_names = list(set(mod_names))
                    self._build_name_tree(pkg_name, mod_names, filter_cls_names=cls_names)
                    if 'except_methods' in group:
                        self._del_except_methods_in_name_tree(group['except_methods'])
                    test_cases_names.extend(self._get_full_method_names_from_name_tree(mod_names))
                elif gran == 'method':
                    test_cases_names.extend(group['methods'])
            test_cases_full_names = list(map(lambda n: '.'.join((pkg_name, n)), test_cases_names)) \
                if pkg_name else test_cases_names
            res_suites[suite_name] = {'package': pkg_name, 'test_case_names': test_cases_full_names}
        log.info('Parsed test config successfully.')
        return res_suites

    def _del_except_classes_in_name_tree(self, except_cls_names):
        for except_cls_name in except_cls_names:
            mod_name = '.'.join(except_cls_name.split('.')[:-1])
            self._del_entry_in_name_tree(mod_name, cls_name=except_cls_name)

    def _del_except_methods_in_name_tree(self, except_mth_names):
        for except_mth_name in except_mth_names:
            parts = except_mth_name.split('.')
            mod_name = '.'.join(parts[:-2])
            except_cls_name = '.'.join(parts[:-1])
            self._del_entry_in_name_tree(mod_name, cls_name=except_cls_name, mth_name=except_mth_name)

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

    def _build_name_tree(self, pkg_name, mod_names, filter_cls_names=None):
        tree = self._name_tree = dict()
        for mod_name in mod_names:
            classes = self._get_classes_by_module_name(pkg_name, mod_name)
            if not classes:
                continue
            if mod_name not in tree:
                tree[mod_name] = []
            for cls_name, cls in classes.items():
                cls_name = '.'.join((mod_name, cls_name))  # 'module.class' as class's key
                if filter_cls_names and cls_name not in filter_cls_names:
                    continue
                mth_names = self._get_method_names_by_class(cls)
                if not mth_names:
                    continue
                if cls_name not in tree[mod_name]:
                    tree[mod_name].append(cls_name)
                if cls_name not in tree:
                    tree[cls_name] = []
                for mth_name in mth_names:
                    mth_name = '.'.join((cls_name, mth_name))  # 'module.class.method' as method's key
                    if mth_name not in tree[cls_name]:
                        tree[cls_name].append(mth_name)

    def _del_entry_in_name_tree(self, mod_name, cls_name=None, mth_name=None):
        if mod_name not in self._name_tree:
            return
        if cls_name and mth_name:
            if cls_name in self._name_tree:
                mth_names = self._name_tree[cls_name]
                if mth_name in mth_names:
                    mth_names.remove(mth_name)
                if not mth_names:
                    del self._name_tree[cls_name]
        elif cls_name:
            cls_names = self._name_tree[mod_name]
            if cls_name in cls_names:
                cls_names.remove(cls_name)
            if not cls_names:
                del self._name_tree[mod_name]
            if cls_name in self._name_tree:
                del self._name_tree[cls_name]

    def _get_full_method_names_from_name_tree(self, parents):
        res_names = []
        for parent in parents:
            if parent not in self._name_tree:
                continue
            for child in self._name_tree[parent]:
                res_names.append(child)
        if not res_names:
            return parents
        else:
            return self._get_full_method_names_from_name_tree(res_names)

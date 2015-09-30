import unittest
import unishark
from tests.mock1 import test_module1, test_module2
from tests.mock2 import test_module3
from tests import logger


class LoaderTestCase(unittest.TestCase):
    def setUp(self):
        super(LoaderTestCase, self).setUp()
        self.loader = unishark.DefaultTestLoader()

    def test_load_modules(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['package'], 'tests.mock1')
        loader = unittest.TestLoader()
        exp_suite = unittest.TestSuite()
        exp_suite.addTests(list(map(loader.loadTestsFromModule, [test_module1, test_module2])))
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), exp_suite.countTestCases())

    def test_load_invalid_module(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ImportError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_classes(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2'],
                            'except_classes': ['test_module1.MyTestClass1', 'test_module2.MyTestClass3']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        loader = unittest.TestLoader()
        exp_suite = unittest.TestSuite()
        exp_suite.addTest(loader.loadTestsFromName('MyTestClass2', module=test_module1))
        exp_suite.addTest(loader.loadTestsFromName('MyTestClass4', module=test_module2))
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), exp_suite.countTestCases())

    def test_exclude_invalid_class(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2'],
                            'except_classes': ['test_module1.MyTestClass1.test_1']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_non_existing_class(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2'],
                            'except_classes': ['test_module1.MyTestClass5']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_methods_from_module(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_methods': ['test_module1.MyTestClass1.test_1', 'test_module1.MyTestClass2.test_3']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        loader = unittest.TestLoader()
        exp_suite = unittest.TestSuite()
        exp_suite.addTest(loader.loadTestsFromNames(['MyTestClass1.test_2',
                                                     'MyTestClass2.test_4'],
                                                    module=test_module1))
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), exp_suite.countTestCases())

    def test_exclude_invalid_method_from_module(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_methods': ['test_module1.MyTestClass1']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_non_existing_method_from_module_1(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_methods': ['test_module1.MyTestClass1.test_5']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_non_existing_method_from_module_2(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_methods': ['test_module1.MyTestClass3.test_5']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_non_existing_method_from_module_3(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_methods': ['test_module2.MyTestClass3.test_5']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_missing_keyword_modules(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'module',
                            'classes': ['test_module1.MyTestClass1']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(KeyError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_load_classes(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module1.MyTestClass1', 'test_module2.MyTestClass3']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        loader = unittest.TestLoader()
        exp_suite = unittest.TestSuite()
        exp_suite.addTest(loader.loadTestsFromName('MyTestClass1', module=test_module1))
        exp_suite.addTest(loader.loadTestsFromName('MyTestClass3', module=test_module2))
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), exp_suite.countTestCases())

    def test_load_invalid_class(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module1.MyTestClass1', 'MyTestClass2']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_load_non_existing_class(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module1.MyTestClass5']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 0)

    def test_exclude_methods_from_class(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module1.MyTestClass1', 'test_module2.MyTestClass3'],
                            'except_methods': ['test_module1.MyTestClass1.test_1',
                                               'test_module1.MyTestClass1.test_2']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        loader = unittest.TestLoader()
        exp_suite = unittest.TestSuite()
        exp_suite.addTest(loader.loadTestsFromName('MyTestClass3', module=test_module2))
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), exp_suite.countTestCases())

    def test_exclude_invalid_method_from_class(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module1.MyTestClass1', 'test_module2.MyTestClass3'],
                            'except_methods': ['test_module1.MyTestClass1',
                                               'test_module1.MyTestClass1.test_2']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_non_existing_method_from_class_1(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module1.MyTestClass1', 'test_module2.MyTestClass3'],
                            'except_methods': ['test_module1.MyTestClass1.test_1',
                                               'test_module1.MyTestClass1.test_5']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_non_existing_method_from_class_2(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module1.MyTestClass1', 'test_module2.MyTestClass3'],
                            'except_methods': ['test_module1.MyTestClass1.test_1',
                                               'test_module1.MyTestClass2.test_3']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_non_existing_method_from_class_3(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module1.MyTestClass1', 'test_module2.MyTestClass3'],
                            'except_methods': ['test_module3.MyTestClass5.test_11']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_missing_keyword_classes(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'methods': ['test_module1.MyTestClass1.test_1']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(KeyError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_load_methods(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'method',
                            'methods': ['test_module1.MyTestClass1.test_1', 'test_module2.MyTestClass3.test_5']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 2)

    def test_load_invalid_methods(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'method',
                            'methods': ['MyTestClass1.test_1']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_load_non_existing_methods_1(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'method',
                            'methods': ['test_module1.MyTestClass3.test_5']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(AttributeError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_load_non_existing_methods_2(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'method',
                            'methods': ['test_module3.MyTestClass5.test_11']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(AttributeError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_invalid_granularity(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'function',
                            'functions': ['test_module1.MyTestClass1.test_1']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_missing_keyword_methods(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'method',
                            'method': 'test_module1.MyTestClass1.test_1'
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(KeyError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_load_multi_suites_and_groups(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3'],
                            'except_methods': ['test_module2.MyTestClass3.test_5']
                        },
                        'g2': {
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_classes': ['test_module1.MyTestClass2'],
                            'except_methods': ['test_module1.MyTestClass1.test_2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'method',
                            'methods': ['test_module3.MyTestClass5.test_11',
                                        'test_module3.MyTestClass6.test_13']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        loader = unittest.TestLoader()
        exp_suite1 = unittest.TestSuite()
        exp_suite1.addTest(loader.loadTestsFromName('MyTestClass1.test_1', module=test_module1))
        exp_suite1.addTest(loader.loadTestsFromName('MyTestClass3.test_6', module=test_module2))
        exp_suite1.addTest(loader.loadTestsFromName('MyTestClass3.test_7', module=test_module2))
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), exp_suite1.countTestCases())
        exp_suite2 = unittest.TestSuite()
        exp_suite2.addTest(loader.loadTestsFromName('MyTestClass5.test_11', module=test_module3))
        exp_suite2.addTest(loader.loadTestsFromName('MyTestClass6.test_13', module=test_module3))
        logger.info(suite_dict['my_suite_2']['suite'])
        self.assertEqual(suite_dict['my_suite_2']['suite'].countTestCases(), exp_suite2.countTestCases())

    def test_exclude_suite_and_group(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': True,
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3'],
                            'except_methods': ['test_module2.MyTestClass3.test_5']
                        },
                        'g2': {
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_classes': ['test_module1.MyTestClass2'],
                            'except_methods': ['test_module1.MyTestClass1.test_2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'method',
                            'methods': ['test_module3.MyTestClass5.test_11',
                                        'test_module3.MyTestClass6.test_13']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        loader = unittest.TestLoader()
        exp_suite = unittest.TestSuite()
        exp_suite.addTest(loader.loadTestsFromName('MyTestClass1.test_1', module=test_module1))
        logger.info(suite_dict['my_suite_1']['suite'])
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), exp_suite.countTestCases())

    def test_empty_suite_1(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': False,
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3']
                        }
                    }
                }
            },
            'test': {
                'suites': []
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertDictEqual(suite_dict, {})

    def test_empty_suite_2(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': True,
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 0)

    def test_missing_keyword_test(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': True,
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3']
                        }
                    }
                }
            }
        }
        with self.assertRaises(KeyError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_missing_keyword_suites(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'disable': True,
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3']
                        }
                    }
                }
            },
            'test': {
                'reporters': ['html', 'xunit'],
                'max_workers': 10
            }
        }
        with self.assertRaises(KeyError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_load_package(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'granularity': 'package'
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'package',
                            'pattern': '\w+\.MyTestClass6\.test\w+[1|2]{2}'
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 10)
        self.assertEqual(suite_dict['my_suite_2']['suite'].countTestCases(), 1)

    def test_exclude_modules_from_package(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'package',
                            'except_modules': ['test_module3']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 2)
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'package',
                            'except_modules': ['test_module3', 'mock_module4']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 0)

    def test_exclude_classes_from_package(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'package',
                            'except_classes': ['test_module3.MyTestClass6', 'test_module3.MyTestClass7',
                                               'test_module3.MyTestClass8']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 4)

    def test_exclude_methods_from_package(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'package',
                            'pattern': '^test\w*\.\w+\.test\w*',
                            'except_methods': ['test_module3.MyTestClass7.test_15',
                                               'test_module3.MyTestClass8.test_17']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 5)

    def test_exclude_invalid_modules(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'package',
                            'except_modules': ['test_module4']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_invalid_classes(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'package',
                            'except_classes': ['test_module3.MyTestClass99', 'mock_module3.MyTestClass7']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_exclude_invalid_methods(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'package',
                            'pattern': '^test\w*\.\w+\.test\w*',
                            'except_methods': ['test_module3.MyTestClass8.test_99']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_dict(dict_conf)

    def test_filtered_by_name_pattern(self):
        self.loader = unishark.DefaultTestLoader(name_pattern='^no_such_prefix\w*')
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'granularity': 'package'
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        },
                        'g2': {
                            'granularity': 'method',
                            'methods': ['mock_module4.MyTestClass6.test_12']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['suite'].countTestCases(), 0)
        self.assertEqual(suite_dict['my_suite_2']['suite'].countTestCases(), 0)

    def test_load_tests_from_package_with_default_pattern(self):
        suite = self.loader.load_tests_from_package('tests.mock2')
        self.assertEqual(suite.countTestCases(), 9)

    def test_load_tests_from_package_with_pattern(self):
        suite = self.loader.load_tests_from_package('tests.mock2', '^mock\w*\.\w+\.test\w*')
        self.assertEqual(suite.countTestCases(), 2)
        suite = self.loader.load_tests_from_package('tests.mock2', '(\w+\.){2}\w*static$')
        self.assertEqual(suite.countTestCases(), 0)
        suite = self.loader.load_tests_from_package('tests.mock2', '(\w+\.){2}\w*__\w+')
        self.assertEqual(suite.countTestCases(), 0)  # filtered by name pattern
        suite = self.loader.load_tests_from_package('tests.mock2', '\w+\.\w+5\.\w+')
        self.assertEqual(suite.countTestCases(), 3)

    def test_load_tests_from_package_no_pkg_name(self):
        with self.assertRaises(ValueError):
            self.loader.load_tests_from_package(None)

    def test_load_tests_from_package_invalid_pkg(self):
        with self.assertRaises(ImportError):
            self.loader.load_tests_from_package('tests.no_such_pkg')

    def test_load_tests_from_modules_with_default_pattern(self):
        suite = self.loader.load_tests_from_modules(['tests.mock2.mock_module4', 'tests.mock1.test_module1'])
        self.assertEqual(suite.countTestCases(), 6)

    def test_load_tests_from_modules_with_pattern(self):
        suite = self.loader.load_tests_from_modules(['tests.mock2.mock_module4', 'tests.mock2.test_module3'],
                                                    regex='\w+5.\w+')
        self.assertEqual(suite.countTestCases(), 3)

    def test_load_tests_from_modules_no_modules(self):
        suite = self.loader.load_tests_from_modules([])
        self.assertEqual(suite.countTestCases(), 0)

    def test_load_tests_from_modules_invalid_modules(self):
        with self.assertRaises(ImportError):
            self.loader.load_tests_from_modules(['tests.mock2.no_such_mod'])

    def test_concurrency_level_module_and_method(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'max_workers': 2,
                    'concurrency_level': 'module',
                    'groups': {
                        'g1': {
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3'],
                            'except_methods': ['test_module2.MyTestClass3.test_5']
                        },
                        'g2': {
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_classes': ['test_module1.MyTestClass2'],
                            'except_methods': ['test_module1.MyTestClass1.test_2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'max_workers': 2,
                    'concurrency_level': 'method',
                    'groups': {
                        'g1': {
                            'granularity': 'method',
                            'methods': ['test_module3.MyTestClass5.test_11',
                                        'test_module3.MyTestClass6.test_13']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['concurrency_level'], 'module')
        self.assertEqual(suite_dict['my_suite_2']['concurrency_level'], 'method')

    def test_concurrency_level_class(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'max_workers': 2,
                    'groups': {
                        'g1': {
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3'],
                            'except_methods': ['test_module2.MyTestClass3.test_5']
                        },
                        'g2': {
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_classes': ['test_module1.MyTestClass2'],
                            'except_methods': ['test_module1.MyTestClass1.test_2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency_level': 'class',
                    'groups': {
                        'g1': {
                            'granularity': 'method',
                            'methods': ['test_module3.MyTestClass5.test_11',
                                        'test_module3.MyTestClass6.test_13']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2']
            }
        }
        suite_dict = self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(suite_dict['my_suite_1']['concurrency_level'], 'class')
        self.assertEqual(suite_dict['my_suite_2']['concurrency_level'], 'class')

    def test_invalid_concurrency_level(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'max_workers': 2,
                    'concurrency_level': 'mod',
                    'groups': {
                        'g1': {
                            'granularity': 'class',
                            'classes': ['test_module2.MyTestClass3'],
                            'except_methods': ['test_module2.MyTestClass3.test_5']
                        },
                        'g2': {
                            'granularity': 'module',
                            'modules': ['test_module1'],
                            'except_classes': ['test_module1.MyTestClass2'],
                            'except_methods': ['test_module1.MyTestClass1.test_2']
                        }
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1']
            }
        }
        with self.assertRaises(ValueError) as cm:
            self.loader.load_tests_from_dict(dict_conf)
        self.assertEqual(str(cm.exception), "Concurrency level ('mod') is not one of ['module', 'class', 'method'].")


if __name__ == '__main__':
    unittest.main(verbosity=2)
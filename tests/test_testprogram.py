import unittest
import unishark
import os
import shutil


class TestProgramTestCase(unittest.TestCase):
    def setUp(self):
        super(TestProgramTestCase, self).setUp()
        self.dest = 'results'
        if os.path.exists(self.dest):
            shutil.rmtree(self.dest)

    def tearDown(self):
        if os.path.exists(self.dest):
            shutil.rmtree(self.dest)


class DefaultTestProgramTestCase(TestProgramTestCase):
    def test_sequential_run(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit']
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        self.assertDictEqual(program.concurrency, {'type': 'threads', 'max_workers': 1, 'timeout': None})
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_multithreading_on_suites(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
                'concurrency': {'max_workers': 2},
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        self.assertEqual(program.concurrency, {'max_workers': 2, 'type': 'threads', 'timeout': None})
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_multithreading_on_classes(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
                'concurrency': {'max_workers': 0},
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        self.assertEqual(program.concurrency, {'max_workers': 0, 'type': 'threads', 'timeout': None})
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_multithreading_on_suites_and_within_suite(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 2, 'level': 'module'},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 8, 'level': 'method'},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
                'concurrency': {'max_workers': 2, 'type': 'threads'},
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        self.assertEqual(program.concurrency, {'max_workers': 2, 'type': 'threads', 'timeout': None})
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_multiprocessing_on_suites(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 2, 'level': 'module'},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 8, 'level': 'method'},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
                'concurrency': {'max_workers': 2, 'type': 'processes'},
                }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        self.assertEqual(program.concurrency, {'max_workers': 2, 'type': 'processes', 'timeout': None})
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_illegal_suites_concurrency_type(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 2, 'level': 'module'},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 8, 'level': 'method'},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
                'concurrency': {'max_workers': 2, 'type': 'processing'},
                }
        }
        with self.assertRaises(ValueError):
            unishark.DefaultTestProgram(dict_conf)
        self.assertFalse(os.path.exists(self.dest))

    def test_program_with_no_suites(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': [],
                'reporters': ['html', 'xunit'],
                'concurrency': {'max_workers': 2},
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 0)
        exp_filenames = ['index.html', 'overview.html', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_program_with_no_reporters_1(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': [],
                'concurrency': {'max_workers': 2},
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        self.assertFalse(os.path.exists(self.dest))

    def test_program_with_no_reporters_2(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'concurrency': {'max_workers': 2},
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        self.assertFalse(os.path.exists(self.dest))

    def test_program_with_name_pattern(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'concurrency': {'max_workers': 2},
                'name_pattern': '^no_such_prefix\w*'
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 0)

    def test_default_suites_concurrency(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_missing_max_workers(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
                'concurrency': {}
            }
        }
        with self.assertRaises(KeyError):
            program = unishark.DefaultTestProgram(dict_conf)
            program.run()
        self.assertFalse(os.path.exists(self.dest))

    def test_illegal_max_workers_type(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
                'concurrency': {'max_workers': 'a'}
            }
        }
        with self.assertRaises(ValueError):
            program = unishark.DefaultTestProgram(dict_conf)
            program.run()
        self.assertFalse(os.path.exists(self.dest))

    def test_misplacing_max_workers(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'concurrency': {'max_workers': 4},
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module3']
                        }
                    }
                }
            },
            'reporters': {
                'html': {
                    'class': 'unishark.HtmlReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                },
                'xunit': {
                    'class': 'unishark.XUnitReporter',
                    'kwargs': {
                        'dest': self.dest
                    }
                }
            },
            'test': {
                'suites': ['my_suite_1', 'my_suite_2'],
                'reporters': ['html', 'xunit'],
                'max_workers': 1
            }
        }
        with self.assertRaises(KeyError) as cm:
            program = unishark.DefaultTestProgram(dict_conf)
            program.run()
            self.assertEqual(cm.exception.message, 'Please set "max_workers" in the "concurrency" sub-dict instead.')
        self.assertFalse(os.path.exists(self.dest))


if __name__ == '__main__':
    unittest.main(verbosity=2)
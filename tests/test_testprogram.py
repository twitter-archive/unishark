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
        exit_code = unishark.DefaultTestProgram(dict_conf).run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_program_with_concurrency_on_suites(self):
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
                'max_workers': 2
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_program_with_concurrency_on_classes(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'max_workers': 4,
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'max_workers': 4,
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
                'max_workers': 0
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_program_with_concurrency_on_both_suites_and_classes(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'max_workers': 4,
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'max_workers': 4,
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
                'max_workers': 2
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html', 'my_suite_2_result.html',
                         'my_suite_1_xunit_result.xml', 'my_suite_2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_program_with_no_suites(self):
        dict_conf = {
            'suites': {
                'my_suite_1': {
                    'package': 'tests.mock1',
                    'max_workers': 4,
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'max_workers': 4,
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
                'max_workers': 2
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
                    'max_workers': 4,
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'max_workers': 4,
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
                'max_workers': 2
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
                    'max_workers': 4,
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'max_workers': 4,
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
                'max_workers': 2
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
                    'max_workers': 4,
                    'groups': {
                        'g1': {
                            'granularity': 'module',
                            'modules': ['test_module1', 'test_module2']
                        }
                    }
                },
                'my_suite_2': {
                    'package': 'tests.mock2',
                    'max_workers': 4,
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
                'max_workers': 2,
                'name_pattern': '^no_such_prefix\w*'
            }
        }
        program = unishark.DefaultTestProgram(dict_conf)
        exit_code = program.run()
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
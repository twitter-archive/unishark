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

    def test_default_test_program(self):
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
                }
            }
        }
        exit_code = unishark.DefaultTestProgram(dict_conf).run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_program_with_multi_reporters(self):
        self.dest = 'reports'
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
                }
            }
        }
        program = unishark.DefaultTestProgram(dict_conf, dest=self.dest)
        program.reporters.append(unishark.XUnitReporter(dest=self.dest))
        exit_code = program.run()
        self.assertEqual(exit_code, 1)
        exp_filenames = ['index.html', 'overview.html', 'my_suite_1_result.html',
                         'summary_xunit_result.xml', 'my_suite_1_xunit_result.xml']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))


if __name__ == '__main__':
    unittest.main(verbosity=2)
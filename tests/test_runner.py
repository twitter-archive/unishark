import unittest
import unishark


class RunnerTestCase(unittest.TestCase):
    def setUp(self):
        super(RunnerTestCase, self).setUp()
        self.loader = unittest.TestLoader()
        self.suite = None
        self.runner = unishark.BufferedTestRunner(verbosity=0)
        self.__context__ = 'tests.mock3'
        unishark.contexts.set(self.__context__, [])
        self.mod1_name = 'test_concur1'
        self.mod2_name = 'test_concur2'
        self.cls11_name = 'test_concur1.Class1'
        self.cls12_name = 'test_concur1.Class2'
        self.cls21_name = 'test_concur2.Class1'
        self.cls22_name = 'test_concur2.Class2'

    def test_init_with_non_iterable_reporters(self):
        with self.assertRaises(TypeError):
            unishark.BufferedTestRunner(reporters=unishark.HtmlReporter())

    def test_init_with_wrong_reporter_type(self):
        class MyReporter():
            def __init__(self):
                pass

            def report(self, result):
                pass

            def collect(self):
                pass
        with self.assertRaises(TypeError):
            unishark.BufferedTestRunner(reporters=[MyReporter()])

    def get_mod_order(self, mod_name, order):
        return [i for i in order if i.startswith(mod_name)]

    def get_cls_order(self, cls_name, order):
        return [i for i in order if i.startswith(cls_name)]

    def check_mod_fixtures(self, mod_name, mod_order):
        self.assertEqual(mod_order.count('%s.setUpModule' % mod_name), 1)
        self.assertEqual(mod_order.count('%s.tearDownModule' % mod_name), 1)
        self.assertEqual(mod_order.index('%s.setUpModule' % mod_name), 0)
        self.assertEqual(mod_order.index('%s.tearDownModule' % mod_name), len(mod_order)-1)

    def check_cls_fixtures(self, cls_name, cls_order):
        self.assertEqual(cls_order.count('%s.setUpClass' % cls_name), 1)
        self.assertEqual(cls_order.count('%s.tearDownClass' % cls_name), 1)
        self.assertEqual(cls_order.index('%s.setUpClass' % cls_name), 0)
        self.assertEqual(cls_order.index('%s.tearDownClass' % cls_name), len(cls_order)-1)

    def check_mod_in_seq(self, order):
        mod_fixtures = [i for i in order if i.endswith('setUpModule') or i.endswith('tearDownModule')]
        mod1_name = mod_fixtures[0].rstrip('.setUpModule')
        self.assertEqual(mod_fixtures[1], '%s.tearDownModule' % mod1_name)
        mod2_name = mod_fixtures[2].rstrip('.setUpModule')
        self.assertNotEqual(mod2_name, mod1_name)
        self.assertEqual(mod_fixtures[3], '%s.tearDownModule' % mod2_name)

    def check_mod_in_parallel(self, mod1_name, mod2_name, order):
        self.assertLess(order.index(mod1_name + '.setUpModule'), order.index(mod2_name + '.tearDownModule'))
        self.assertLess(order.index(mod2_name + '.setUpModule'), order.index(mod1_name + '.tearDownModule'))

    def check_cls_in_seq(self, mod_order):
        cls_fixtures = [i for i in mod_order if i.endswith('setUpClass') or i.endswith('tearDownClass')]
        cls1_name = cls_fixtures[0].rstrip('.setUpClass')
        self.assertEqual(cls_fixtures[1], '%s.tearDownClass' % cls1_name)
        cls2_name = cls_fixtures[2].rstrip('.setUpClass')
        self.assertNotEqual(cls2_name, cls1_name)
        self.assertEqual(cls_fixtures[3], '%s.tearDownClass' % cls2_name)

    def check_cls_in_parallel(self, cls1_name, cls2_name, mod_order):
        self.assertLess(mod_order.index(cls1_name + '.setUpClass'), mod_order.index(cls2_name + '.tearDownClass'))
        self.assertLess(mod_order.index(cls2_name + '.setUpClass'), mod_order.index(cls1_name + '.tearDownClass'))

    def check_cases_in_seq(self, cls_order):
        case1_name = cls_order[1].rstrip('.setUp')
        self.assertEqual(cls_order[2], '%s.tearDown' % case1_name)
        case2_name = cls_order[3].rstrip('.setUp')
        self.assertNotEqual(case2_name, case1_name)
        self.assertEqual(cls_order[4], '%s.tearDown' % case2_name)

    def check_cases_in_parallel(self, case1_name, case2_name, cls_order):
        self.assertLess(cls_order.index(case1_name + '.setUp'), cls_order.index(case2_name + '.tearDown'))
        self.assertLess(cls_order.index(case2_name + '.setUp'), cls_order.index(case1_name + '.tearDown'))

    def check_result(self, result):
        self.assertTrue(result.wasSuccessful())
        results = result.results
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[self.mod1_name][self.cls11_name]), 2)
        self.assertEqual(len(results[self.mod1_name][self.cls12_name]), 2)
        self.assertEqual(len(results[self.mod2_name][self.cls21_name]), 2)
        self.assertEqual(len(results[self.mod2_name][self.cls22_name]), 2)

    def test_seq_run_1(self):
        self.suite = self.loader.loadTestsFromNames(['tests.mock3.test_concur1', 'tests.mock3.test_concur2'])
        result = self.runner.run(self.suite, max_workers=8, concurrency_level='none')
        self.check_result(result)
        order = unishark.contexts.get(self.__context__)
        mod1_order = self.get_mod_order(self.mod1_name, order)
        mod2_order = self.get_mod_order(self.mod2_name, order)
        self.check_mod_fixtures(self.mod1_name, mod1_order)
        self.check_mod_fixtures(self.mod2_name, mod2_order)
        cls11_order = self.get_cls_order(self.cls11_name, order)
        cls12_order = self.get_cls_order(self.cls12_name, order)
        cls21_order = self.get_cls_order(self.cls21_name, order)
        cls22_order = self.get_cls_order(self.cls22_name, order)
        self.check_cls_fixtures(self.cls11_name, cls11_order)
        self.check_cls_fixtures(self.cls12_name, cls12_order)
        self.check_cls_fixtures(self.cls21_name, cls21_order)
        self.check_cls_fixtures(self.cls22_name, cls22_order)
        self.check_mod_in_seq(order)
        self.check_cls_in_seq(mod1_order)
        self.check_cls_in_seq(mod2_order)
        self.check_cases_in_seq(cls11_order)
        self.check_cases_in_seq(cls12_order)
        self.check_cases_in_seq(cls21_order)
        self.check_cases_in_seq(cls22_order)

    def test_seq_run_2(self):
        self.suite = self.loader.loadTestsFromNames(['tests.mock3.test_concur1', 'tests.mock3.test_concur2'])
        result = self.runner.run(self.suite, max_workers=1, concurrency_level='method')
        self.check_result(result)
        order = unishark.contexts.get(self.__context__)
        mod1_order = self.get_mod_order(self.mod1_name, order)
        mod2_order = self.get_mod_order(self.mod2_name, order)
        self.check_mod_fixtures(self.mod1_name, mod1_order)
        self.check_mod_fixtures(self.mod2_name, mod2_order)
        cls11_order = self.get_cls_order(self.cls11_name, order)
        cls12_order = self.get_cls_order(self.cls12_name, order)
        cls21_order = self.get_cls_order(self.cls21_name, order)
        cls22_order = self.get_cls_order(self.cls22_name, order)
        self.check_cls_fixtures(self.cls11_name, cls11_order)
        self.check_cls_fixtures(self.cls12_name, cls12_order)
        self.check_cls_fixtures(self.cls21_name, cls21_order)
        self.check_cls_fixtures(self.cls22_name, cls22_order)
        self.check_mod_in_seq(order)
        self.check_cls_in_seq(mod1_order)
        self.check_cls_in_seq(mod2_order)
        self.check_cases_in_seq(cls11_order)
        self.check_cases_in_seq(cls12_order)
        self.check_cases_in_seq(cls21_order)
        self.check_cases_in_seq(cls22_order)

    def test_seq_run_3_empty_suite(self):
        self.suite = unittest.TestSuite()
        self.suite.addTest(unittest.TestSuite())
        result = self.runner.run(self.suite, max_workers=8, concurrency_level='method')
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.results), 0)

    def test_concurrency_level_module(self):
        self.suite = self.loader.loadTestsFromNames(['tests.mock3.test_concur1', 'tests.mock3.test_concur2'])
        result = self.runner.run(self.suite, max_workers=2, concurrency_level='module')
        self.check_result(result)
        order = unishark.contexts.get(self.__context__)
        print('Execution Order: %r' % order)
        mod1_order = self.get_mod_order(self.mod1_name, order)
        mod2_order = self.get_mod_order(self.mod2_name, order)
        print('\nModule 1 execution order: %r' % mod1_order)
        print('\nModule 2 execution order: %r' % mod2_order)
        self.check_mod_fixtures(self.mod1_name, mod1_order)
        self.check_mod_fixtures(self.mod2_name, mod2_order)
        cls11_order = self.get_cls_order(self.cls11_name, order)
        cls12_order = self.get_cls_order(self.cls12_name, order)
        cls21_order = self.get_cls_order(self.cls21_name, order)
        cls22_order = self.get_cls_order(self.cls22_name, order)
        self.check_cls_fixtures(self.cls11_name, cls11_order)
        self.check_cls_fixtures(self.cls12_name, cls12_order)
        self.check_cls_fixtures(self.cls21_name, cls21_order)
        self.check_cls_fixtures(self.cls22_name, cls22_order)
        self.check_mod_in_parallel(self.mod1_name, self.mod2_name, order)
        self.check_cls_in_seq(mod1_order)
        self.check_cls_in_seq(mod2_order)
        self.check_cases_in_seq(cls11_order)
        self.check_cases_in_seq(cls12_order)
        self.check_cases_in_seq(cls21_order)
        self.check_cases_in_seq(cls22_order)

    def test_concurrency_level_class(self):
        self.suite = self.loader.loadTestsFromNames(['tests.mock3.test_concur1', 'tests.mock3.test_concur2'])
        result = self.runner.run(self.suite, max_workers=4, concurrency_level='class')
        self.check_result(result)
        order = unishark.contexts.get(self.__context__)
        print('Execution Order: %r' % order)
        mod1_order = self.get_mod_order(self.mod1_name, order)
        mod2_order = self.get_mod_order(self.mod2_name, order)
        self.check_mod_fixtures(self.mod1_name, mod1_order)
        self.check_mod_fixtures(self.mod2_name, mod2_order)
        cls11_order = self.get_cls_order(self.cls11_name, order)
        cls12_order = self.get_cls_order(self.cls12_name, order)
        cls21_order = self.get_cls_order(self.cls21_name, order)
        cls22_order = self.get_cls_order(self.cls22_name, order)
        print('\nModule 1 Class 1 execution order: %r' % cls11_order)
        print('\nModule 1 Class 2 execution order: %r' % cls12_order)
        print('\nModule 2 Class 1 execution order: %r' % cls21_order)
        print('\nModule 2 Class 2 execution order: %r' % cls22_order)
        self.check_cls_fixtures(self.cls11_name, cls11_order)
        self.check_cls_fixtures(self.cls12_name, cls12_order)
        self.check_cls_fixtures(self.cls21_name, cls21_order)
        self.check_cls_fixtures(self.cls22_name, cls22_order)
        self.check_mod_in_parallel(self.mod1_name, self.mod2_name, order)
        self.check_cls_in_parallel(self.cls11_name, self.cls12_name, mod1_order)
        self.check_cls_in_parallel(self.cls21_name, self.cls22_name, mod2_order)
        self.check_cases_in_seq(cls11_order)
        self.check_cases_in_seq(cls12_order)
        self.check_cases_in_seq(cls21_order)
        self.check_cases_in_seq(cls22_order)

    def test_concurrency_level_class_with_inadequate_workers(self):
        self.suite = self.loader.loadTestsFromNames(['tests.mock3.test_concur1', 'tests.mock3.test_concur2'])
        result = self.runner.run(self.suite, max_workers=2, concurrency_level='class')
        self.check_result(result)
        order = unishark.contexts.get(self.__context__)
        print('Execution Order: %r' % order)
        mod1_order = self.get_mod_order(self.mod1_name, order)
        mod2_order = self.get_mod_order(self.mod2_name, order)
        self.check_mod_fixtures(self.mod1_name, mod1_order)
        self.check_mod_fixtures(self.mod2_name, mod2_order)
        cls11_order = self.get_cls_order(self.cls11_name, order)
        cls12_order = self.get_cls_order(self.cls12_name, order)
        cls21_order = self.get_cls_order(self.cls21_name, order)
        cls22_order = self.get_cls_order(self.cls22_name, order)
        print('\nModule 1 Class 1 execution order: %r' % cls11_order)
        print('\nModule 1 Class 2 execution order: %r' % cls12_order)
        print('\nModule 2 Class 1 execution order: %r' % cls21_order)
        print('\nModule 2 Class 2 execution order: %r' % cls22_order)
        self.check_cls_fixtures(self.cls11_name, cls11_order)
        self.check_cls_fixtures(self.cls12_name, cls12_order)
        self.check_cls_fixtures(self.cls21_name, cls21_order)
        self.check_cls_fixtures(self.cls22_name, cls22_order)
        self.check_mod_in_parallel(self.mod1_name, self.mod2_name, order)
        self.check_cls_in_parallel(self.cls11_name, self.cls12_name, mod1_order)
        self.check_cls_in_parallel(self.cls21_name, self.cls22_name, mod2_order)
        self.check_cases_in_seq(cls11_order)
        self.check_cases_in_seq(cls12_order)
        self.check_cases_in_seq(cls21_order)
        self.check_cases_in_seq(cls22_order)

    def test_concurrency_level_method(self):
        self.suite = self.loader.loadTestsFromNames(['tests.mock3.test_concur1', 'tests.mock3.test_concur2'])
        result = self.runner.run(self.suite, max_workers=8, concurrency_level='method')
        self.check_result(result)
        order = unishark.contexts.get(self.__context__)
        print('Execution Order: %r' % order)
        mod1_order = self.get_mod_order(self.mod1_name, order)
        mod2_order = self.get_mod_order(self.mod2_name, order)
        self.check_mod_fixtures(self.mod1_name, mod1_order)
        self.check_mod_fixtures(self.mod2_name, mod2_order)
        cls11_order = self.get_cls_order(self.cls11_name, order)
        cls12_order = self.get_cls_order(self.cls12_name, order)
        cls21_order = self.get_cls_order(self.cls21_name, order)
        cls22_order = self.get_cls_order(self.cls22_name, order)
        print('\nModule 1 Class 1 execution order: %r' % cls11_order)
        print('\nModule 1 Class 2 execution order: %r' % cls12_order)
        print('\nModule 2 Class 1 execution order: %r' % cls21_order)
        print('\nModule 2 Class 2 execution order: %r' % cls22_order)
        self.check_cls_fixtures(self.cls11_name, cls11_order)
        self.check_cls_fixtures(self.cls12_name, cls12_order)
        self.check_cls_fixtures(self.cls21_name, cls21_order)
        self.check_cls_fixtures(self.cls22_name, cls22_order)
        self.check_mod_in_parallel(self.mod1_name, self.mod2_name, order)
        self.check_cls_in_parallel(self.cls11_name, self.cls12_name, mod1_order)
        self.check_cls_in_parallel(self.cls21_name, self.cls22_name, mod2_order)
        self.check_cases_in_parallel(self.cls11_name + '.test_case_1', self.cls11_name + '.test_case_2', cls11_order)
        self.check_cases_in_parallel(self.cls12_name + '.test_case_1', self.cls12_name + '.test_case_2', cls12_order)
        self.check_cases_in_parallel(self.cls21_name + '.test_case_1', self.cls21_name + '.test_case_2', cls21_order)
        self.check_cases_in_parallel(self.cls22_name + '.test_case_1', self.cls22_name + '.test_case_2', cls22_order)

    def test_concurrency_level_method_with_inadequate_workers(self):
        self.suite = self.loader.loadTestsFromNames(['tests.mock3.test_concur1', 'tests.mock3.test_concur2'])
        result = self.runner.run(self.suite, max_workers=4, concurrency_level='method')
        self.check_result(result)
        order = unishark.contexts.get(self.__context__)
        print('Execution Order: %r' % order)
        mod1_order = self.get_mod_order(self.mod1_name, order)
        mod2_order = self.get_mod_order(self.mod2_name, order)
        self.check_mod_fixtures(self.mod1_name, mod1_order)
        self.check_mod_fixtures(self.mod2_name, mod2_order)
        cls11_order = self.get_cls_order(self.cls11_name, order)
        cls12_order = self.get_cls_order(self.cls12_name, order)
        cls21_order = self.get_cls_order(self.cls21_name, order)
        cls22_order = self.get_cls_order(self.cls22_name, order)
        print('\nModule 1 Class 1 execution order: %r' % cls11_order)
        print('\nModule 1 Class 2 execution order: %r' % cls12_order)
        print('\nModule 2 Class 1 execution order: %r' % cls21_order)
        print('\nModule 2 Class 2 execution order: %r' % cls22_order)
        self.check_cls_fixtures(self.cls11_name, cls11_order)
        self.check_cls_fixtures(self.cls12_name, cls12_order)
        self.check_cls_fixtures(self.cls21_name, cls21_order)
        self.check_cls_fixtures(self.cls22_name, cls22_order)
        self.check_mod_in_parallel(self.mod1_name, self.mod2_name, order)
        self.check_cls_in_parallel(self.cls11_name, self.cls12_name, mod1_order)
        self.check_cls_in_parallel(self.cls21_name, self.cls22_name, mod2_order)

    def test_fixtures_failures(self):
        mod3_name = 'test_concur3'
        mod4_name = 'test_concur4'
        mod5_name = 'test_concur5'
        cls1_name = 'Class1'
        cls2_name = 'Class2'
        self.suite = self.loader.loadTestsFromNames(['tests.mock3.test_concur3',
                                                     'tests.mock3.test_concur4',
                                                     'tests.mock3.test_concur5'])
        result = self.runner.run(self.suite, max_workers=12, concurrency_level='method')
        self.assertEqual(result.successes, 2)
        self.assertEqual(len(result.errors), 6)
        self.assertEqual(len(result.failures), 6)
        self.assertEqual(len(result.skipped), 2)
        order = unishark.contexts.get(self.__context__)
        # mod3 setUpModule failed
        self.assertEqual(order.count('%s.setUpModule' % mod3_name), 1)
        self.assertNotIn('%s.tearDownModule' % mod3_name, order)
        self.assertNotIn('%s.%s.setUpClass' % (mod3_name, cls1_name), order)
        self.assertNotIn('%s.%s.tearDownClass' % (mod3_name, cls1_name), order)
        self.assertNotIn('%s.%s.setUpClass' % (mod3_name, cls2_name), order)
        self.assertNotIn('%s.%s.tearDownClass' % (mod3_name, cls2_name), order)
        # mod4.Class1 setUpClass failed, mod4.Class2 skipped
        self.assertEqual(order.count('%s.setUpModule' % mod4_name), 1)
        self.assertEqual(order.count('%s.tearDownModule' % mod4_name), 1)
        self.assertEqual(order.count('%s.%s.setUpClass' % (mod4_name, cls1_name)), 1)
        self.assertNotIn('%s.%s.tearDownClass' % (mod4_name, cls1_name), order)
        self.assertNotIn('%s.%s.setUpClass' % (mod4_name, cls2_name), order)
        self.assertNotIn('%s.%s.tearDownClass' % (mod4_name, cls2_name), order)
        # mod5 tearDownModule and mod5.Class1 tearDownClass failed
        self.assertEqual(order.count('%s.setUpModule' % mod5_name), 1)
        self.assertEqual(order.count('%s.tearDownModule' % mod5_name), 1)
        self.assertEqual(order.count('%s.%s.setUpClass' % (mod5_name, cls1_name)), 1)
        self.assertEqual(order.count('%s.%s.tearDownClass' % (mod5_name, cls1_name)), 1)
        self.assertEqual(order.count('%s.%s.setUpClass' % (mod5_name, cls2_name)), 1)
        self.assertEqual(order.count('%s.%s.tearDownClass' % (mod5_name, cls2_name)), 1)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(RunnerTestCase)
    rslt = unittest.TextTestRunner(descriptions=False, verbosity=0).run(suite)
    print('Successful: %r' % rslt.wasSuccessful())
    import sys
    sys.exit(0 if rslt.wasSuccessful() else 1)

# Manually test with:
# if __name__ == '__main__':
#     suite = unittest.TestLoader().loadTestsFromNames(['tests.mock3.test_concur1',
#                                                       'tests.mock3.test_concur2',
#                                                       'tests.mock3.test_concur3',
#                                                       'tests.mock3.test_concur4',
#                                                       'tests.mock3.test_concur5'])
#     unishark.contexts.set('tests.mock3', [])
#     unishark.BufferedTestRunner(reporters=[unishark.HtmlReporter(dest='logs')]) \
#         .run(suite, max_workers=20, concurrency_level='method')

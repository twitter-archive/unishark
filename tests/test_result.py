import unittest
import unishark
from unishark.result import PASS, SKIPPED, ERROR, FAIL, EXPECTED_FAIL, UNEXPECTED_PASS
from tests import logger
import time
import threading


class Mocking(unittest.TestCase):
    def test_successes(self):
        """
        This is doc string.
        Great.
        """
        self.assertEqual(1, 1)
        print('A stdout log.')

    @unittest.skip('')
    def test_skipped(self):
        self.assertEqual(2, 2)

    def test_errors(self):
        raise ValueError

    def test_failures(self):
        logger.error('A logging log.')
        self.assertEqual(1, 2)

    @unittest.expectedFailure
    def test_expected_failures(self):
        self.assertTrue(False)

    @unittest.expectedFailure
    def test_unexpected_successes(self):
        self.assertTrue(True)


class MyTestClass1(unittest.TestCase):
    count = None

    @classmethod
    def setUpClass(cls):
        cls.count = []
        print('[thread:%d] Mary setUpClass' % threading.current_thread().ident)

    @classmethod
    def tearDownClass(cls):
        print('[thread:%d] Mary tearDownClass (count %r)' % (threading.current_thread().ident, cls.count))
        assert cls.count == [1, 1]
        cls.count = []

    def setUp(self):
        self.count.append(1)
        print('[thread:%d] Mary setUp' % threading.current_thread().ident)

    def tearDown(self):
        print('[thread:%d] Mary tearDown (count %r)' % (threading.current_thread().ident, self.count))

    def test_1(self):
        for i in range(3):
            logger.info('Here is log #%d of test_1' % i)
            print('[thread:%d] Mary test 1==1 (%d)' % (threading.current_thread().ident, i+1))
            self.assertEqual(1, 1)
            time.sleep(1)

    def test_2(self):
        logger.info('Here is log of test_2')
        print('[thread:%d] Mary test 2!=1' % threading.current_thread().ident)
        time.sleep(1)
        self.assertEqual(2, 1)


class MyTestClass2(unittest.TestCase):
    count = None

    @classmethod
    def setUpClass(cls):
        cls.count = 0
        print('[thread:%d] Bob setUpClass' % threading.current_thread().ident)

    @classmethod
    def tearDownClass(cls):
        print('[thread:%d] Bob tearDownClass (count %r)' % (threading.current_thread().ident, cls.count))
        assert cls.count == 2
        cls.count = 0

    def setUp(self):
        self.__class__.count += 1
        print('[thread:%d] Bob setUp' % threading.current_thread().ident)

    def tearDown(self):
        print('[thread:%d] Bob tearDown (count %r)' % (threading.current_thread().ident, self.__class__.count))

    @unishark.data_driven(left=list(range(2)))
    @unishark.data_driven(right=list(range(2)))
    def test_1(self, **param):
        """Test cross-multiply data-driven"""
        l = param['left']
        r = param['right']
        logger.info('%d x %d = %d' % (l, r, l*r))
        print('[thread:%d] Bob test %dx%d' % (threading.current_thread().ident, l, r))
        time.sleep(1)

    def test_3(self):
        logger.info('Here is log of test_3')
        print('[thread:%d] Bob test 3!=2' % threading.current_thread().ident)
        time.sleep(1)
        self.assertEqual(3, 2)


class ResultTestCase(unittest.TestCase):
    def setUp(self):
        super(ResultTestCase, self).setUp()
        self.loader = unittest.TestLoader()
        self.suite = self.loader.loadTestsFromTestCase(Mocking)

    def test_buffered_result(self):
        result = unishark.BufferedTestRunner(verbosity=0).run(self.suite)
        self.assertEqual(result.successes, 1)
        self.assertEqual(len(result.skipped), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.expectedFailures), 1)
        self.assertEqual(len(result.unexpectedSuccesses), 1)
        self.assertEqual(result.testsRun, 6)

        results = result.results['test_result']['test_result.Mocking']
        res_dict = dict()
        duration_sum = 0
        for tup in results:
            res_dict[tup[0]] = tup[1:]
            duration_sum += tup[2]
        self.assertGreaterEqual(result.sum_duration, duration_sum)
        method_names = ['test_successes', 'test_skipped', 'test_errors', 'test_failures',
                        'test_expected_failures', 'test_unexpected_successes']
        method_names = list(map(lambda x: 'test_result.Mocking.'+x, method_names))
        self.assertSetEqual(set(res_dict.keys()), set(method_names))

        success_res = res_dict['test_result.Mocking.test_successes']
        self.assertEqual(success_res[0], '\n        This is doc string.\n        Great.\n        ')
        self.assertEqual(success_res[2], PASS)
        self.assertEqual(success_res[3], 'No Log\n')
        self.assertEqual(success_res[4], 'No Exception\n')
        skip_res = res_dict['test_result.Mocking.test_skipped']
        self.assertEqual(skip_res[0], 'No Method Doc\n')
        self.assertEqual(skip_res[2], SKIPPED)
        self.assertEqual(skip_res[3], 'No Log\n')
        self.assertEqual(skip_res[4], "Skipped: ''")
        error_res = res_dict['test_result.Mocking.test_errors']
        self.assertEqual(error_res[2], ERROR)
        self.assertIn('ValueError', error_res[4])
        fail_res = res_dict['test_result.Mocking.test_failures']
        self.assertEqual(fail_res[2], FAIL)
        self.assertEqual(fail_res[3], 'ERROR: A logging log.\n')
        self.assertIn('AssertionError', fail_res[4])
        exp_fail_res = res_dict['test_result.Mocking.test_expected_failures']
        self.assertEqual(exp_fail_res[2], EXPECTED_FAIL)
        self.assertIn('AssertionError', exp_fail_res[4])
        unexp_success_res = res_dict['test_result.Mocking.test_unexpected_successes']
        self.assertEqual(unexp_success_res[2], UNEXPECTED_PASS)
        self.assertEqual(unexp_success_res[4], 'No Exception\n')

    def test_multi_runner_with_multithreads(self):
        suite1 = self.loader.loadTestsFromTestCase(MyTestClass1)
        suite2 = self.loader.loadTestsFromTestCase(MyTestClass2)

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(unishark.BufferedTestRunner(verbosity=0).run, suite1)
            f2 = executor.submit(unishark.BufferedTestRunner(verbosity=0).run, suite2)
        r1 = f1.result()
        r2 = f2.result()
        print('suite1 result: %r' % r1.results)
        self.assertEqual(r1.testsRun, 2)
        self.assertEqual(r1.successes, 1)
        self.assertEqual(len(r1.failures), 1)
        self.assertEqual(len(r1.errors), 0)
        self.assertFalse(r1.wasSuccessful())
        print('suite2 result: %r' % r2.results)
        self.assertEqual(r2.testsRun, 2)
        self.assertEqual(r2.successes, 1)
        self.assertEqual(len(r2.failures), 1)
        self.assertEqual(len(r2.errors), 0)
        self.assertFalse(r2.wasSuccessful())

    def test_single_runner_with_multithreads(self):
        self.suite = self.loader.loadTestsFromNames(['tests.test_result.MyTestClass1.test_1',
                                                     'tests.test_result.MyTestClass1.test_2',
                                                     'tests.test_result.MyTestClass2.test_1',
                                                     'tests.test_result.MyTestClass2.test_3'])
        result = unishark.BufferedTestRunner(verbosity=0).run(self.suite, max_workers=4, concurrency_level='method')
        print(result.results)
        self.assertEqual(result.testsRun, 4)
        self.assertEqual(result.successes, 2)
        self.assertEqual(len(result.failures), 2)
        self.assertEqual(len(result.errors), 0)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.results['test_result']['test_result.MyTestClass2'][0][4],
                         'INFO: 0 x 0 = 0\nINFO: 0 x 1 = 0\nINFO: 1 x 0 = 0\nINFO: 1 x 1 = 1\n')
        self.assertEqual(result.results['test_result']['test_result.MyTestClass2'][0][5], 'No Exception\n')
        self.assertEqual(result.results['test_result']['test_result.MyTestClass1'][1][4],
                         'INFO: Here is log of test_2\n')
        self.assertIn('AssertionError: 2 != 1', result.results['test_result']['test_result.MyTestClass1'][1][5])


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ResultTestCase)
    rslt = unittest.TextTestRunner(descriptions=False, verbosity=0).run(suite)
    print('Successful: %r' % rslt.wasSuccessful())
    import sys
    sys.exit(0 if rslt.wasSuccessful() else 1)
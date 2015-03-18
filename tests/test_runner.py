import unittest
import unishark
from unishark.runner import PASS, SKIPPED, ERROR, FAIL, EXPECTED_FAIL, UNEXPECTED_PASS
from tests import logger


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


class RunnerTestCase(unittest.TestCase):
    def setUp(self):
        super(RunnerTestCase, self).setUp()
        self.suite = unittest.TestLoader().loadTestsFromTestCase(Mocking)

    def test_buffered_result(self):
        result = unishark.BufferedTestRunner([]).run(self.suite)
        self.assertEqual(result.successes, 1)
        self.assertEqual(len(result.skipped), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.expectedFailures), 1)
        self.assertEqual(len(result.unexpectedSuccesses), 1)
        self.assertEqual(result.testsRun, 6)

        results = result.results['test_runner']['test_runner.Mocking']
        res_dict = dict()
        duration_sum = 0
        for tup in results:
            res_dict[tup[0]] = tup[1:]
            duration_sum += tup[2]
        self.assertGreaterEqual(result.sum_duration, duration_sum)
        method_names = ['test_successes', 'test_skipped', 'test_errors', 'test_failures',
                        'test_expected_failures', 'test_unexpected_successes']
        method_names = list(map(lambda x: 'test_runner.Mocking.'+x, method_names))
        self.assertSetEqual(set(res_dict.keys()), set(method_names))

        success_res = res_dict['test_runner.Mocking.test_successes']
        self.assertEqual(success_res[0], '\n        This is doc string.\n        Great.\n        ')
        self.assertEqual(success_res[2], PASS)
        self.assertEqual(success_res[3], 'A stdout log.\n')
        self.assertEqual(success_res[4], 'No Exceptions')
        skip_res = res_dict['test_runner.Mocking.test_skipped']
        self.assertEqual(skip_res[0], 'No Method Doc')
        self.assertEqual(skip_res[2], SKIPPED)
        self.assertEqual(skip_res[3], '')
        self.assertEqual(skip_res[4], "Skipped: ''")
        error_res = res_dict['test_runner.Mocking.test_errors']
        self.assertEqual(error_res[2], ERROR)
        self.assertIn('ValueError', error_res[4])
        fail_res = res_dict['test_runner.Mocking.test_failures']
        self.assertEqual(fail_res[2], FAIL)
        self.assertEqual(fail_res[3], 'ERROR: A logging log.\n')
        self.assertIn('AssertionError', fail_res[4])
        exp_fail_res = res_dict['test_runner.Mocking.test_expected_failures']
        self.assertEqual(exp_fail_res[2], EXPECTED_FAIL)
        self.assertIn('AssertionError', exp_fail_res[4])
        unexp_success_res = res_dict['test_runner.Mocking.test_unexpected_successes']
        self.assertEqual(unexp_success_res[2], UNEXPECTED_PASS)
        self.assertEqual(unexp_success_res[4], 'No Exceptions')

    @unittest.expectedFailure
    def test_init_with_non_iterable_reporters(self):
        unishark.BufferedTestRunner(unishark.HtmlReporter()).run(self.suite)

    @unittest.expectedFailure
    def test_init_with_wrong_reporter_type(self):
        class MyReporter():
            def __init__(self):
                pass

            def report(self, result):
                pass

            def collect(self):
                pass
        unishark.BufferedTestRunner([MyReporter()]).run(self.suite)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(RunnerTestCase)
    rslt = unittest.TextTestRunner(verbosity=2).run(suite)
    import sys
    sys.exit(0 if rslt.wasSuccessful() else 1)

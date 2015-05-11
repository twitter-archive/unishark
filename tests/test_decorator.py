import unittest
import unishark
import time
from unishark.exception import MultipleErrors


class DecoratorTestCase(unittest.TestCase):
    def test_data_driven_json_style(self):
        @unishark.data_driven(*[{'a': 1, 'b': 2, 'sum': 3}, {'a': 3, 'b': 4, 'sum': 7}])
        def mock_test(count, option=1, **param):
            count.append(1)
            self.assertEqual(option, 1)
            self.assertEqual(param['a']+param['b'], param['sum'])

        cnt = []
        mock_test(cnt)
        self.assertEqual(sum(cnt), 2)

    def test_data_driven_args_style(self):
        @unishark.data_driven(a=[1, 3, 0], b=[2, 4], sum=[3, 7])
        def mock_test(count, option=1, **param):
            count.append(1)
            self.assertEqual(option, 1)
            self.assertEqual(param['a']+param['b'], param['sum'])

        cnt = []
        mock_test(cnt)
        self.assertEqual(sum(cnt), 2)

    def test_data_driven_cross_multiply(self):
        @unishark.data_driven(left=list(range(3)), i=list(range(3)))
        @unishark.data_driven(right=list(range(3)), j=list(range(3)))
        def mock_test(res, **param):
            n = param['left'] * param['right']
            i = param['i']
            j = param['j']
            self.assertEqual(n, res[i*3+j])

        mock_test([0, 0, 0, 0, 1, 2, 0, 2, 4])

    @unittest.expectedFailure
    def test_data_driven_invalid_input_1(self):
        @unishark.data_driven([{'a': 1}, {'a': 3}])
        def mock_test(**param):
            print(param['a'])

        mock_test()

    @unittest.expectedFailure
    def test_data_driven_invalid_input_2(self):
        @unishark.data_driven(a=set(range(3)))
        def mock_test(**param):
            print(param['a'])

        mock_test()

    def test_multi_treads_data_driven_json_style(self):
        @unishark.multi_threading_data_driven(2, *[{'a': 1, 'b': 2, 'sum': 3}, {'a': 3, 'b': 4, 'sum': 7}])
        def mock_test(count, option=1, **param):
            count.append(1)
            self.assertEqual(option, 1)
            self.assertEqual(param['a']+param['b'], param['sum'])

        cnt = []
        mock_test(cnt)
        self.assertEqual(sum(cnt), 2)

    def test_multi_threads_data_driven_args_style(self):
        @unishark.multi_threading_data_driven(2, a=[1, 3, 0], b=[2, 4], sum=[3, 7])
        def mock_test(count, option=1, **param):
            count.append(1)
            self.assertEqual(option, 1)
            self.assertEqual(param['a']+param['b'], param['sum'])

        cnt = []
        mock_test(cnt)
        self.assertEqual(sum(cnt), 2)

    def test_multi_threads_data_driven_time(self):
        @unishark.multi_threading_data_driven(10, time=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        def mock_test(count, **param):
            count.append(1)
            time.sleep(param['time'])

        start = time.time()
        cnt = []
        mock_test(cnt)
        self.assertEqual(sum(cnt), 10)
        taken = time.time() - start
        self.assertLess(taken, 3)

    def test_multi_threads_data_driven_errors(self):
        @unishark.multi_threading_data_driven(6, time=[1, 2, 1, 1, 1, 3])
        def mock_test(**param):
            if param['time'] == 1:
                time.sleep(param['time'])
            else:
                raise AssertionError('Error thrown in thread.')

        try:
            mock_test()
            raise AssertionError('No MultipleErrors caught.')
        except MultipleErrors as e:
            self.assertEqual(len(e), 2)

    def test_multi_threads_data_driven_cross_multiply(self):
        @unishark.multi_threading_data_driven(2, time1=[1, 2])
        @unishark.multi_threading_data_driven(3, time2=[1, 1, 1])
        def mock_test(**param):
            t = param['time1'] * param['time2']
            if t == 1:
                time.sleep(t)
            else:
                raise AssertionError('Error thrown in thread.')
        try:
            mock_test()
            raise AssertionError('No MultipleErrors caught.')
        except MultipleErrors as e:
            self.assertEqual(len(e), 1)

    def test_multi_threads_data_driven_single_thread(self):
        @unishark.multi_threading_data_driven(1, a=[1, 3], b=[2, 4], sum=[3, 7, 0])
        def mock_test(count, option=1, **param):
            count.append(1)
            self.assertEqual(option, 1)
            self.assertEqual(param['a']+param['b'], param['sum'])

        cnt = []
        mock_test(cnt)
        self.assertEqual(sum(cnt), 2)

    @unittest.expectedFailure
    def test_multi_threads_data_driven_no_threads(self):
        @unishark.multi_threading_data_driven(*[{'a': 1, 'b': 2, 'sum': 3}, {'a': 3, 'b': 4, 'sum': 7}])
        def mock_test(**param):
            print('%d + %d = %d' % (param['a'], param['b'], param['sum']))

    @unittest.expectedFailure
    def test_multi_threads_data_driven_invalid_threads(self):
        @unishark.multi_threading_data_driven(0, time=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        def mock_test(**param):
            time.sleep(param['time'])

    @unittest.expectedFailure
    def test_multi_threads_data_driven_invalid_threads(self):
        @unishark.multi_threading_data_driven(-1, time=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        def mock_test(**param):
            time.sleep(param['time'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
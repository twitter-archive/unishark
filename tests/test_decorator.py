import unittest
import unishark


class DecoratorTestCase(unittest.TestCase):
    def test_data_driven_json_style(self):
        @unishark.data_driven(*[{'a': 1, 'b': 2, 'sum': 3}, {'a': 3, 'b': 4, 'sum': 7}])
        def mock_test(name, option=1, **param):
            self.assertEqual(name, 'mock')
            self.assertEqual(option, 1)
            self.assertEqual(param['a']+param['b'], param['sum'])

        mock_test('mock')

    def test_data_driven_args_style(self):
        @unishark.data_driven(a=[1, 3], b=[2, 4], sum=[3, 7])
        def mock_test(name, option=1, **param):
            self.assertEqual(name, 'mock')
            self.assertEqual(option, 1)
            self.assertEqual(param['a']+param['b'], param['sum'])

        mock_test('mock')

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

if __name__ == '__main__':
    unittest.main(verbosity=2)
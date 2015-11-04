import unittest
import unishark.suite


class SuiteTestCase(unittest.TestCase):
    def setUp(self):
        super(SuiteTestCase, self).setUp()
        self.loader = unittest.TestLoader()
        self.suite = None

    def test_convert_suite(self):
        self.suite = self.loader.loadTestsFromNames(['tests.mock1.test_module1',
                                                     'tests.mock1.test_module2'])
        tests = unishark.suite.convert(self.suite)
        self.assertEqual(len(tests), 2)
        self.assertEqual(sum([len(t) for t in tests]), 4)
        self.assertEqual(tests.countTestCases(), 10)
        self.suite = self.loader.loadTestsFromNames(['tests.mock1.test_module1.MyTestClass1',
                                                     'tests.mock1.test_module1.MyTestClass2',
                                                     'tests.mock1.test_module2.MyTestClass3',
                                                     'tests.mock1.test_module2.MyTestClass4'])
        tests = unishark.suite.convert(self.suite)
        self.assertEqual(len(tests), 2)
        self.assertEqual(sum([len(t) for t in tests]), 4)
        self.assertEqual(tests.countTestCases(), 10)
        self.suite = self.loader.loadTestsFromNames(['tests.mock1.test_module1.MyTestClass1.test_1',
                                                     'tests.mock1.test_module1.MyTestClass2.test_3',
                                                     'tests.mock1.test_module2.MyTestClass3.test_5',
                                                     'tests.mock1.test_module2.MyTestClass4.test_8'])
        tests = unishark.suite.convert(self.suite)
        self.assertEqual(len(tests), 2)
        self.assertEqual(sum([len(t) for t in tests]), 4)
        self.assertEqual(tests.countTestCases(), 4)
        from tests.mock1 import test_module1
        self.suite = self.loader.loadTestsFromModule(test_module1)
        tests = unishark.suite.convert(self.suite)
        self.assertEqual(len(tests), 1)
        self.assertEqual(sum([len(t) for t in tests]), 2)
        self.assertEqual(tests.countTestCases(), 4)
        self.suite = self.loader.loadTestsFromTestCase(test_module1.MyTestClass1)
        tests = unishark.suite.convert(self.suite)
        self.assertEqual(len(tests), 1)
        self.assertEqual(sum([len(t) for t in tests]), 1)
        self.assertEqual(tests.countTestCases(), 2)


if __name__ == '__main__':
    unittest.main()
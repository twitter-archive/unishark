import unittest
import logging


log = logging.getLogger(__name__)


class MyTestClass3(unittest.TestCase):

    def test_5(self):
        """Here is test_5's doc str"""
        log.error('This is a case having an error that is not AssertionError. '
                  'unittest distinguishes "failure" and "error" by if the case raises an AssertionError or not.')
        raise TypeError

    def test_6(self):
        """Here is test_6's doc str"""
        log.info('Here is logging of test_6')
        self.assertEqual(1, 1)

    @unittest.skip('Reason of skipping test_7')
    def test_7(self):
        """Here is test_7's doc str"""
        self.assertEqual(1, 1)


class MyTestClass4(unittest.TestCase):
    def test_8(self):
        """Here is test_8's doc str"""
        log.debug('There is an error')
        raise TypeError

    def test_9(self):
        """Here is test_9's doc str"""
        log.error('This is a failure case, which raises AssertionError')
        self.assertEqual(1, 2)

    def test_10(self):
        """Here is test_10's doc str"""
        log.info('Here is test_10 INFO log')
        log.debug('Here is test_10 DEBUG log')
        self.assertEqual(1, 1)


if __name__ == '__main__':
    import unishark
    reporter = unishark.HtmlReporter(dest='log')
    unittest.main(testRunner=unishark.BufferedTestRunner([reporter]))
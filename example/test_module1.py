__author__ = 'Ying Ni <yni@twitter.com>'

import unishark
import unittest
import logging


log = logging.getLogger(__name__)


def data_provider():
    return [{'user_id': 1, 'passwd': 'abc'}, {'user_id': 2, 'passwd': 'def'}]


class MyTestClass1(unittest.TestCase):
    @unishark.data_driven(*data_provider())
    def repeat_part(self, **param):
        log.info('user_id: %d, passwd: %s' % (param['user_id'], param['passwd']))

    def test_1(self):
        """Here is test_1's doc str"""
        log.info('This is an example of data_driven decorator')
        self.repeat_part()

    @unishark.data_driven(user_id=[1, 2, 3, 4], passwd=['a', 'b', 'c', 'd'])
    def test_2(self, **param):
        """Here is test_2's doc str"""
        log.info('Another example of data_driven decorator')
        log.info('user_id: %d, passwd: %s' % (param['user_id'], param['passwd']))


class MyTestClass2(unittest.TestCase):
    @unittest.skip('Here is the reason of skipping test_3')
    def test_3(self):
        """Here is test_3's doc str"""
        log.info('Here is logging of test_3')
        self.assertEqual(1, 2)

    def test_4(self):
        """Here is test_4's doc str"""
        log.info('Here is logging of test_4')
        log.info('Try escape: <div>')
        self.assertEqual(1, 1)


if __name__ == '__main__':
    reporter = unishark.HtmlReporter(dest='./log')
    unittest.main(testRunner=unishark.BufferedTestRunner([reporter]))

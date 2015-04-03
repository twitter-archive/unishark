import sys
import os
cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(cur_dir, os.pardir))
import unittest
import logging
import unishark
from time import sleep

log = logging.getLogger(__name__)


class MyTestClass5(unittest.TestCase):

    def test_11(self):
        """Here is test_11's doc str"""
        log.info('Here is logging of test_11')
        sleep(2)
        self.assertEqual(1, 1)

    def test_12(self):
        """Here is test_12's doc str"""
        log.info('Here is logging of test_12')
        sleep(3)
        self.assertEqual(1, 1)


class MyTestClass6(unittest.TestCase):
    def test_13(self):
        """Here is test_13's doc str"""
        log.info('Here is logging of test_13')
        sleep(2)
        self.assertEqual(1, 1)

    def test_14(self):
        """Here is test_14's doc str"""
        log.info('Here is logging of test_14')
        sleep(4)
        self.assertEqual(1, 1)


class MyTestClass7(unittest.TestCase):
    def test_15(self):
        """Here is test_15's doc str"""
        log.info('Here is logging of test_15')
        sleep(2)
        self.assertEqual(1, 1)

    def test_16(self):
        """Here is test_16's doc str"""
        log.info('Here is logging of test_16')
        sleep(1)
        self.assertEqual(1, 1)


class MyTestClass8(unittest.TestCase):
    @unishark.data_driven(left=list(range(1, 10)))
    @unishark.data_driven(right=list(range(1, 10)))
    def test_17(self, **param):
        """Test cross-multiply data-driven"""
        l = param['left']
        r = param['right']
        sleep(0.1)
        log.info(str(l) + ' x ' + str(r) + ' = ' + str(l * r))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = unishark.BufferedTestRunner().run(suite, name='mytest3', max_workers=2)
    reporter = unishark.HtmlReporter(dest='log')
    reporter.report(result)
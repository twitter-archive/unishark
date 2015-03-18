import unittest
import unishark
import os
import shutil
from xml.dom import minidom
from tests import logger


class Mocking1(unittest.TestCase):
    def test_successes(self):
        """This is doc string."""
        self.assertEqual(1, 1)
        logger.info(u'{\n\t"\u6c49": "<~!@#$%^&*()_+=-?/>,;."\n}')

    @unittest.skip('skip reason.')
    def test_skipped(self):
        self.assertEqual(2, 2)

    @unittest.expectedFailure
    def test_unexpected_successes(self):
        logger.error('Failed (unexpected success).')
        self.assertTrue(True)


class Mocking2(unittest.TestCase):
    def test_failures(self):
        logger.error('Failed.')
        self.assertEqual(1, 2, u'{\n\t"\u6c49": "<~!@#$%^&*()_+=-?/>,;."\n}')

    @unittest.expectedFailure
    def test_expected_failures(self):
        logger.info('Passed (expected failure).')
        self.assertTrue(False)

    def test_errors(self):
        logger.error('Error.')
        raise ValueError(u'{\n\t"\u6c49": "<~!@#$%^&*()_+=-?/>,;."\n}')


class ReporterTestCase(unittest.TestCase):
    def setUp(self):
        super(ReporterTestCase, self).setUp()
        loader = unittest.TestLoader()
        self.suite1 = loader.loadTestsFromTestCase(Mocking1)
        self.suite2 = loader.loadTestsFromTestCase(Mocking2)
        self.dest = 'results'
        if os.path.exists(self.dest):
            shutil.rmtree(self.dest)

    def tearDown(self):
        if os.path.exists(self.dest):
            shutil.rmtree(self.dest)

    def test_html_report(self):
        reporter = unishark.HtmlReporter()
        result = unishark.BufferedTestRunner([]).run(self.suite1)
        reporter.suite_name = 'My Suite 1'
        reporter.suite_description = u'Description 1: \n\t<~!@#$%^&*()_+=-?/>,;."\u6c49"\r\n'
        reporter.report(result)

        result = unishark.BufferedTestRunner([]).run(self.suite2)
        reporter.suite_name = 'My Suite 2'
        reporter.suite_description = u'Description 2: \n\t<~!@#$%^&*()_+=-?/>,;."\u6c49"\r\n'
        reporter.report(result)

        reporter.collect()
        exp_filenames = ['index.html', 'overview.html', 'My Suite 1_result.html', 'My Suite 2_result.html']
        filenames = os.listdir(self.dest)
        self.assertSetEqual(set(filenames), set(exp_filenames))

    def test_junit_report(self):
        reporter = unishark.XUnitReporter()
        result = unishark.BufferedTestRunner([]).run(self.suite1)
        reporter.suite_name = 'My Suite 1'
        reporter.suite_description = u'Description 1: \n\t<~!@#$%^&*()_+=-?/>,;."\u6c49"\r\n'
        reporter.report(result)

        result = unishark.BufferedTestRunner([]).run(self.suite2)
        reporter.suite_name = 'My Suite 2'
        reporter.suite_description = u'Description 2: \n\t<~!@#$%^&*()_+=-?/>,;."\u6c49"\r\n'
        reporter.report(result)

        reporter.collect()
        exp_filenames = ['My Suite 1_xunit_result.xml', 'My Suite 2_xunit_result.xml', 'summary_xunit_result.xml']
        filenames = os.listdir(self.dest)
        self.assertSetEqual(set(filenames), set(exp_filenames))
        for filename in filenames:
            minidom.parse(os.path.join(self.dest, filename))

    def test_multi_reporters(self):
        self.dest = 'reports'
        reporter1 = unishark.HtmlReporter(title='My Title',
                                          description=u'My Description: : \n\t<~!@#$%^&*()_+=-?/>,;."\u6c49"\r\n',
                                          dest=self.dest)
        reporter2 = unishark.XUnitReporter(title='My Title',
                                           description=u'My Description: : \n\t<~!@#$%^&*()_+=-?/>,;."\u6c49"\r\n',
                                           dest=self.dest)
        unishark.BufferedTestRunner([reporter1, reporter2]).run(self.suite1)
        reporter1.collect()
        reporter2.collect()
        exp_filenames = ['suite_xunit_result.xml', 'summary_xunit_result.xml',
                         'index.html', 'overview.html', 'suite_result.html']
        filenames = os.listdir(os.path.join(self.dest))
        self.assertSetEqual(set(filenames), set(exp_filenames))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ReporterTestCase)
    rslt = unittest.TextTestRunner(verbosity=2).run(suite)
    import sys
    sys.exit(0 if rslt.wasSuccessful() else 1)
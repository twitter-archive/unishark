__author__ = 'Ying Ni <yni@twitter.com>'

import abc
import unishark
import sys
import logging

log = logging.getLogger(__name__)


class TestProgram(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self):
        pass


class DefaultTestProgram(TestProgram):
    def __init__(self, test_dict_conf, title='Reports', description='', dest='./results',
                 verbosity=1, show_runtime_descriptions=False):
        self.test_dict_conf = test_dict_conf
        self.title = title
        self.description = description
        self.dest = dest
        self.verbosity = verbosity
        self.show_runtime_descriptions = show_runtime_descriptions
        self.reporters = [unishark.HtmlReporter(title=self.title, description=self.description, dest=self.dest)]

    def run(self):
        exit_code = 0
        suites = unishark.DefaultTestLoader().load_test_from_dict(self.test_dict_conf)
        for suite_name, suite_content in suites.items():
            package_name = suite_content['package']
            suite = suite_content['suite']
            for reporter in self.reporters:
                reporter.suite_name = suite_name
                reporter.suite_description = 'Package: ' + package_name
            result = unishark.BufferedTestRunner(self.reporters, verbosity=self.verbosity,
                                                 descriptions=self.show_runtime_descriptions).run(suite)
            exit_code += 0 if result.wasSuccessful() else 1
        for reporter in self.reporters:
            reporter.collect()
        return exit_code


def main(test_program):
    if not isinstance(test_program, TestProgram):
        raise TypeError
    exit_code = test_program.run()
    log.info('Exit Code: %d' % exit_code)
    sys.exit(exit_code)
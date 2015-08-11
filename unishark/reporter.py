# Copyright 2015 Twitter, Inc and other contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import jinja2
import re
import os
import codecs
import datetime
import abc
import unishark
from unishark.runner import (PASS, SKIPPED, ERROR, FAIL, EXPECTED_FAIL, UNEXPECTED_PASS)
import threading

_status_to_str = {
    PASS: 'Passed',
    SKIPPED: 'Skipped',
    ERROR: 'Error',
    FAIL: 'Failed',
    EXPECTED_FAIL: 'Passed',
    UNEXPECTED_PASS: 'Failed'
}


class Reporter(object):
    """Base class of all reporter classes"""
    __metaclass__ = abc.ABCMeta

    lock = threading.RLock()

    def __init__(self):
        self._actual_duration = None

    def set_actual_duration(self, duration):
        self._actual_duration = duration

    @abc.abstractmethod
    def report(self, result):
        pass

    @abc.abstractmethod
    def collect(self):
        pass


class Summary(object):
    """Base class of representation classes"""
    def __init__(self, name):
        self.name = name
        self.description = ''
        self.duration = 0.0
        self.run = 0
        self.passed = 0
        self.skipped = 0
        self.error = 0
        self.fail = 0
        self.rate = ''
        self.category = ''

    def round_duration(self):
        self.duration = round(self.duration, 3)

    def calc_rate(self):
        if self.run:
            self.rate = str(round((self.passed + self.skipped) * 100.0 / self.run, 2)) + '%'
        else:
            self.rate = '0%'

    def calc_category(self):
        self.category = (self.fail or self.error) and 'danger' or self.skipped and 'warning' or 'success'


class TestsSummary(Summary):
    def __init__(self, name):
        super(TestsSummary, self).__init__(name)
        self.suite_sum_list = []

    def build(self, actual_duration=None):
        if self.suite_sum_list:
            if actual_duration is not None:
                self.duration = actual_duration
            else:
                self.duration = sum(map(lambda s: s.duration, self.suite_sum_list))
            self.run = sum(map(lambda s: s.run, self.suite_sum_list))
            self.passed = sum(map(lambda s: s.passed, self.suite_sum_list))
            self.skipped = sum(map(lambda s: s.skipped, self.suite_sum_list))
            self.error = sum(map(lambda s: s.error, self.suite_sum_list))
            self.fail = sum(map(lambda s: s.fail, self.suite_sum_list))
            self.round_duration()
            self.calc_category()
            self.calc_rate()


class SuiteSummary(Summary):
    def __init__(self, name):
        super(SuiteSummary, self).__init__(name)
        self.mod_sum_list = []

    def build(self, result):
        # Suite summary
        self.description = result.description
        self.duration = result.sum_duration
        self.run = result.testsRun
        self.passed = result.successes + len(result.expectedFailures)
        self.skipped = len(result.skipped)
        self.error = len(result.errors)
        self.fail = len(result.failures) + len(result.unexpectedSuccesses)
        self.round_duration()
        self.calc_category()
        self.calc_rate()
        # Module summary
        mod_id = cls_id = mth_id = 0
        for mod_name in result.results:
            mod_id += 1
            mod_results = result.results[mod_name]
            mod_sum = ModuleSummary(mod_id, mod_name)
            # Class summary
            for cls_name in mod_results:
                cls_id += 1
                result_list = mod_results[cls_name]
                cls_sum = ClassSummary(cls_id, cls_name)
                for r in result_list:
                    # Method summary
                    mth_id += 1
                    mth_name, mth_doc, mth_duration, mth_status, mth_output, mth_traceback = r
                    mth_sum = MethodSummary(mth_id, mth_name, mth_duration, mth_status,
                                            mth_doc, mth_output, mth_traceback)
                    # Fill stats in class summary
                    cls_sum.mth_sum_list.append(mth_sum)
                    cls_sum.run += 1
                    cls_sum.duration += mth_duration
                    if mth_status == EXPECTED_FAIL or mth_status == PASS:
                        cls_sum.passed += 1
                    elif mth_status == UNEXPECTED_PASS or mth_status == FAIL:
                        cls_sum.fail += 1
                    elif mth_status == SKIPPED:
                        cls_sum.skipped += 1
                    else:
                        cls_sum.error += 1
                cls_sum.round_duration()
                cls_sum.calc_category()
                cls_sum.calc_rate()
                # Skip filling stats in module summary
                mod_sum.cls_sum_list.append(cls_sum)
            self.mod_sum_list.append(mod_sum)


class ModuleSummary(Summary):
    def __init__(self, mid, name):
        super(ModuleSummary, self).__init__(name)
        self.mid = 'mod-' + str(mid)
        self.cls_sum_list = []


class ClassSummary(Summary):
    def __init__(self, cid, name):
        super(ClassSummary, self).__init__(name)
        self.cid = 'cls-' + str(cid)
        self.mth_sum_list = []


class MethodSummary(Summary):
    def __init__(self, fid, name, duration, status, doc, output, trace_back):
        super(MethodSummary, self).__init__(name)
        self.fid = 'mth-' + str(fid)
        self.duration = duration
        self.round_duration()
        self.status = _status_to_str[status]
        self.category = (status == PASS or status == EXPECTED_FAIL) and 'pass' \
            or (status == FAIL or status == UNEXPECTED_PASS) and 'fail' \
            or status == SKIPPED and 'skipped' \
            or 'error'
        self.description = doc
        self.output = output
        self.trace_back = trace_back


class HtmlReporter(Reporter):
    def __init__(self, dest='results',
                 overview_title='Reports',
                 overview_description='',
                 templates_path=None,
                 report_template=None,
                 overview_template=None,
                 index_template=None):
        super(HtmlReporter, self).__init__()
        self.dest = dest
        self._tests_sum = TestsSummary(overview_title)
        self._tests_sum.description = overview_description
        if templates_path and report_template and overview_template and index_template:
            loader = jinja2.FileSystemLoader(templates_path, encoding='utf-8')
            self.report_template = report_template
            self.overview_template = overview_template
            self.index_template = index_template
        else:
            loader = jinja2.PackageLoader(unishark.PACKAGE, package_path='templates', encoding='utf-8')
            self.report_template = 'report.html'
            self.overview_template = 'overview.html'
            self.index_template = 'index.html'
        self.jinja_env = jinja2.Environment(loader=loader, autoescape=False)

        # Add converting newline to <br> filter
        @jinja2.evalcontextfilter
        def nl2br(eval_ctx, text):
            paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
            result = u'\n\n'.join(paragraph_re.split(jinja2.escape(text)))
            result = result.replace('\n', '<br/>\n')
            if eval_ctx.autoescape:
                result = jinja2.Markup(result)
            return result
        self.jinja_env.filters['nl2br'] = nl2br

        # Add <pre> tag wrapper filter
        @jinja2.evalcontextfilter
        def pre(eval_ctx, value):
            _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
            text = u'\n\n'.join(u'<pre>%s</pre>' % p
                                for p in _paragraph_re.split(jinja2.escape(value)))
            if eval_ctx.autoescape:
                text = jinja2.Markup(text)
            return text
        self.jinja_env.filters['pre'] = pre

    def _make_output_dir(self):
        with Reporter.lock:
            if not os.path.exists(self.dest):
                os.makedirs(self.dest)

    def report(self, result):
        self._make_output_dir()
        # Heading
        date_time = str(datetime.datetime.now())
        app = unishark.PACKAGE
        version = unishark.VERSION
        # Summary
        suite_sum = SuiteSummary(result.name)
        suite_sum.build(result)
        # Generate report from template
        template = self.jinja_env.get_template(self.report_template)
        html = template.render(app=app,
                               version=version,
                               date_time=date_time,
                               suite_sum=suite_sum)
        filename = os.path.join(self.dest, suite_sum.name + '_result.html')
        with codecs.open(filename, encoding='utf-8', mode='w+') as f:
            f.write(html)

        self._tests_sum.suite_sum_list.append(suite_sum)

    def collect(self):
        self._make_output_dir()
        self._generate_overview()
        self._generate_index()

    def _generate_overview(self):
        # Overview heading
        date_time = str(datetime.datetime.now())
        app = unishark.PACKAGE
        version = unishark.VERSION
        # Summary
        self._tests_sum.build(actual_duration=self._actual_duration)
        # Generate overview from template
        template = self.jinja_env.get_template(self.overview_template)
        html = template.render(app=app,
                               version=version,
                               date_time=date_time,
                               tests_sum=self._tests_sum)
        with codecs.open(os.path.join(self.dest, 'overview.html'), encoding='utf-8', mode='w+') as f:
            f.write(html)

    def _generate_index(self):
        template = self.jinja_env.get_template(self.index_template)
        html = template.render(tests_sum=self._tests_sum)
        with codecs.open(os.path.join(self.dest, 'index.html'), encoding='utf-8', mode='w+') as f:
            f.write(html)


class XUnitReporter(Reporter):
    def __init__(self, dest='results',
                 summary_title='XUnit Reports',
                 templates_path=None,
                 report_template=None,
                 summary_template=None):
        super(XUnitReporter, self).__init__()
        self.dest = dest
        self._tests_sum = TestsSummary(summary_title)
        if templates_path and report_template and summary_template:
            loader = jinja2.FileSystemLoader(templates_path, encoding='utf-8')
            self.report_template = report_template
            self.summary_template = summary_template
        else:
            loader = jinja2.PackageLoader(unishark.PACKAGE, package_path='templates', encoding='utf-8')
            self.report_template = 'junit_suite_result.xml'
            self.summary_template = 'junit_suites_result.xml'
        self.jinja_env = jinja2.Environment(loader=loader, autoescape=False)

    def _make_output_dir(self):
        with Reporter.lock:
            if not os.path.exists(self.dest):
                os.makedirs(self.dest)

    def report(self, result):
        self._make_output_dir()
        # Summary
        suite_sum = SuiteSummary(result.name)
        suite_sum.build(result)
        # Get short method names
        for mod_sum in suite_sum.mod_sum_list:
            for cls_sum in mod_sum.cls_sum_list:
                for mth_sum in cls_sum.mth_sum_list:
                    mth_sum.name = mth_sum.name.split('.')[-1]
        # Generate report from single suite junit result template
        template = self.jinja_env.get_template(self.report_template)
        xml = template.render(suite_sum=suite_sum)
        filename = os.path.join(self.dest, suite_sum.name + '_xunit_result.xml')
        with codecs.open(filename, encoding='utf-8', mode='w+') as f:
            f.write(xml)

        self._tests_sum.suite_sum_list.append(suite_sum)

    def collect(self):
        self._make_output_dir()
        # Summary
        self._tests_sum.build(actual_duration=self._actual_duration)
        # Generate test suites summary
        template = self.jinja_env.get_template(self.summary_template)
        xml = template.render(tests_sum=self._tests_sum)
        with codecs.open(os.path.join(self.dest, 'summary_xunit_result.xml'), encoding='utf-8', mode='w+') as f:
            f.write(xml)
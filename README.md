# unishark [![Build Status](https://travis-ci.org/twitter/unishark.svg?branch=master)](https://travis-ci.org/twitter/unishark) [![Coverage Status](https://coveralls.io/repos/twitter/unishark/badge.png?branch=master)](https://coveralls.io/r/twitter/unishark?branch=master)
  
A lightweight unittest extension (that extends unitest2)
  
* <a href="#Overview">Overview</a>
* <a href="#Prerequisites">Prerequisites</a>
* <a href="#Installation">Installation</a>
* <a href="#The_Test_Config">The Test Config</a>
  - <a href="#Customize_Test_Suites">Customize Test Suites</a>
  - <a href="#Test_Reports">Test Reports</a>
  - <a href="#Concurrent_Tests">Concurrent Tests</a>
* <a href="#Data_Driven">Data Driven</a>
* <a href="#Advanced_Usage">Advanced Usage</a>
* <a href="#More_Examples">More Examples</a>
* <a href="#User_Extension">User Extension</a>
  - <a href="#Customized_Reports">Customized Reports</a>
  - <a href="#Implement_TestProgram">Implement TestProgram</a>
  
<a name="Overview"></a>
## Overview
  
The latest released version: https://pypi.python.org/pypi/unishark
  
unishark extends unittest (to be more accurate, unittest2) in the following ways:
* Customizing test suites with dictionary config (or yaml/json like config).
* Running the tests in parallel.
* Generating polished test reports in HTML/XUnit formats.
* Offering data-driven decorator to accelerate tests writing.
  
You could acquire the first three features for your existent unittests immediately with a single config, without changing any existing code.
  
Here is an example config in YAML format (you could also write it directly in a <code>dict()</code>):
```yaml
suites:
  my_suite_name_1:
    package: my.package.name
    max_workers: 6
    groups:
      my_group_1:
        granularity: module
        modules: [test_module1, test_module2]
        except_classes: [test_module2.MyTestClass3]
        except_methods: [test_module1.MyTestClass1.test_1]
      my_group_2:
        granularity: class
        disable: False
        classes: [test_module3.MyTestClass5]
        except_methods: [test_module3.MyTestClass5.test_11]
  my_suite_name_2:
    package: my.package.name
    max_workers: 2
    groups:
      my_group_1:
        granularity: method
        methods: [test_module3.MyTestClass6.test_13, test_module3.MyTestClass7.test_15]

reporters:
  html:
    class: unishark.HtmlReporter
    kwargs:
      dest: logs
      overview_title: 'Example Report'
      overview_description: 'This is an example report'
  xunit:
    class: unishark.XUnitReporter
    kwargs:
      summary_title: 'Example Report'

test:
  suites: [my_suite_name_1, my_suite_name_2]
  max_workers: 2
  reporters: [html, xunit]
  method_prefix: 'test'
```
  
It defines two test suites with some of the test cases excluded, and tells unishark to run the defined set of tests with multi-threads (max_workers), then generate both HTML and XUnit (default JUnit) format reports at the end of testing.
  
To run it, simply add the following code:
```python
import unishark
import yaml

if __name__ == '__main__':
    dict_conf = None
    with open('your_yaml_config_file', 'r') as f:
        dict_conf = yaml.load(f.read())  # use a 3rd party yaml parser, e.g., PyYAML
    program = unishark.DefaultTestProgram(dict_conf)
    unishark.main(program)
```
  
And a HTML report is like:
![Screenshot 1](https://rawgit.com/twitter/unishark/master/docs/unishark_report_overview.png)
![Screenshot 2](https://rawgit.com/twitter/unishark/master/docs/unishark_report_detail.png)
  
<a name="Prerequisites"></a>
## Prerequisites
  
Language:
* Python 2.7, 3.3, 3.4
  
3rd Party Dependencies:
* Jinja2>=2.7.2
* MarkupSafe>=0.15
* futures>=2.1.1
  
OS:
* Tested: Linux, MacOS X
  
<a name="Installation"></a>
## Installation
  
pip install unishark
  
<a name="The_Test_Config"></a>
## The Test Config
  
Each config must have a **test** section, which has the following keys:
* **suites**: A list of suite names defined in **suites** section. See <a href="#Customize_Test_Suites">Customize Test Suites</a>.
* **reporters**: A list of reporter names defined in **reporters** section. See <a href="#Test_Reports">Test Reports</a>.
* **max_workers**: The max number of threads used to run the test suites. Default is 1 if not set. See <a href="#Concurrent_Tests">Concurrent Tests</a>.
* **method_prefix**: The prefix of the method names used to filter test cases when loading them. Default 'test' if not set. If it is set to '', there will be no filter.
  
<a name="Customize_Test_Suites"></a>
### Customize Test Suites
  
This part describes **suites** section in the test config, with the example in <a href="#Overview">Overview</a>:
* Name of a suite or a group could be anything you like.
* **package**: A dotted path (relative to PYTHONPATH) indicating the python package where your test .py files locate. The tests in one suite have to be in the same package. To collect tests in another package, define another suite. However tests in one package can be divided into several suites.
* **granularity**: One of 'module', 'class' and 'method'.
* **modules**: A list of module names (test file names with .py trimmed). Only takes effect when granularity is 'module'.
* **classes**: A list of dotted class names conforming to 'module.class'. Only takes effect when granularity is 'class'.
* **methods**: A list of dotted method names conforming to 'module.class.method'. Only takes effect when granularity is 'method'.
* **except_classes**: A list of excluded class names conforming to 'module.class'. Only takes effect when granularity is 'module'.
* **except_methods**: A list of excluded methods names conforming to 'module.class.method'. Only takes effect when granularity is 'module' or 'class'.
* **max_workers**: The max number of threads used to run the test cases within a suite. Default is 1 if not set. See <a href="#Concurrent_Tests">Concurrent Tests</a>.
  
To temporarily exclude a group of tests, set boolean attribute 'disable' to True (default False if not set) in a group config:
```yaml
suites:
  ...
    ...
      my_group_1:
        disable: True
```
  
To include/exclude a suite, add/remove the suite name in/from the **suites** list in the **test** section:
```yaml
test:
  suites: [my_suite_1] # will not run my_suite_2
  ...
```
  
<a name="Test_Reports"></a>
### Test Reports
  
This part describes the **reporters** section in the test config, with the example in <a href="#Overview">Overview</a>:
* **class**: A dotted reporter class name.
* **kwargs**: The arguments for initiating the reporter instance.
  
You could define multiple reporters and use all of them to generate different formats of reports for a single run of the tests.
  
To include/exclude a reporter, add/remove the reporter name in/from the **reporters** list in the **test** section:
```yaml
test:
  reporters: [html] # will not generate xunit format reports
  ...
```
  
If the list is empty, no report files will be generated.
  
unishark can buffer logging stream during the running of a test case, and writes all buffered output to report files at the end of testing. To let unishark capture the logging stream and write logs into reports, simply redirect the logging stream to <code>unishark.out</code>, e.g.,
```python
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler = logging.StreamHandler(stream=unishark.out)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger = logging.getLogger('example')
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```
  
or in YAML format,
```yaml
formatters:
  simple:
    format: '%(levelname)s: %(message)s'

handlers:
  myhandler:
    class: logging.StreamHandler
    formatter: simple
    stream: ext://unishark.out

loggers:
  example:
    level: DEBUG
    handlers: [myhandler]
    propagate: False
```
  
**NOTE**: 
* unishark does NOT buffer stdout and stderr. So if you use <code>print('some message')</code> in a test case, the message will be output to stdout during the test running.
* Suite names are reflected in the reports while groups are not. Test cases are grouped by class then module in the reports. **groups** config is simply for conveniently including/excluding a group of test cases by enabling/disabling the group.
  
<a name="Concurrent_Tests"></a>
### Concurrent Tests
  
There are two levels of concurrency: concurrency at classes level within a suite and concurrency at suites level.
  
To enable concurrency within a suite, set 'max_workers' > 1 in the suite config: 
```yaml
suites:
  my_suite_name_1:
    max_workers: 6
    ...
```
  
To enable concurrency at suites level, set 'max_workers' > 1 in the **test** section:
```yaml
test:
  ...
  max_workers: 2
```
  
**NOTE**: 
* Currently only multi-threading is supported, not multi-processing. Multi-threading concurrency will significantly shorten the running time of I/O bound tests (which many practical cases are, e.g., http requests). But it is not so useful when the tests are CPU bound.
* The smallest granularity of the concurrency is class, not method (this is to make sure <code>setUpClass()</code> and <code>tearDownClass()</code> is executed once for each class, unfortunately). This means test cases in the same class are always executed sequentially, and test cases from the different classes might be executed concurrently.
* It is user's responsibility to make sure the test cases are thread-safe before enabling the concurrent tests. For example, It is dangerous for any method, including <code>setUpClass()</code>/<code>tearDownClass()</code> and <code>setUp()</code>/<code>tearDown()</code>, to modify a cross-classes shared resource, while it is OK for them to modify a class-scope shared resource.
* Technically one can split a class into two suites (by loading test cases with 'method' granularity), and run the methods in the same class concurrently by running the two suites concurrently (but why would you do that?). In this case, <code>setUpClass()</code>/<code>tearDownClass()</code> will be executed twice for the same class, and modifying a class-scope shared resource might be a problem.
* To achieve full concurrency, set 'max_workers' >= number of classes within a suite and set 'max_workers' >= number of suites in the **test** section.
* If 'max_workers' is not set or its value <= 1, it is just sequential running.

<a name="Data_Driven"></a>
## Data Driven
  
Here are some effects of using <code>@unishark.data_driven</code>.  
'Json' style data-driven. This style is good for loading the data in json format to drive the test case: 
```python
@unishark.data_driven(*[{'userid': 1, 'passwd': 'abc'}, {'userid': 2, 'passwd': 'def'}])
def test_data_driven(self, **param):
    print('userid: %d, passwd: %s' % (param['userid'], param['passwd']))
```
  
Results:
```
userid: 1, passwd: abc
userid: 2, passwd: def
```
  
'Args' style data-driven:
```python
@unishark.data_driven(userid=[1, 2, 3, 4], passwd=['a', 'b', 'c', 'd'])
def test_data_driven(self, **param):
    print('userid: %d, passwd: %s' % (param['userid'], param['passwd']))
```
  
Results:
```
userid: 1, passwd: a
userid: 2, passwd: b
userid: 3, passwd: c
userid: 4, passwd: d
```
  
Cross-multiply data-driven:
```python
@unishark.data_driven(left=list(range(10)))
@unishark.data_driven(right=list(range(10)))
def test_data_driven(self, **param):
    l = param['left']
    r = param['right']
    print('%d x %d = %d' % (l, r, l * r))
```
  
Results:
```
0 x 1 = 0
0 x 2 = 0
...
1 x 0 = 0
1 x 1 = 1
1 x 2 = 2
...
...
9 x 8 = 72
9 x 9 = 81
```
  
You can get the permutations (with repetition) of the parameters values by doing:
```python
@unishark.data_driven(...)
@unishark.data_driven(...)
@unishark.data_driven(...)
...
```

Multi-threads data-driven in 'json style':
```python
@unishark.multi_threading_data_driven(2, *[{'userid': 1, 'passwd': 'abc'}, {'userid': 2, 'passwd': 'def'}])
def test_data_driven(self, **param):
    print('userid: %d, passwd: %s' % (param['userid'], param['passwd']))
```

Results: same results as using <code>unishark.data_driven</code>, but up to 2 threads are spawned, each running the test with a set of inputs (userid, passwd).

Multi-threads data-driven in 'args style':
```python
@unishark.multi_threading_data_driven(5, time=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
def test_data_driven(self, **param):
    sleep(param['time'])
```

Results: 5 threads are spawned to run the test with 10 sets of inputs concurrently (only sleep 1 sec in each thread).
It takes about 2 sec in total (10 sec if using <code>unishark.data_driven</code>) to run.

**NOTE**: It is user's responsibility to ensure thread-safe within the test method which is decorated by <code>unishark.multi_threading_data_driven</code>.
If exceptions are thrown in one or more threads, the exceptions information will be collected and summarized in the "main" thread and thrown as <code>unishark.exception.MultipleErrors</code>.
  

<a name="Advanced_Usage"></a>
## Advanced Usage
  
unishark is fully compatible with unittest because it is extended from unittest. Here are some examples of mixed use of the two:

Run unittest suite with <code>unishark.BufferedTestRunner</code>: 
```python
if __name__ == '__main__':
    reporter = unishark.HtmlReporter(dest='log')
    unittest.main(testRunner=unishark.BufferedTestRunner(reporters=[reporter]))
```
```python
if __name__ == '__main__':
    import sys
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    reporter = unishark.HtmlReporter(dest='log')
    # This will run the suite with 2 workers and generate 'mytest2_result.html'
    result = unishark.BufferedTestRunner(reporters=[reporter]).run(suite, name='mytest2', max_workers=2)
    sys.exit(0 if result.wasSuccessful() else 1)
```
```python
if __name__ == '__main__':
    import sys
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = unishark.BufferedTestRunner().run(suite, name='mytest3', max_workers=2)
    # Generating reports can be delayed
    reporter = unishark.HtmlReporter(dest='log')
    reporter.report(result)
    # Also generate overview and index pages
    reporter.collect()
```
  
Load test suites with <code>unishark.DefaultTestLoader</code> and run them with <code>unittest.TextTestRunner</code>:
```python
if __name__ == '__main__':
    dict_conf = None
    with open('your_yaml_config_file', 'r') as f:
        dict_conf = yaml.load(f.read())  # use a 3rd party yaml parser, e.g., PyYAML
    suites = unishark.DefaultTestLoader(method_prefix='test').load_tests_from_dict(dict_conf)
    for suite_name, suite_content in suites.items():
        package_name = suite_content['package']
        suite = suite_content['suite']
        max_workers = suite_content['max_workers']
        unittest.TextTestRunner().run(suite)
```
  
<a name="More_Examples"></a>
## More Examples
  
For more examples, please see 'example/' in the project directory. To run the examples, please read 'example/read_me.txt' first.
  
<a name="User_Extension"></a>
## User Extension
  
<a name="Customized_Reports"></a>
### Customized Reports
  
If you prefer a different style of HTML or XUnit reports, passing different template files to the <code>unishark.HtmlReporter</code> or <code>unishark.XUnitReporter</code> constructor is the easiest way:
```yaml
reporters:
  html:
    class: unishark.HtmlReporter
    kwargs:
      dest: logs
      overview_title: 'Example Report'
      overview_description: 'This is an example report'
      templates_path: mytemplates
      report_template: myreport.html
      overview_template: myoverview.html
      index_template: myindex.html
  xunit:
    class: unishark.XUnitReporter
    kwargs:
      summary_title: 'Example Report'
      templates_path: xmltemplates
      report_template: xunit_report.xml
      summary_template: xunit_summary.xml
```
  
**NOTE**:
* The customized templates must also be <a href="http://jinja.pocoo.org/docs/dev/templates">Jinja2</a> templates
* Once you decide to use your own templates, you have to specify all of the 'teamplates_path' and '*_template' arguments. If one of them is None or empty, the reporters will still use the default templates carried with unishark.
  
If the above customization cannot satisfy you, you could write your own reporter class extending <code>unishark.Reporter</code> abstract class. Either passing the reporter instance to <code>unishark.BufferedTestRunner</code> or configuring the initiating in the test config will make unishark run your reporter.
  
<a name="Implement_TestProgram"></a>
### Implement TestProgram
  
You could also write your own test program class extending <code>unishark.TestProgram</code> abstract class. Implement <code>run()</code> method, making sure it returns an integer exit code, and call <code>unishark.main(your_program)</code> to run it.
  

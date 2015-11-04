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
* <a href="#Useful_API">Useful API</a>
  - <a href="#DefaultTestLoader">DefaultTestLoader</a>
* <a href="#Advanced_Usage">Advanced Usage</a>
* <a href="#More_Examples">More Examples</a>
* <a href="#User_Extension">User Extension</a>
  - <a href="#Customized_Reports">Customized Reports</a>
  - <a href="#Implement_TestProgram">Implement TestProgram</a>
  
<a name="Overview"></a>
## Overview
  
The latest released version: https://pypi.python.org/pypi/unishark
  
unishark extends unittest (to be accurate, unittest2) in the following ways:
* Customizing test suites with dictionary config (or yaml/json like config).
* Running the tests concurrently at different levels.
* Generating polished test reports in HTML/XUnit formats.
* Offering data-driven decorator to accelerate tests writing.
  
For existing unittests, the first three features could be gained immediately with a single config, without changing any test code.
  
Here is an example config in YAML format (you could also write it directly in a <code>dict()</code>):
```yaml
suites:
  my_suite_name_1:
    package: my.package.name
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
    concurrency:
      level: module
      max_workers: 2
  my_suite_name_2:
    package: my.package.name
    groups:
      my_group_1:
        granularity: method
        methods: [test_module3.MyTestClass6.test_13, test_module3.MyTestClass7.test_15]
    concurrency:
      level: class
      max_workers: 2
  my_suite_name_3:
    package: another.package.name
    groups:
      group_1:
        granularity: package
        pattern: '(\w+\.){2}test\w*'
        except_modules: [module1, module2]
        except_classes: [module3.Class1, module3.Class3]
        except_methods: [module3.Class2.test_1, module4.Class2.test_5]
    concurrency:
      level: method
      max_workers: 20
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
  suites: [my_suite_name_1, my_suite_name_2, my_suite_name_3]
  concurrency:
    max_workers: 3
  reporters: [html, xunit]
  name_pattern: '^test\w*'
```
  
It configures 3 test suites with some of the test cases excluded, and running the defined set of tests concurrently (multi-threads), and generating both HTML and XUnit (default JUnit) format reports at the end of tests.

**NOTE: For versions below 0.3.0, 'max_workers' was set directly under 'test', and 'max_workers' and 'concurrency_level' were set directly under '\<suite name\>'. For versions since 0.3.0, there is 'concurrency' sub-dict.**
  
To run it, simply add the following code:
```python
import unishark
import yaml

if __name__ == '__main__':
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
* Python 2.7, 3.3, 3.4, 3.5
  
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
  
Each config must have a **test** dict, which has the following keys:
* **test['suites']**: Required. A list of suite names defined in **suites** dict. See <a href="#Customize_Test_Suites">Customize Test Suites</a>.
* **test['reporters']**: Optional. A list of reporter names defined in **reporters** dict. See <a href="#Test_Reports">Test Reports</a>.
* **test['concurrency']** (since 0.3.0): Optional. See <a href="#Concurrent_Tests">Concurrent Tests</a>.
* **test['concurrency']['max_workers']**: Required if 'concurrency' is defined. The max number of workers allocated to run the test suites.
* **test['concurrency']['timeout']**: Optional. The maximum number of seconds to wait before getting results. Can be an int or float. Default is None(no limit to the wait time). The wait only happens when max_workers > 1.
* **test['name_pattern']**: Optional. A python regular expression to match the test method names. All the tests whose method name does not match the pattern will be filtered out. Default **'^test\w*'** if not set.
  
<a name="Customize_Test_Suites"></a>
### Customize Test Suites
  
This part describes **suites** dict in the test config, with the example in <a href="#Overview">Overview</a>:
* Name of a suite or a group could be anything you like.
* **suites[\<suite name\>]['package']**: Optional. A dotted path (relative to PYTHONPATH) indicating the python package where your test .py files locate. The tests in one suite have to be in the same package. To collect tests in another package, define another suite. However tests in one package can be divided into several suites.
* **suites[\<suite name\>]['concurrency']** (since 0.3.0): Optional. Default is {'max_workers': 1, 'level': 'class', 'timeout': None}. See <a href="#Concurrent_Tests">Concurrent Tests</a>.
* **suites[\<suite name\>]['concurrency']['max_workers']**: Required if 'concurrency' is defined. The max number of workers allocated to run the tests within a suite.
* **suites[\<suite name\>]['concurrency']['level']**: Optional. Can be 'module', 'class' or 'method' to run the modules, classes, or methods concurrently. Default is 'class'.
* **suites[\<suite name\>]['concurrency']['timeout']**: Optional. The maximum number of seconds to wait before getting the suite result. Can be an int or float. Default is None(no limit to the wait time). The wait only happens when max_workers > 1.
* **suites[\<suite name\>]['groups'][\<group name\>]['granularity']**: Required. Must be one of 'package', 'module', 'class' and 'method'. If granularity is 'package', then suites[\<suite name\>]['package'] must be given.
* **suites[\<suite name\>]['groups'][\<group name\>]['pattern']**: Optional. Only takes effect when granularity is 'package'. A python regular expression to match tests long names like 'module.class.method' in the package. Default is **'(\w+\\.){2}test\w*'** if not set.
* **suites[\<suite name\>]['groups'][\<group name\>]['modules']**: Required if granularity is 'module'. A list of module names (test file names with .py trimmed).
* **suites[\<suite name\>]['groups'][\<group name\>]['classes']**: Required if granularity is 'class'. A list of dotted class names conforming to 'module.class'.
* **suites[\<suite name\>]['groups'][\<group name\>]['methods']**: Required if granularity is 'method'. A list of dotted method names conforming to 'module.class.method'.
* **suites[\<suite name\>]['groups'][\<group name\>]['except_modules']**: Optional. Only takes effect when granularity is 'package'. A list of excluded module names.
* **suites[\<suite name\>]['groups'][\<group name\>]['except_classes']**: Optional. Only takes effect when granularity is 'package' or 'module'. A list of excluded class names conforming to 'module.class'. 
* **suites[\<suite name\>]['groups'][\<group name\>]['except_methods']**: Optional. Only takes effect when granularity is 'package', 'module' or 'class'. A list of excluded method names conforming to 'module.class.method'.
* **suites[\<suite name\>]['groups'][\<group name\>]['disable']**: Optional. Excludes the group of tests if the value is True. Default is False if not set.
  
To include/exclude a suite, add/remove the suite name in/from the **test['suites']** list in the **test** dict:
```yaml
test:
  suites: [my_suite_1] # will only run my_suite_1
  ...
```
  
<a name="Test_Reports"></a>
### Test Reports
  
This part describes the **reporters** dict in the test config, with the example in <a href="#Overview">Overview</a>:
* **reporters['class']**: Required if a reporter is defined. A dotted reporter class name.
* **reporters['kwargs']**: Optional. The arguments for initiating the reporter instance.
  
The arguments of the built-in HtmlReporter and their default values are:
* dest='results'
* overview_title='Reports'
* overview_description=''
* templates_path=None
* report_template=None
* overview_template=None
* index_template=None
  
The arguments of the built-in XUnitReporter and their default values are:
* dest='results'
* summary_title='XUnit Reports'
* templates_path=None
* report_template=None
* summary_template=None
  
Configuring multiple reporters which generate different formats of reports is allowed, and only a single run of the tests is needed to generate all different formats.
  
To include/exclude a reporter, add/remove the reporter name in/from the **test['reporters']** list in the **test** dict:
```yaml
test:
  reporters: [html] # will only generate html format reports
  ...
```
  
If the list is empty, no report files will be generated.
  
unishark can buffer logging stream during the running of a test case, and writes all buffered output to report files at the end of tests. To let unishark capture the logging stream and write logs into reports, simply redirect the logging stream to <code>unishark.out</code>, e.g.,
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
  
Concurrency in unishark can be:  
* concurrent execution of multiple suites.
* concurrent execution within a suite:  
  - at module level.
  - at class level.
  - at method level.
  
To enable concurrent execution of multiple suites, set 'concurrency' sub-dict (since 0.3.0) in the 'test' dict:
```yaml
test:
  ...
  concurrency:
    max_workers: 3
    timeout: 1800
```
  
To enable concurrent execution within a suite, set 'concurrency' sub-dict (since 0.3.0) in the '\<suite name\>' dict:
```yaml
suites:
  my_suite_name_1:
    concurrency:
      max_workers: 6
      level: method
      timeout: 1800
    ...
```
  
**NOTE**:
* For versions **below 0.3.0**, 'max_workers' was set directly under 'test', and 'max_workers' and 'concurrency_level' were set directly under '\<suite name\>'.
* Currently only multi-threading is supported, not multi-processing. Multi-threading concurrency will significantly shorten the running time of I/O bound tests (which many practical cases are, e.g., http requests). But it is not so useful when the tests are CPU bound due to python's GIL.
* If max_workers <= 1, it is just sequential running.
* **Users are responsible for reasoning the thread-safety** before enabling concurrent execution. For example, when concurrency level is 'method', race conditions will occur if any method including setUp/tearDown tries to modify a class-scope shared resource. In this case, user should set concurrency level to 'class' or 'module'.
* Versions **since 0.3.0** use a new concurrent execution model internally. Test fixtures setUpModule/tearDownModule setUpClass/tearDownClass will be executed **once and only once** in a suite no matter what concurrency level(module/class/method) of the suite is.
* For versions **below 0.3.0**: on the condition of thread-safety, the recommended concurrency level for most user cases are: If there is setUpModule/tearDownModule in a module, set 'concurrency_level' to 'module', otherwise setUpModule/tearDownModule may run multiple times for the module; If there is setUpClass/tearDownClass in a class, set 'concurrency_level' to 'class' or 'module', otherwise setUpClass/tearDownClass may run multiple times for the class; If there are only setUp/tearDown, 'concurrency_level' can be set to any level.
* To achieve full concurrency, set suites[\<suite name\>]['concurrency']['max_workers'] >= number of modules/classes/methods when concurrency level is module/class/method, and set test['concurrency']['max_workers'] >= number of test['suites'].
  

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
  

<a name="Useful_API"></a>
## Useful API
  
<a name="DefaultTestLoader"></a>
### DefaultTestLoader
  
* **load_tests_from_dict(dict_conf)**: Loads tests from a dictionary config described in <a href="#The_Test_Config">The Test Config</a>. Returns a suites dictionary with suite names as keys.
* **load_tests_from_package(pkg_name, regex=None)**: Returns a unittest.TestSuite instance containing the tests whose dotted long name 'module.class.method' matches the given regular expression and short method name matches DefaultTestLoader.name_pattern. A dotted package name must be provided. regex is default to '(\w+\\.){2}test\w*'.
* **load_tests_from_modules(mod_names, regex=None)**: Returns a unittest.TestSuite instance containing the tests whose dotted name 'class.method' matches the given regular expression and short method name matches DefaultTestLoader.name_pattern. A list of dotted module names must be provided. regex is default to '\w+\\.test\w*'.
  

<a name="Advanced_Usage"></a>
## Advanced Usage
  
unishark is totally compatible with unittest because it extends unittest. Here are some examples of mixed use of the two:

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
    # Run methods concurrently with 10 workers and generate 'mytest2_result.html'
    result = unishark.BufferedTestRunner(reporters=[reporter]).run(suite, name='mytest2', max_workers=10, concurrency_level='method')
    sys.exit(0 if result.wasSuccessful() else 1)
```
```python
if __name__ == '__main__':
    import sys
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    # Run classes concurrently with 2 workers
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
    suites = unishark.DefaultTestLoader(name_pattern='^test\w*').load_tests_from_dict(dict_conf)
    for suite_name, suite_content in suites.items():
        package_name = suite_content['package']
        suite = suite_content['suite']
        concurrency = suite_content['concurrency']
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
  
If the above customization cannot satisfy you, you could write your own reporter class extending <code>unishark.Reporter</code> abstract class. Either passing the reporter instance to <code>unishark.BufferedTestRunner</code> or configuring the constructor in the test config will make unishark run your reporter.
  
<a name="Implement_TestProgram"></a>
### Implement TestProgram
  
You could also write your own test program class extending <code>unishark.TestProgram</code> abstract class. Implement <code>run()</code> method, making sure it returns an integer exit code, and call <code>unishark.main(your_program)</code> to run it.
  

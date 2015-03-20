# unishark - another unittest extension
  
* <a href="#Overview">Overview</a>
* <a href="#Prerequisites">Prerequisites</a>
* <a href="#User_Guide">User Guide</a>
  - <a href="#Test_Reports">Test Reports</a>
  - <a href="#Customizing_Test_Suites">Customizing Test Suites</a>
  - <a href="#Utils">Utils</a>
  
<a name="Overview"></a>

## Overview
  
unishark extends unittest (to be more accurate, unittest2) in the following ways:
* Generating polished test reports in different formats such as HTML, XUnit, etc..
* Organizing test suites with dictionary config (or yaml/json like config).
* Offering test utils such as data-driven decorator to accelerate tests writing.
  
Extending existent unittest code with one or more unishark features is easy.
  
<a name="Prerequisites"></a>

## Prerequisites
  
Language:
* Python 2.7.x, Python 3.x
  
3rd Parties:
* Jinja2>=2.7.2
* MarkupSafe>=0.23
  
<a name="User_Guide"></a>

## User Guide
  
<a name="Test_Reports"></a>

### Test Reports
  
**Quick Start**
  
To generate HTML reports:
```python
if __name__ == '__main__':
    reporter = unishark.HtmlReporter()
    unittest.main(testRunner=unishark.BufferedTestRunner([reporter]))
```
  
To generate XUnit reports (currently JUnit format):
```python
if __name__ == '__main__':
    reporter = unishark.XUnitReporter()
    unittest.main(testRunner=unishark.BufferedTestRunner([reporter]))
```
  
<code>unishark.BufferedTestRunner</code> buffers <code>sys.stdout</code> and <code>sys.stderr</code> output (including exceptions information) during the running of a test case, and writes all buffered output to report files at the end of the tests. To let unishark capture the logging stream and write logs into reports, simply redirect the logging stream to <code>unishark.out</code>, e.g.,
```python
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler = logging.StreamHandler(stream=unishark.out)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```
  
or in YAML format,
```yaml
formatters:
  simple:
    format: '%(levelname)s: %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    stream: ext://unishark.out
```
  
**Advanced Usage**
  
The example below shows running unittest suite with <code>unishark.BufferedTestRunner</code> and having both HTML and XUnit reports generated at the same time. The reports will be in <code>./log</code> directory instead of the default output directory <code>./results</code>.
```python
if __name__ == '__main__':
    # Prepare unittest suite
    suite = unittest.TestLoader().loadTestsFromName('MyTestClass', module=test_module)
    # Create reporters
    html_reporter = unishark.HtmlReporter(dest='log')
    xunit_reporter = unishark.XUnitReporter(dest='log')
    # Assign a suite name to this suite (default name is 'suite')
    html_reporter.suite_name = xunit_reporter.suite_name = 'my_suite'
    # Run test suite with BufferedTestRunner and generate reports in both HTML and JUnit formats
    result = unishark.BufferedTestRunner([html_reporter, xunit_reporter]).run(suite)
    # Generate index/summary of the reports
    html_reporter.collect()
    xunit_reporter.collect()
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)
```
  
<a name="Customizing_Test_Suites"></a>

### Customizing Test Suites
  
This section describs how to organize unittest suites with a dictionary or YAML configuration.  
Here is an example in YAML format:
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
        classes: [test_module3.MyTestClass5]
        except_methods: [test_module3.MyTestClass5.test_11]
  my_suite_name_2:
    package: my.package.name
    groups:
      my_group_1:
        granularity: method
        methods: [test_module3.MyTestClass6.test_13, test_module3.MyTestClass7.test_15]
```
  
Notes of the configuration:
* Name of a suite or a group could be anything you like.
* **package**: A dotted package name implying the directory of your test .py files. The tests in one suite have to be in the same package. To collect tests in another package, define another suite.
* **granularity**: One of 'module', 'class' and 'method'.
* **modules**: A list of module names (test file names with .py trimmed). Only takes effect when granularity is 'module'.
* **classes**: A list of dotted class names conforming to 'module.class'. Only takes effect when granularity is 'class'.
* **methods**: A list of dotted method names conforming to 'module.class.method'. Only takes effect when granularity is 'method'.
* **except_classes**: A list of excluded class names conforming to 'module.class'. Only takes effect when granularity is 'module'.
* **except_methods**: A list of excluded methods names conforming to 'module.class.method'. Only takes effect when granularity is 'module' or 'class'.
  
To temporarily exclude a suite or a group, set boolean attribute 'disable' to <code>True</code> in a suite or a group config:
```yaml
suites:
  my_suite_name_1:
    disable: True
    ...
```
```yaml
suites:
  ...
    ...
      my_group_1:
        disable: True
```
  
To run the customized test suites:
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
  
You could also write the configuration directly in a <code>dict()</code>.  
Note that **suite names are reflected in the reports while groups are not**. Test cases are grouped by class then module in the reports in practice. **groups** config is simply for including/excluding a group of test cases by enabling/disabling the group.
  
<a name="Utils"></a>

### Utils
  
**Data-driven Decorator**
  
Here are some effects of using <code>@unishark.data_driven</code>.  
'Json' style data-driven: 
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
@unishark.data_driven(left=list(range(1, 10)))
@unishark.data_driven(right=list(range(1, 10)))
def test_data_driven(self, **param):
    l = param['left']
    r = param['right']
    print(str(l) + ' x ' + str(r) + ' = ' + str(l * r))
```

Results:
```
1 x 1 = 1
1 x 2 = 2
...
2 x 1 = 2
2 x 2 = 4
...
...
9 x 8 = 72
9 x 9 = 81
```
  
For more examples, please see <code>tests/test_decorator.py</code> and <code>example/</code>.

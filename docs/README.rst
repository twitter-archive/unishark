INTRODUCTION
============

unishark extends unittest (to be accurate, unittest2) in the
following ways:

-  Customizing test suites with dictionary config (or yaml/json like config).
-  Running the tests concurrently at different levels.
-  Generating polished test reports in HTML/XUnit formats.
-  Offering data-driven decorator to accelerate tests writing.

For existing unittests, the first three features could be gained immediately with a single config, without changing any test code.

The Test Config
---------------

Here is an example config in YAML format (you could also write it
directly in a dict()):

.. code:: yaml

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

It configures 3 test suites with some of the test cases excluded, and running the defined set of tests concurrently (multi-threads), and generating both HTML and XUnit (default JUnit) format reports at the end of tests.

NOTE: For versions below 0.3.0, 'max_workers' was set directly under 'test', and 'max_workers' and 'concurrency_level' were set directly under '<suite name>'. For versions since 0.3.0, there is 'concurrency' sub-dict.

To run it, simply add the following code:

.. code:: python

    import unishark
    import yaml

    if __name__ == '__main__':
        with open('your_yaml_config_file', 'r') as f:
            dict_conf = yaml.load(f.read())  # use a 3rd party yaml parser, e.g., PyYAML
            program = unishark.DefaultTestProgram(dict_conf)
            unishark.main(program)

A HTML report example can be found Here_.

.. _Here: https://github.com/twitter/unishark

Data Driven
-----------

Here are some effects of using @unishark.data\_driven.

‘Json’ style data-driven:

.. code:: python

    @unishark.data_driven(*[{'userid': 1, 'passwd': 'abc'}, {'userid': 2, 'passwd': 'def'}])
    def test_data_driven(self, **param):
        print('userid: %d, passwd: %s' % (param['userid'], param['passwd']))

Results:

::

    userid: 1, passwd: abc
    userid: 2, passwd: def

‘Args’ style data-driven:

.. code:: python

    @unishark.data_driven(userid=[1, 2, 3, 4], passwd=['a', 'b', 'c', 'd'])
    def test_data_driven(self, **param):
        print('userid: %d, passwd: %s' % (param['userid'], param['passwd']))

Results:

::

    userid: 1, passwd: a
    userid: 2, passwd: b
    userid: 3, passwd: c
    userid: 4, passwd: d

Cross-multiply data-driven:

.. code:: python

    @unishark.data_driven(left=list(range(10)))
    @unishark.data_driven(right=list(range(10)))
    def test_data_driven(self, **param):
        l = param['left']
        r = param['right']
        print('%d x %d = %d' % (l, r, l * r))

Results:

::

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

You can get the permutations (with repetition) of the parameters values
by doing:

.. code:: python

    @unishark.data_driven(...)
    @unishark.data_driven(...)
    @unishark.data_driven(...)
    ...

Multi-threads data-driven in 'json style':

.. code:: python

    @unishark.multi_threading_data_driven(2, *[{'userid': 1, 'passwd': 'abc'}, {'userid': 2, 'passwd': 'def'}])
    def test_data_driven(self, **param):
        print('userid: %d, passwd: %s' % (param['userid'], param['passwd']))

Results: same results as using unishark.data_driven, but up to 2 threads are spawned, each running the test with a set of inputs (userid, passwd).

Multi-threads data-driven in 'args style':

.. code:: python

    @unishark.multi_threading_data_driven(5, time=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    def test_data_driven(self, **param):
        sleep(param['time'])

Results: 5 threads are spawned to run the test with 10 sets of inputs concurrently (only sleep 1 sec in each thread).
It takes about 2 sec in total (10 sec if using unishark.data_driven) to run.

For more information please visit the Project_Home_ and read README.md.

.. _Project_Home: https://github.com/twitter/unishark

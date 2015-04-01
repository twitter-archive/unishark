This directory contains examples of how to use unishark.
The examples include both passed and failed tests.

To run the example:
1. pip install Jinja2 unishark. (if python2, also install 'futures')
2. cd /your/path/to/unishark/example
3. python run_tests.py (by default it runs with complete-tests.yaml)
4. use 'python run_tests.py -t incomplete-tests.yaml' to run a specific test.

Note that the tests set defined in incomplete-tests.yaml is a subset of complete-tests.yaml.
However running with complete-tests.yaml is faster because it runs concurrently.

Use 'run_tests.py' to run a defined set of tests across several modules
or run any of the individual 'test_module*.py'.
Note that some tests in test_module2.py are expected to fail.


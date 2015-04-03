To run the example:
1. pip install Jinja2 unishark. (if python2, also install 'futures')
2. cd /your/path/to/unishark/example
3. python run_tests.py (by default it runs with config complete-tests.yaml)
4. use 'python run_tests.py -t incomplete-tests.yaml' to run with a specific test config.

The tests set defined in incomplete-tests.yaml is a subset of complete-tests.yaml.
However running with complete-tests.yaml is faster because it enables concurrent running.

Also 'python test_module*.py' to run any of the individual module.
Note that some tests in test_module2.py are expected to fail.

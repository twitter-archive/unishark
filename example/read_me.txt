To run the example:
1. pip install unishark, or no need to install if you have the entire repo cloned.
2. cd /path/to/unishark/example
3. python run_tests.py (by default it runs with config/complete-tests.yaml)
4. use 'python run_tests.py -t config/xxx-tests.yaml' to run with a specific test profile.

The tests set defined in incomplete-tests.yaml is a subset of complete-tests.yaml.
However running with complete-tests.yaml is faster because it enables concurrency.

Also 'python test_module*.py' to run any of the individual module.
Note that some tests are expected to fail.

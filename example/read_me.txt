This directory contains examples of how to use unishark data driven tests
and configuration files. The tests include examples of assertions and
failing tests.

To run the example:
1. pip install Jinja2 unishark.
2. assume you copied 'example' to /your/dir/, cd /your/dir/example
3. PYTHONPATH=.. python run_tests.py (or export PYTHONPATH=/your/dir, then python run_tests.py)

Use run_tests.py to run a defined set of tests across several classes
or run any of the individual test_module*.py classes. Note that some
tests in test_module2.py are expected to fail.
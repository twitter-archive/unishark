import sys
import os
cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(cur_dir, os.pardir))
from unishark import main, DefaultTestProgram
import yaml
import example.config as config
import argparse


if __name__ == '__main__':
    conf = config.Configuration()
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', '-t',
                        default='complete-tests.yaml',
                        help='test config file that determines which test suites to run',
                        metavar='filename')
    args = parser.parse_args()
    test_conf_file = os.path.join(conf.conf_dir, args.test)
    dict_conf = None
    with open(test_conf_file, 'r') as f:
        dict_conf = yaml.load(f.read())
    program = DefaultTestProgram(dict_conf)
    main(program)
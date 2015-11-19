import sys
from os.path import abspath, dirname, join

rootdir = dirname(dirname(abspath(__file__)))
sys.path.append(rootdir)

from unishark import main, DefaultTestProgram, contexts
import yaml
import example.config as config
import argparse
from os.path import sep


if __name__ == '__main__':
    conf = config.Configuration()
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', '-t',
                        default=sep.join(('config', 'complete-tests.yaml')),
                        help='test config file that determines which test suites to run',
                        metavar='filename')
    args = parser.parse_args()
    test_conf_file = join(conf.cur_dir, args.test)
    print('Set configuration to context "example.config".')
    contexts.set('example.config', conf)
    with open(test_conf_file, 'r') as f:
        dict_conf = yaml.load(f.read())
        program = DefaultTestProgram(dict_conf)
        main(program)
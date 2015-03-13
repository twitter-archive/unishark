__author__ = 'Ying Ni <yni@twitter.com>'

from unishark import main, DefaultTestProgram, XUnitReporter
import yaml
import example.config as config


if __name__ == '__main__':
    config.Configuration()

    tests_file = 'config/incomplete-tests.yaml'
    dict_conf = None
    with open(tests_file, 'rt') as f:
        dict_conf = yaml.load(f.read())
    program = DefaultTestProgram(dict_conf,
                                 description='<Here is customized description>: {\n\tcontent\n}.',
                                 dest='./log')
    program.reporters.append(XUnitReporter(dest=program.dest))
    main(program)
from setuptools import setup, find_packages
from os import path
from sys import version_info

NAME = 'unishark'
VERSION = '0.3.2'

long_description = (
    open(path.join('docs', 'README.rst'), 'r').read() + '\n' +
    open(path.join('docs', 'CHANGELOG.rst'), 'r').read()
)

py3_requires = ['Jinja2', 'MarkupSafe']
py2_requires = ['Jinja2', 'MarkupSafe', 'futures']

requires = None
if version_info[0] >= 3 and version_info[1] >= 2:
    requires = py3_requires
else:
    requires = py2_requires

setup(
    name=NAME,
    version=VERSION,

    description='A test framework extending unittest, providing flexible test suites config, concurrent execution, '
                'Html/XUnit reports, and data driven utility.',
    long_description=long_description,

    url='https://github.com/twitter/unishark',

    author='Ying Ni',
    author_email='niying7@gmail.com',

    license='Apache License, Version 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',

        'License :: OSI Approved :: Apache Software License',

        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: Jython',
    ],

    keywords='test framework, unittest extension, concurrent, data driven',

    # See https://packaging.python.org/en/latest/requirements.html
    install_requires=requires,

    extras_require={
        'test': ['coveralls'],
    },

    packages=find_packages(include=[NAME]),
    include_package_data=True,
    package_data={
        NAME: ['templates/*.html', 'templates/*.xml'],
    },
)

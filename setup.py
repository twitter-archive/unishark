from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
NAME = 'unishark'
VERSION = '0.1.2'

setup(
    name=NAME,
    version=VERSION,

    description='A lightweight unittest extension providing Html/XUnit reports, '
                'test suites config and data driven utility.',
    long_description='''unishark extends unittest (to be more accurate, unittest2) in the following ways:

  - Generating polished test reports in different formats such as HTML, XUnit, etc..
  - Organizing test suites with dictionary config (or yaml/json like config).
  - Offering test utils such as data-driven decorator to accelerate tests writing.

3rd party dependencies: Jinja2, MarkupSafe.
Extending existent unittest code with one or more unishark features is easy.
For more information please see README.md on the project home page on github.''',

    url='https://github.com/twitter/unishark',

    author='Ying Ni',
    author_email='niying7@gmail.com',

    license='Apache License, Version 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',

        'License :: OSI Approved :: Apache Software License',

        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='unittest extension test reports config utility',

    # See https://packaging.python.org/en/latest/requirements.html
    install_requires=['Jinja2>=2.7.2', 'MarkupSafe>=0.23'],

    extras_require={
        'test': ['coveralls'],
    },

    packages=find_packages(include=[NAME]),
    include_package_data=True,
    package_data={
        NAME: ['templates/*.html', 'templates/*.xml'],
    },
)

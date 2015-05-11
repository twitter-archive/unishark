from setuptools import setup, find_packages
from os import path

NAME = 'unishark'
VERSION = '0.2.1'

long_description = (
    open(path.join('docs', 'README.rst'), 'r').read() + '\n' +
    open(path.join('docs', 'CHANGELOG.rst'), 'r').read()
)

setup(
    name=NAME,
    version=VERSION,

    description='A lightweight unittest extension providing test suites config, concurrent tests, Html/XUnit reports, '
                'and data driven utility.',
    long_description=long_description,

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
    install_requires=['Jinja2>=2.7.2', 'MarkupSafe>=0.23', 'futures>=2.2.0'],

    extras_require={
        'test': ['coveralls'],
    },

    packages=find_packages(include=[NAME]),
    include_package_data=True,
    package_data={
        NAME: ['templates/*.html', 'templates/*.xml'],
    },
)

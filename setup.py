#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import os
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import relpath
from os.path import splitext
import sys

from setuptools import find_packages
from setuptools import setup


version = '0.0.1.beta'


#### Small hack to force using a plain version number if the option
#### --plain-version is passed to setup.py

USE_DEFAULT_VERSION = False
try:
    sys.argv.remove('--use-default-version')
    USE_DEFAULT_VERSION = True
except ValueError:
    pass
####


def get_version(default=version, template='{commit}',
                use_default=USE_DEFAULT_VERSION):
    """
    Return a version collected from git. If `use_default` is True,
    always use the default version.
    """
    if use_default:
        return default

    try:
        commit = get_git_version()

        return template.format(**locals())
    except:
        # no git data: use default version
        return default


def get_git_version():
    """
    Return version parts from Git or raise an exception.
    """
    from subprocess import check_output, STDOUT
    cmd = 'git describe --tags --long --dirty --always'
    version = check_output(cmd, stderr=STDOUT).strip()

    return version


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='deltacode',
    version=get_version(),
    license='Apache-2.0',
    description='Delta-related utilities.',
    long_description='Delta-related utilities.',
    author='nexB Inc.',
    author_email='info@nexb.com',
    url='https://github.com/nexb/deltacode',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords=[],
    install_requires=[
        'click',
        'scancode-toolkit',
        'unicodecsv',
    ],

    entry_points={
        'console_scripts': [
            'deltacode=deltacode.cli:cli',
        ],
    },

    extras_require={
        # eg: 'rst': ['docutils>=0.11'],
    }
)

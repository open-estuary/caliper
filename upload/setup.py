#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    import client.common as common
except ImportError:
    import common

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if os.path.isdir('upload'):
    upload_dir = 'upload'
else:
    upload_dir = '.'

def get_packages():
    return ['caliper.upload']


def get_package_dirs():
    return {'caliper.upload': upload_dir}

params = dict(
        name='caliper',
        description='A test suite for automatically running on different\
        devices, and compare the test results',
        package_dir=get_package_dirs(),
        packages=get_packages(),
        url='http://github.com/open-estuary',
        maintainer="open-estuary/caliper",
)

def run():
    setup(**params)

if __name__ == "__main__":
    run()

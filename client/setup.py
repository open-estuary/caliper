#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                      
#    E-mail    :    wu.wu@hisilicon.com 
#    Data      :    2015-08-06 11:42:02
#    Desc      :

import os
import sys
import pdb

try:
    import client.common as common
except ImportError:
    import common

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if os.path.isdir('client'):
    client_dir = 'client'
else:
    client_dir = '.'

def get_packages():
    return ['caliper.client.shared',
            'caliper.client.parser',
            'caliper.client'] 

def get_package_dirs():
    return {'caliper.client': client_dir}

params = dict(
        name='caliper',
        description='A test suite for automatically running on different\
        devices, and compare the test results',
        package_dir=get_package_dirs(),
        packages=get_packages(),
        url='http://github.com/hisilicon/caliper-dev',
        maintainer="hisilicon HTSAT",
)

def run():
    setup(**params)

if __name__=="__main__":
    run()

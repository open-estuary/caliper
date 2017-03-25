#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    import server.common as common
except ImportError:
    import common

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if os.path.isdir('server'):
    server_dir = 'server'
else:
    server_dir = '.'

caliper_dir = os.path.join(server_dir, '..')


def _get_files(path):
    flist = []
    for root, _, files in sorted(os.walk(path)):
        for name in files:
            rel_dir = os.path.relpath(root, caliper_dir)
            fullname = os.path.join(rel_dir, name)
            flist.append(fullname)
    return flist


def _get_data_files(path):
    file_list = []
    fdir = {}
    for root, _, files in sorted(os.walk(path)):
        rel_dir = os.path.relpath(root, caliper_dir)
        fdir[rel_dir] = []
        for name in files:
            fullname = os.path.join(rel_dir, name)
            fdir[rel_dir].append(fullname)
        if fdir[rel_dir]:
            file_list.append(
                    (os.path.join(os.environ['HOME'], 'caliper_output', 'configuration',rel_dir), fdir[rel_dir]))
    return file_list


def get_packages():
    return ['caliper.server.build',
            'caliper.server.compute_model',
            'caliper.server.hosts',
            'caliper.server.parser_process',
            'caliper.server.run',
            'caliper.server',
            'caliper']


def get_package_dirs():
    return {'caliper.server': server_dir, 'caliper': caliper_dir}


def get_filelist():
    pd_filelist = []
    # pd_filelist.extend(_get_files(os.path.join(caliper_dir, 'benchmarks')))
    pd_filelist.extend(_get_files(os.path.join(caliper_dir, 'frontend')))
    return pd_filelist


def get_package_data():
    return {'caliper': get_filelist(), 'caliper.server':
            ['build/build.sh', 'build/building_timing.yaml', ]}


def get_scripts():
    return [os.path.join(caliper_dir, 'caliper'),
            os.path.join(server_dir, 'caliper-prerequisite')]


def get_data_files():
    config_filelist = []
    config_filelist.extend(_get_files(os.path.join(caliper_dir, 'config')))
    test_cfg_lists = []
    test_cfg_lists = _get_data_files(
            os.path.join(caliper_dir, 'test_cases_cfg'))
    return [((os.path.join(os.environ['HOME'], 'caliper_output/configuration/config')), config_filelist)] + test_cfg_lists


params = dict(name='caliper',
              description='A test suite for automatically running on different\
                    devices, and compare the test results',
              package_dir=get_package_dirs(),
              packages=get_packages(),
              data_files=get_data_files(),
              url='http://github.com/open-estuary/caliper',
              maintainer="open-estuary",
              )


def run():
    setup(**params)


if __name__ == "__main__":
    run()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import stat
import shutil
import glob
import sys
from pwd import getpwnam  
import logging
try:
    import caliper.common as common
except ImportError:
    import common

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import client.setup
import server.setup

CURRENT_PATH = os.path.dirname(sys.modules[__name__].__file__)
CALIPER_TMP_DIR = os.path.join(os.environ['HOME'], 'caliper_output')
CALIPER_REPORT_HOME = CALIPER_TMP_DIR
CALIPER_DIR = CURRENT_PATH

FRONT_END_DIR = os.path.join(CALIPER_REPORT_HOME,'frontend')
FRONT_TMP_DIR = os.path.join(CALIPER_DIR, 'frontend')
HTML_DATA_DIR = os.path.join(FRONT_END_DIR, 'frontend', 'data_files')

DATA_DIR_INPUT = os.path.join(HTML_DATA_DIR, 'Input_Logs')
HTML_DATA_DIR_INPUT = os.path.join(DATA_DIR_INPUT, 'Input_Report')
OPENSSL_DATA_DIR_INPUT = os.path.join(DATA_DIR_INPUT,'Input_Openssl')
COV_DATA_DIR_INPUT = os.path.join(DATA_DIR_INPUT,'Input_Cov')
CONSOLIDATED_DATA_DIR_INPUT = os.path.join(DATA_DIR_INPUT,'Input_Consolidated')
HW_DATA_DIR_INPUT = os.path.join(DATA_DIR_INPUT,'Input_Hardware')
HW_DATA_DIR_OUTPUT = os.path.join(FRONT_END_DIR, 'polls', 'static', 'TargetInfo')
HTML_DATA_DIR_OUTPUT = os.path.join(HTML_DATA_DIR, 'Normalised_Logs')
COV_DATA_DIR_OUTPUT = os.path.join(FRONT_END_DIR, 'polls', 'static', 'TestInfo','Iterations')
EXCEL_DATA_DIR_OUTPUT = os.path.join(FRONT_END_DIR, 'polls', 'static', 'TestInfo','Report-Data')
TEMPLATE_DATA_DIR = os.path.join(FRONT_END_DIR,'polls','templates','polls')

HTML_PICTURE_DIR = os.path.join(FRONT_END_DIR, 'polls', 'static', 'polls',
                                'pictures')

def create_folder(folder, mode=0755):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    try:
        os.mkdir(folder, mode)
    except OSError:
        os.makedirs(folder, mode)

def create_dir():
    if not os.path.exists(FRONT_END_DIR):
        shutil.copytree(FRONT_TMP_DIR,
                        FRONT_END_DIR)
    if not os.path.exists(HTML_DATA_DIR_INPUT):
        create_folder(HTML_DATA_DIR_INPUT)
    if not os.path.exists(HTML_DATA_DIR_OUTPUT):
        create_folder(HTML_DATA_DIR_OUTPUT)

    if not os.path.exists(DATA_DIR_INPUT):
        create_folder(DATA_DIR_INPUT)
    if not os.path.exists(OPENSSL_DATA_DIR_INPUT):
        create_folder(OPENSSL_DATA_DIR_INPUT)
    if not os.path.exists(COV_DATA_DIR_INPUT):
        create_folder(COV_DATA_DIR_INPUT)

    # Reverte the code as before
    for i in range(1,6):
        if not os.path.exists(os.path.join(COV_DATA_DIR_INPUT,str(i))):
            create_folder(os.path.join(COV_DATA_DIR_INPUT,str(i)))

    if not os.path.exists(CONSOLIDATED_DATA_DIR_INPUT):
        create_folder(CONSOLIDATED_DATA_DIR_INPUT)
    if not os.path.exists(HW_DATA_DIR_INPUT):
        create_folder(HW_DATA_DIR_INPUT)
    if not os.path.exists(HTML_DATA_DIR):
        create_folder(HTML_DATA_DIR)
    if not os.path.exists(COV_DATA_DIR_OUTPUT):
        create_folder(COV_DATA_DIR_OUTPUT)
    if not os.path.exists(EXCEL_DATA_DIR_OUTPUT):
        create_folder(EXCEL_DATA_DIR_OUTPUT)
    if not os.path.exists(TEMPLATE_DATA_DIR):
        create_folder(TEMPLATE_DATA_DIR)

def _combine_dicts(list_dicts):
    result_dict = {}
    for d in list_dicts:
        for k in d:
            result_dict[k] = d[k]
    return result_dict


def get_packages():
    return (client.setup.get_packages() + server.setup.get_packages())


def get_package_dirs():
    return _combine_dicts(
            [client.setup.get_package_dirs(),
            server.setup.get_package_dirs()]
            )


def recursive_file_permissions(path, mode, uid=-1, gid=-1):
    '''
    Recursively updates file permissions on a given path.
    UID and GID default to -1, and mode is required
    '''
    for item in glob.glob(path + '/*'):
        if os.path.isdir(item):
	    os.chown(item, uid, gid)
            recursive_file_permissions(os.path.join(path, item), mode, uid, gid)
        else:
            try:
                os.chown(os.path.join(path, item), uid, gid)
                os.chmod(os.path.join(path, item), mode)
            except:
                print('File permissions on {0} not updated due to error.'.format(os.path.join(path, item)))

def run():
    caliper_data_dir = os.path.join(os.environ['HOME'], '.caliper')
    caliper_tmp_dir = os.path.join(caliper_data_dir, 'benchmarks')
    caliper_output = os.path.join(os.environ['HOME'], 'caliper_output')
    caliper_configuration = os.path.join(caliper_output,'configuration')
    caliper_config_file = os.path.join(caliper_configuration,'config')
    caliper_test_def = os.path.join(caliper_configuration,'test_cases_def')
    if os.path.exists(caliper_tmp_dir):
        shutil.rmtree(caliper_tmp_dir)

    shutil.copytree(
            os.path.join(os.getcwd(), 'benchmarks'),
            caliper_tmp_dir
            )
    shutil.copystat(
            os.path.join(os.getcwd(), 'benchmarks'),
            caliper_tmp_dir
    )
    os.chmod(caliper_data_dir, stat.S_IRWXO + stat.S_IRWXU)
    setup(
            name='caliper',
            description='A test suite for automatically running on different\
                devices, and compare the test results',
            package_dir=get_package_dirs(),
            package_data=server.setup.get_package_data(),
            packages=get_packages(),
            data_files=server.setup.get_data_files(),
            scripts=server.setup.get_scripts(),
            url='http://github.com/open-estuary/caliper',
            maintainer="open-estuary",
            install_requires=[
                'pyYAML',
                'django >= 1.6.1', ]
            )
    create_dir()
    os.chown(caliper_output,getpwnam(os.environ['HOME'].split('/')[-1]).pw_uid,-1)
    recursive_file_permissions(path=caliper_output,mode=0775,uid=getpwnam(os.environ['HOME'].split('/')[-1]).pw_uid,gid=-1)

    if os.path.exists('caliper.egg-info'):
        shutil.rmtree('caliper.egg-info')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    get_packages()

if __name__ == "__main__":
    run()

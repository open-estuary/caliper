#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                      
#    E-mail    :    wu.wu@hisilicon.com 
#    Data      :    2015-04-18 13:54:37
#    Desc      :

import re
import os
import sys
import subprocess

def judge_caliper_installed():
    try:
        output = subprocess.Popen('which caliper', shell=True,
                stdout=subprocess.PIPE)
    except Exception:
        return 0
    else:
        if output.stdout.readlines():
            return 1
        else:
            return 0
CURRENT_PATH = os.path.dirname(sys.modules[__name__].__file__)
CALIPER_DIR = os.path.abspath(os.path.join(CURRENT_PATH, '..', '..'))
PARSER_DIR = os.path.abspath(os.path.join(CALIPER_DIR, 'client', 'parser'))
FRONT_TMP_DIR = os.path.join(CALIPER_DIR, 'frontend')

if judge_caliper_installed():
    CALIPER_TMP_DIR = os.path.join(os.environ['HOME'], 'caliper_workspace')
    if not os.path.exists(CALIPER_TMP_DIR):
        os.mkdir(CALIPER_TMP_DIR)

if not judge_caliper_installed():
    TESTS_CFG_DIR = os.path.join(CALIPER_DIR, 'test_cases_cfg')
    CALIPER_PRE = CALIPER_DIR
    CONFIG_DIR = os.path.join(CALIPER_DIR, 'config')
else:
    TESTS_CFG_DIR = os.path.join('/etc', 'caliper', 'test_cases_cfg')
    CALIPER_PRE = CALIPER_TMP_DIR
    CONFIG_DIR = os.path.join('/etc','caliper', 'config')

BUILD_FILE = 'build.sh'
BENCHS_DIR = os.path.join(CALIPER_DIR, 'benchmarks')
SOURCE_BUILD_FILE = os.path.join(CALIPER_DIR, 'server', 'build', 'build.sh')
TMP_DIR = os.path.join('/tmp', 'caliper.tmp')
GEN_DIR = os.path.join(CALIPER_PRE, 'binary')

FRONT_END_DIR = os.path.join(CALIPER_PRE, 'frontend')
HTML_DATA_DIR = os.path.join(FRONT_END_DIR, 'frontend', 'data_files')
HTML_PICTURE_DIR = os.path.join(FRONT_END_DIR, 'polls', 'static', 'polls', 'pictures')

def get_caliper_num():
    number = 0
    files = os.listdir(CALIPER_PRE)
    for name in files:
        if re.search('output', name) and re.search('\d+', name):
            num_tmp = re.search('(\d+)', name).group(1)
            if num_tmp > number:
                number = num_tmp
    if number:
        return int(number)+1
    else:
        return int(number)

class Singleton(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._inst

class Folder(Singleton):
    name = ''
    build_dir = ''
    exec_dir = ''
    results_dir = ''
    caliper_log_file = ''
    summary_file = ''
    yaml_dir = ''
    html_dir= ''

    def __init__(self, folder=""):
        if folder:
            self.name = folder
        if not folder:
            self.name = '_'.join(['output', str(get_caliper_num())])
        self.name = os.path.join(CALIPER_PRE, self.name) 

    def set_up_path(self):
        self.build_dir = os.path.join(CALIPER_PRE, self.name, 'caliper_build')
        self.exec_dir = os.path.join(CALIPER_PRE, self.name, 'caliper_exec')
        self.results_dir = os.path.join(CALIPER_PRE, self.name, 'results')
        self.caliper_log_file = os.path.join(CALIPER_PRE, self.name, 'caliper_exe.log')
        self.summary_file = os.path.join(CALIPER_PRE, self.name, 'results_summary.log')
        self.yaml_dir = os.path.join(self.results_dir, 'yaml')
        self.html_dir = os.path.join(self.results_dir, 'html')

folder_ope = Folder()
folder_ope.set_up_path()

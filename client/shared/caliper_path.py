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

intermediate = 0

if not judge_caliper_installed():
    # This means caliper is not installed and execution will be local.
    # Output folders are created with in the local directory structure.
    # This will allow multi instance of caliper to execute.
    # fixme CALIPER_REPORT_HOME ??? replace it with CALIPER_REPORT_HOME
    CALIPER_REPORT_HOME = os.path.join(CALIPER_DIR, 'caliper_output')
    if not os.path.exists(CALIPER_REPORT_HOME):
        os.mkdir(CALIPER_REPORT_HOME)
    BENCHS_DIR = os.path.join(CALIPER_DIR, 'benchmarks')
else:
    # This means that the caliper is already installed. Only instance can
    # execute as the updatation of the results will happen under
    # ~/home/user/caliper_workspace
    CALIPER_TMP_DIR = os.path.join(os.environ['HOME'], 'caliper_output')
    if not os.path.exists(CALIPER_TMP_DIR):
        os.mkdir(CALIPER_TMP_DIR)
    CALIPER_REPORT_HOME = CALIPER_TMP_DIR
    BENCHS_DIR = os.path.join(os.environ['HOME'], '.caliper', 'benchmarks')

BUILD_FILE = 'build.sh'
SOURCE_BUILD_FILE = os.path.join(CALIPER_DIR, 'server', 'build', 'build.sh')
TMP_DIR = os.path.join('/tmp', 'caliper.tmp')
GEN_DIR = os.path.join(CALIPER_REPORT_HOME, 'binary')

FRONT_END_DIR = os.path.join(CALIPER_REPORT_HOME, 'frontend')
HTML_DATA_DIR = os.path.join(FRONT_END_DIR, 'frontend', 'data_files')
HTML_DATA_DIR_INPUT = os.path.join(HTML_DATA_DIR, 'Input_Logs')
HTML_DATA_DIR_OUTPUT = os.path.join(HTML_DATA_DIR, 'Normalised_Logs')
HTML_PICTURE_DIR = os.path.join(FRONT_END_DIR, 'polls', 'static', 'polls',
                                'pictures')


def get_caliper_num():
    number = 0
    files = os.listdir(CALIPER_REPORT_HOME)
    for name in files:
        if re.search('^output_\d+$', name):
            num_tmp = int(re.search('_(\d+)$', name).group(1))
            if num_tmp >= number:
                number = num_tmp + 1
    return number


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
    html_dir = ''

    def __init__(self, folder=""):
        if folder:
            self.name = folder
        if not folder:
            self.name = '_'.join(['output', str(get_caliper_num())])
        self.name = os.path.join(CALIPER_REPORT_HOME, self.name)

    def set_up_path(self):
        self.build_dir = os.path.join(CALIPER_REPORT_HOME, self.name,
                                            'caliper_build')
        self.exec_dir = os.path.join(CALIPER_REPORT_HOME, self.name,
                                            'caliper_exec')
        self.results_dir = os.path.join(CALIPER_REPORT_HOME, self.name,
                                            'results')
        self.caliper_log_file = os.path.join(CALIPER_REPORT_HOME, self.name,
                                            'caliper_exe.log')
        self.summary_file = os.path.join(CALIPER_REPORT_HOME, self.name,
                                            'results_summary.log')
        self.final_parser = os.path.join(CALIPER_REPORT_HOME, self.name,'final_parsing_logs.yaml')
        self.yaml_dir = os.path.join(self.results_dir, 'yaml')
        self.html_dir = os.path.join(self.results_dir, 'html')
        self.name = os.path.join(CALIPER_REPORT_HOME, self.name)

folder_ope = Folder()
folder_ope.set_up_path()


class ConfigFile(Singleton):
    tests_cfg_dir = ''
    config_dir = ''
    name = ''

    def __init__(self, folder=""):
        if folder:
            self.name = os.path.abspath(folder)
        else:
            if judge_caliper_installed():
                self.name = os.path.join('/etc', 'caliper')
            else:
                self.name = CALIPER_DIR

    def setup_path(self):
        self.tests_cfg_dir = os.path.join(self.name, 'test_cases_cfg')
        self.config_dir = os.path.join(self.name, 'config')

config_files = ConfigFile()
config_files.setup_path()

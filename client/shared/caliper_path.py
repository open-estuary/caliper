#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import subprocess
import datetime
import shutil
import ConfigParser
import logging


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
SERVER_SYNC_FILE_SRC=os.path.join(CALIPER_DIR,'client','server.py')


caliper_output = os.path.join(os.environ['HOME'], 'caliper_output', 'configuration')
caliper_config_file = os.path.join(caliper_output,'config')
caliper_test_def = os.path.join(caliper_output,'test_cases_cfg')
TIMP_STAMP = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")



# FETCHING THE TARGET HOST NAME AND ARCH FOR CREATING THE WORKSPACE
def ConfigValue(path=None,section=None,key=None,action='get',value=None):
    config = ConfigParser.ConfigParser()
    config.read(path)
    if action == 'get':
        return config.get(section, key)
    else:
        return config.set(section,key,value)

client_ip = ConfigValue(path=os.path.join(caliper_output,'config','client_config.cfg'), section='TARGET', key='ip',action='get')
client_user = ConfigValue(path=os.path.join(caliper_output,'config','client_config.cfg'), section='TARGET', key='user',action='get')
platForm_name = ConfigValue(path=os.path.join(caliper_output,'config','client_config.cfg'), section='TARGET', key='Platform_name',action='get')

if not platForm_name:
    # Redirecting the ssh warning to the standard "stderr" File
    try:
        hostName = subprocess.Popen('ssh '+str(client_user)+"@"+str(client_ip)+" 'hostname'", shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        hostName = hostName.communicate()
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    WORKSPACE = os.path.join(os.environ['HOME'],'caliper_output', str(hostName[0].strip()) + '_WS_'+ TIMP_STAMP)
else:
    WORKSPACE = os.path.join(os.environ['HOME'], 'caliper_output',
                             str(platForm_name) + '_WS_' + TIMP_STAMP)
intermediate = 0

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


if not judge_caliper_installed():
    # This means caliper is not installed and execution will be local.
    # Output folders are created with in the local directory structure.
    # This will allow multi instance of caliper to execute.
    # fixme CALIPER_REPORT_HOME ??? replace it with CALIPER_REPORT_HOME
    CALIPER_REPORT_HOME = os.path.join(CALIPER_DIR, 'caliper_output')
    BENCHS_DIR = os.path.join(CALIPER_DIR, 'benchmarks')
else:
    # This means that the caliper is already installed. Only instance can
    # execute as the updatation of the results will happen under
    # ~/home/user/caliper_workspace
    CALIPER_TMP_DIR = os.path.join(os.environ['HOME'], 'caliper_output')
    CALIPER_REPORT_HOME = CALIPER_TMP_DIR
    BENCHS_DIR = os.path.join(os.environ['HOME'], '.caliper', 'benchmarks')

BUILD_FILE = 'build.sh'
BUILD_TIME = os.path.join(CALIPER_DIR,"server","build","building_timing.yaml")
SOURCE_BUILD_FILE = os.path.join(CALIPER_DIR, 'server', 'build', 'build.sh')
TMP_DIR = os.path.join('/tmp', 'caliper.tmp'+ "_" + TIMP_STAMP)
GEN_DIR = os.path.join(CALIPER_REPORT_HOME, 'binary')
BUILD_LOGS = os.path.join(os.environ['HOME'],'.caliper_build_logs')
FRONT_END_DIR = os.path.join(CALIPER_REPORT_HOME,'frontend')
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
    workspace = ''
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
            self.workspace = folder
        if not folder:
            self.workspace = WORKSPACE
        self.name = os.path.join('output')

    def set_up_path(self):
        self.workspace = os.path.join(os.path.join(os.environ['HOME'], 'caliper_output', self.workspace))
        self.name = os.path.join('output')
        self.build_dir = os.path.join(self.workspace, self.name,
                                            'caliper_build')
        self.exec_dir = os.path.join(self.workspace, self.name,
                                            'caliper_exec')
        self.results_dir = os.path.join(self.workspace, self.name,
                                            'results')
        self.caliper_log_file = os.path.join(self.workspace, self.name,
                                            'caliper_exe.log')
        self.summary_file = os.path.join(self.workspace, self.name,
                                            'results_summary.log')
        self.final_parser = os.path.join(self.workspace, self.name,'final_parsing_logs.yaml')
        self.yaml_dir = os.path.join(self.results_dir, 'yaml')
        self.html_dir = os.path.join(self.results_dir, 'html')



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
                self.name = caliper_output
            else:
                self.name = CALIPER_DIR

    def setup_path(self):
        self.tests_cfg_dir = os.path.join(self.name, 'test_cases_cfg')
        self.config_dir = os.path.join(self.name, 'config')

config_files = ConfigFile()
config_files.setup_path()

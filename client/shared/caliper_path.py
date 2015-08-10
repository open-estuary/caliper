#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                      
#    E-mail    :    wu.wu@hisilicon.com 
#    Data      :    2015-04-18 13:54:37
#    Desc      :

import os
import sys
import subprocess

def judge_caliper_installed():
    try:
        output = subprocess.Popen("which caliper", shell=True,
                stdout=subprocess.PIPE)
    except Exception:
        return 0
    else:
        if output.stdout.readlines():
            return 1
        else:
            return 0

CURRENT_PATH = os.path.dirname(sys.modules[__name__].__file__)
CALIPER_DIR = os.path.abspath(os.path.join(CURRENT_PATH, "..", ".."))
PARSER_DIR = os.path.abspath(os.path.join(CALIPER_DIR, 'client', 'parser'))
FRONT_TMP_DIR = os.path.join(CALIPER_DIR, 'frontend')
CALIPER_TMP_DIR = os.path.join(os.environ['HOME'], '.caliper')
if not os.path.exists(CALIPER_TMP_DIR):
    os.mkdir(CALIPER_TMP_DIR)

if not judge_caliper_installed():
    TESTS_CFG_DIR = os.path.join(CALIPER_DIR, "test_cases_cfg")
    GEN_DIR = os.path.join(CALIPER_DIR, "binary")
    BUILD_LOG_DIR = os.path.join(CALIPER_DIR, "caliper_build")
    EXEC_LOG_DIR = os.path.join(CALIPER_DIR, "caliper_exec")
    RESULTS_DIR = os.path.join(CALIPER_DIR, "results")
    CALIPER_LOG_FILE = os.path.join(CALIPER_DIR, "caliper_exe.log")
    CALIPER_SUMMARY_FILE = os.path.join(CALIPER_DIR, "results_summary.log")
    FRONT_END_DIR = os.path.join(CALIPER_DIR, 'frontend')
    CONFIG_DIR = os.path.join(CALIPER_DIR, 'config')
else:
    TESTS_CFG_DIR = os.path.join('/etc', 'caliper', 'test_cases_cfg')
    GEN_DIR = os.path.join(CALIPER_TMP_DIR, "binary")
    BUILD_LOG_DIR = os.path.join(CALIPER_TMP_DIR, "caliper_build")
    EXEC_LOG_DIR = os.path.join(CALIPER_TMP_DIR, "caliper_exec")
    RESULTS_DIR = os.path.join(CALIPER_TMP_DIR, "results")
    CALIPER_LOG_FILE = os.path.join(CALIPER_TMP_DIR, "caliper_exe.log")
    CALIPER_SUMMARY_FILE = os.path.join(CALIPER_TMP_DIR, "results_summary.log")
    FRONT_END_DIR = os.path.join(CALIPER_TMP_DIR, 'frontend')
    CONFIG_DIR = os.path.join('/etc','caliper', 'config')

BUILD_FILE = "build.sh"
BENCHS_DIR = os.path.join(CALIPER_DIR, "benchmarks")
SOURCE_BUILD_FILE = os.path.join(CALIPER_DIR, 'server', 'build', 'build.sh')
YAML_DIR = os.path.join(RESULTS_DIR, "yaml")
HTML_DIR = os.path.join(RESULTS_DIR, "html")
TMP_DIR = os.path.join("/tmp", "caliper.tmp")
HTML_DATA_DIR = os.path.join(FRONT_END_DIR, "frontend", "data_files")
HTML_PICTURE_DIR = os.path.join(FRONT_END_DIR, "polls", "static", "polls", "pictures")

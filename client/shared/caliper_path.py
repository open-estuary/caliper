#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                      
#    E-mail    :    wu.wu@hisilicon.com 
#    Data      :    2015-04-18 13:54:37
#    Desc      :

import os
import sys

CURRENT_PATH = os.path.dirname(sys.modules[__name__].__file__)
CALIPER_DIR = os.path.abspath(os.path.join(CURRENT_PATH, "..", ".."))
GEN_DIR = os.path.join(CALIPER_DIR, "binary")
TESTS_CFG_DIR = os.path.join(CALIPER_DIR, "test_cases_cfg")
BUILD_FILE = "build.sh"
BENCHS_DIR = os.path.join(CALIPER_DIR, "benchmarks")
SOURCE_BUILD_FILE = os.path.join(CALIPER_DIR, 'server', 'build', 'build.sh')
BUILD_LOG_DIR = os.path.join(CALIPER_DIR, "caliper_build")
EXEC_LOG_DIR = os.path.join(CALIPER_DIR, "caliper_exec")
RESULTS_DIR = os.path.join(CALIPER_DIR, "results")
CONFIG_DIR = os.path.join(CALIPER_DIR, "config")
YAML_DIR = os.path.join(RESULTS_DIR, "yaml")
HTML_DIR = os.path.join(RESULTS_DIR, "html")
YAML_OUTPUT_DIR = os.path.join(CALIPER_DIR, "server", "parser_process", "show_output", "output")
CALIPER_LOG_FILE = os.path.join(CALIPER_DIR, "caliper_exe.log")
CALIPER_SUMMARY_FILE = os.path.join(CALIPER_DIR, "results_summary.log")
TMP_DIR = os.path.join("/tmp", "caliper.tmp")

HTML_DATA_DIR = os.path.join(CALIPER_DIR, "frontend", "frontend", "data_files")
HTML_PICTURE_DIR = os.path.join(CALIPER_DIR, "frontend", "polls", "static", "polls", "pictures") 

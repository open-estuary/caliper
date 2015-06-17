#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   wuyanjun 00291783
#   E-mail  :   wu.wu@hisilicon.com
#   Date    :   15/01/21 19:41:34
#   Desc    :  
#

import os
import sys
import re
import shutil
import stat
import logging
import pdb
import subprocess

import parser_yaml_result as deal_result
from caliper.client.shared import caliper_path

LOCATION = os.path.dirname(sys.modules[__name__].__file__)
CALIPER_DIR= caliper_path.CALIPER_DIR
OUT_DIR = os.path.join(CALIPER_DIR, 'results')

def get_targets_data(outdir):
    yaml_dir = os.path.join(outdir, 'yaml')
    yaml_files = []
    json_files = []
    for root, dirs, files in os.walk(yaml_dir):
        for i in range(0, len(files)):
            if re.search('_score_post\.yaml', files[i]):
                yaml_name = os.path.join(root, files[i])
                yaml_files.append(yaml_name)
            else:
                if re.search('.json', files[i]):
                    json_name = os.path.join(root, files[i])
                    json_files.append(json_name)
    return (yaml_files, json_files)

def show_caliper_result():
    HTML_DIR = os.path.join(OUT_DIR, 'html')
   
    file_lists = []
    (file_lists, json_lists) = get_targets_data(OUT_DIR)
   
    picture_location = ''
    picture_location = os.path.join(OUT_DIR, 'html')
    try:
        return_code = deal_result.draw_picture(file_lists, picture_location)
    except Exception, e:
        logging.info("There is wrong in drawing pictures")
    if json_lists:
        for json_file in json_lists:
            subprocess.call("mv %s %s" % (json_file, caliper_path.HTML_DATA_DIR),
                        shell=True)
    subprocess.call("cd %s; mv * %s" % (picture_location, caliper_path.HTML_PICTURE_DIR), 
                    shell=True )
